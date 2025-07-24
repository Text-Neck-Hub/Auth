# from ..models import UserProfile
# from allauth.socialaccount.models import SocialAccount
# import logging

# logger = logging.getLogger('prod')


# class UserProfileService:
#     @staticmethod
#     def get_user_profile_data(profile_instance):
#         logger.info(
#             f"프로필 데이터 조회 서비스 호출됨: 프로필 ID {profile_instance.id}, 유저 ID {profile_instance.user.id}")

#         social_account = SocialAccount.objects.filter(
#             user=profile_instance.user
#         ).first()

#         if social_account:
#             return social_account.uid
#         else:
#             logger.warning(
#                 f"유저 {profile_instance.user.id}에 연결된 소셜 계정을 찾을 수 없습니다. (프로필 ID: {profile_instance.id})"
#             )
#             return None

#     @staticmethod
#     def update_user_profile(profile_instance: UserProfile, validated_data: dict):
#         logger.info(
#             f"프로필 업데이트 서비스 호출됨: 프로필 ID {profile_instance.id}, 유저 ID {profile_instance.user.id}, 데이터: {validated_data}")
#         for attr, value in validated_data.items():
#             setattr(profile_instance, attr, value)
#         profile_instance.save()
#         return profile_instance

#     @staticmethod
#     def delete_user_profile(profile_instance: UserProfile):
#         profile_id = profile_instance.id
#         user_id = profile_instance.user.id
#         profile_instance.delete()
#         logger.info(f"프로필 삭제 서비스 호출됨: 프로필 ID {profile_id}, 유저 ID {user_id}")
import os
import logging
from django.conf import settings
from ..models import UserProfile
from allauth.socialaccount.models import SocialAccount

logger = logging.getLogger('prod')


class UserProfileService:

    @staticmethod
    def get_user_profile_data(profile_instance: UserProfile):
        logger.info(
            f"프로필 데이터 조회 서비스: 프로필 ID={profile_instance.id}, 유저 ID={profile_instance.user.id}"
        )
        social = SocialAccount.objects.filter(user=profile_instance.user).first()
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

        # 새 파일이 업로드됐고, 기존 파일이 있을 경우 시스템에서 삭제
        if new_file and old_file and old_file.name != new_file.name:
            try:
                path = old_file.path
                if os.path.isfile(path):
                    os.remove(path)
                    logger.info(f"기존 프로필 이미지 삭제됨: {path}")
            except Exception as e:
                logger.error(f"기존 이미지 삭제 실패: {e}")

        # 검증된 모든 필드를 인스턴스에 세팅
        for attr, val in validated_data.items():
            setattr(profile_instance, attr, val)

        profile_instance.save()
        return profile_instance

    @staticmethod
    def delete_user_profile(profile_instance: UserProfile) -> None:
        logger.info(
            f"프로필 삭제 서비스 호출: 프로필 ID={profile_instance.id}, 유저 ID={profile_instance.user.id}"
        )
        # 이미지 파일 삭제
        if profile_instance.profile_picture:
            try:
                path = profile_instance.profile_picture.path
                if os.path.isfile(path):
                    os.remove(path)
                    logger.info(f"프로필 이미지 파일 삭제됨: {path}")
            except Exception as e:
                logger.error(f"프로필 이미지 삭제 중 오류: {e}")

        # DB 레코드 삭제
        profile_instance.delete()
        logger.info(f"프로필 레코드 삭제 완료: 프로필 ID={profile_instance.id}")
