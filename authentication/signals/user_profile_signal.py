import requests
from django.core.files import File
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import user_signed_up, user_logged_in
from ..models import UserProfile
from ..serializers.user_profile_serializer import UserProfileSerializer
from ..clients.kafka_client import KafkaClient
from django.conf import settings
import logging

logger = logging.getLogger("prod")

User = get_user_model()


@receiver(user_signed_up)
def populate_user_profile_on_signup(request, user, **kwargs):
    logger.info(
        f"유저 가입 시 프로필 생성 또는 업데이트 시작: 유저 ID {user.id}, 유저명 {user.username}")
    profile, created = UserProfile.objects.get_or_create(user=user)

    if created:
        logger.info(f"새 UserProfile 생성됨: 유저 ID {user.id}")
    else:
        logger.info(f"기존 UserProfile 가져옴: 유저 ID {user.id}")

    profile.name = user.last_name + user.first_name
    profile.email = user.email
    logger.debug(f"초기 프로필 이름: {profile.name}, 이메일: {profile.email}")

    social_login = kwargs.get('sociallogin')
    if social_login:
        logger.info(f"소셜 로그인 정보 감지: 프로필 업데이트 시도")
        extra_data = social_login.account.extra_data

        social_image_url = None
        for profile_image_key in ['picture', 'profile_image', 'image_url']:
            if profile_image_key in extra_data:
                social_image_url = extra_data[profile_image_key]
                logger.debug(f"소셜 프로필 이미지 URL 발견: {social_image_url}")
                break

        if social_image_url:
            logger.info(f"소셜 프로필 이미지 URL 발견: {social_image_url}")
            try:
                response = requests.get(social_image_url, stream=True)
                response.raise_for_status()

                file_name_part = social_image_url.split('/')[-1].split('?')[0]
                file_name = f"{user.id}_{file_name_part}"
                if not '.' in file_name_part:
                    file_name += '.jpg'

                profile.profile_picture.save(file_name, File(response.raw))
                logger.info(f"프로필 이미지 성공적으로 저장됨: {file_name}")
            except requests.exceptions.RequestException as req_e:
                logger.error(f"프로필 이미지 다운로드 실패 (네트워크/HTTP 오류): {req_e}")
            except Exception as e:
                logger.error(f"프로필 이미지 저장 중 예상치 못한 오류 발생: {e}")
        else:
            logger.info("소셜 프로필 이미지 URL 찾을 수 없음.")

        social_name = extra_data.get('name')
        if social_name:
            profile.name = social_name
            logger.debug(f"소셜 이름으로 프로필 이름 업데이트됨: {profile.name}")

        social_email = extra_data.get('email')
        if social_email:
            profile.email = social_email
            logger.debug(f"소셜 이메일로 프로필 이메일 업데이트됨: {profile.email}")

    profile.save()
    serializer = UserProfileSerializer(instance=profile)

    data = serializer.data

    topic = settings.KAFKA_DEFAULT_TOPIC
    key = data.get("user_id")
    headers = {
        "content-type": "application/json",
        "schema": "user-profile-v1",
    }

    KafkaClient.send(topic=topic, key=key, value=data, headers=headers)
    logger.info(f"UserProfile 저장 완료: 유저 ID {user.id}")


# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, created, **kwargs):
#     logger.debug(f"User 모델 저장 시그널 발생: 유저 ID {instance.id}")
#     if created:
#         UserProfile.objects.get_or_create(user=instance)
#     if hasattr(instance, 'profile'):
#         instance.profile.save()
#         logger.debug(f"연결된 UserProfile 저장됨: 유저 ID {instance.id}")
#     else:
#         logger.warning(
#             f"User ID {instance.id} 에 연결된 UserProfile이 없습니다. 초기 UserProfile 생성이 누락되었을 수 있습니다.")
