

import logging
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


logger = logging.getLogger('prod')


class AccessTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        logger.info(f"Generating tokens for user: {user.username}")

        token = super().get_token(user)

        token['email'] = user.email

        return token
