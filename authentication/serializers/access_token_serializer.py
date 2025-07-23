# your_app/serializers/access_token_serializer.py

import logging
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from allauth.socialaccount.models import SocialAccount

logger = logging.getLogger('prod')

class AccessTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        logger.info(f"Generating tokens for user: {user.username}")

        token = super().get_token(user)


        social_account = SocialAccount.objects.filter(user=user).first()
        token['uid'] = getattr(social_account, 'uid', None)

        return token