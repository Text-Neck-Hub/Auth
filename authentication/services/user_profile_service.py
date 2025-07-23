from ..models import UserProfile
from allauth.socialaccount.models import SocialAccount
import logging

logger = logging.getLogger('prod')


class UserProfileService:
    @staticmethod
    def get_user_profile_data(profile_instance):
        logger.info(
            f"프로필 데이터 조회 서비스 호출됨: 프로필 ID {profile_instance.id}, 유저 ID {profile_instance.user.id}")

        social_account = SocialAccount.objects.filter(
            user=profile_instance.user
        ).first()

        if social_account:
            return social_account.uid
        else:
            logger.warning(
                f"유저 {profile_instance.user.id}에 연결된 소셜 계정을 찾을 수 없습니다. (프로필 ID: {profile_instance.id})"
            )
            return None

    @staticmethod
    def update_user_profile(profile_instance: UserProfile, validated_data: dict):
        logger.info(
            f"프로필 업데이트 서비스 호출됨: 프로필 ID {profile_instance.id}, 유저 ID {profile_instance.user.id}, 데이터: {validated_data}")
        for attr, value in validated_data.items():
            setattr(profile_instance, attr, value)
        profile_instance.save()
        return profile_instance

    @staticmethod
    def delete_user_profile(profile_instance: UserProfile):
        profile_id = profile_instance.id
        user_id = profile_instance.user.id
        profile_instance.delete()
        logger.info(f"프로필 삭제 서비스 호출됨: 프로필 ID {profile_id}, 유저 ID {user_id}")
