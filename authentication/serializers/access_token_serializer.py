

import logging
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from allauth.socialaccount.models import SocialAccount

logger = logging.getLogger('prod')


class AccessTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        logger.info(f"Generating tokens for user: {user.username}")

        token = super().get_token(user)

        providers = {'kakao': 'kakao', 'naver': 'naver', 'gmail': 'google'}
        logger.info(f"소셜 로그인 사용자 {user}의 JWT 발급 시작.")
        logger.info(
            f"소셜 로그인 사용자 {user} ({user.email.split('@')[1].split('.')[0]})의 JWT 발급 시작.")
        provider = providers.get(user.email.split('@')[1].split('.')[0], None)
        logger.info(f"소셜 로그인 제공자: {provider}")
        social_account = SocialAccount.objects.filter(
            user=user, provider=provider).first()
        token['uid'] = getattr(social_account, 'uid', None)

        return token
