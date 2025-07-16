
from django.core.cache import cache

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status


from django.core.cache import cache


from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.settings import api_settings
import logging

logger = logging.getLogger('prod')


class RefreshTokenRevokeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        refresh_token_value = request.COOKIES.get('refresh_token')

        if not refresh_token_value:
            return Response(
                {"error": "Refresh token is required for revocation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            token = RefreshToken(refresh_token_value)
            jti = token[api_settings.JTI_CLAIM]

            user_id_from_token = request.user.id

            redis_key = f"refresh_token:{user_id_from_token}:{jti}"

            deleted_count = cache.delete(redis_key)

            if deleted_count == 0:
                logger.warning(
                    f"Attempted to revoke non-existent or already revoked refresh token in Redis for user {user_id_from_token} with JTI {jti}. Key attempted: {redis_key}")
                return Response(
                    {"error": "Refresh token not found or already revoked."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            response = Response(
                {"message": "Refresh token successfully revoked."},
                status=status.HTTP_200_OK
            )
            response.delete_cookie('refresh_token')
            logger.info(
                f"Refresh token revoked for user {user_id_from_token} with JTI {jti} from Redis and cookie. Key: {redis_key}")
            return response

        except Exception as e:
            logger.error(

                f"Error revoking refresh token for user {request.user.id}: {e}", exc_info=True)
            return Response(
                {"error": "An error occurred during token revocation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
