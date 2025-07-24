
import os
import logging
from ..models import UserProfile
from allauth.socialaccount.models import SocialAccount

from django.contrib.auth import get_user_model
from django.db import transaction
logger = logging.getLogger('prod')

User = get_user_model()


class UserProfileService:

    @staticmethod
    def get_user_profile_data(profile_instance: UserProfile):
        logger.info(
            f"프로필 데이터 조회 서비스: 프로필 ID={profile_instance.id}, 유저 ID={profile_instance.user.id}"
        )
        social = SocialAccount.objects.filter(
            user=profile_instance.user).first()
        if social:
            return social.uid
        logger.warning(
            f"유저 {profile_instance.user.id}에 연결된 소셜 계정 없음 (프로필 ID={profile_instance.id})"
        )
        return None

    @staticmethod
    def update_user_profile(
        profile_instance: UserProfile,
        validated_data: dict
    ) -> UserProfile:
        logger.info(
            f"프로필 업데이트 서비스: 프로필 ID={profile_instance.id}, 데이터={validated_data}"
        )

        new_file = validated_data.get('profile_picture')
        old_file = profile_instance.profile_picture

        if new_file and old_file and old_file.name != new_file.name:
            try:
                path = old_file.path
                if os.path.isfile(path):
                    os.remove(path)
                    logger.info(f"기존 프로필 이미지 삭제됨: {path}")
            except Exception as e:
                logger.error(f"기존 이미지 삭제 실패: {e}")

        for attr, val in validated_data.items():
            setattr(profile_instance, attr, val)

        profile_instance.save()
        return profile_instance

    @staticmethod
    def delete_user_profile(profile_instance: UserProfile, user_id: int) -> None:
        logger.info(
            f"프로필 삭제 서비스 호출: 프로필 ID={profile_instance.id}, 유저 ID={profile_instance.user.id}"
        )

        with transaction.atomic():

            try:
                path = profile_instance.profile_picture.path
                if os.path.isfile(path):
                    os.remove(path)
                    logger.info(f"프로필 이미지 파일 삭제됨: {path}")
            except Exception as e:
                logger.error(f"프로필 이미지 삭제 중 오류: {e}")

            profile_instance.profile_picture.delete(save=False)
            profile_instance.delete()
            User.objects.filter(id=user_id).delete()

            logger.info(
                f"✅ 프로필/유저 삭제 완료 - 프로필 ID={profile_instance.id}, 유저 ID={user_id}")
