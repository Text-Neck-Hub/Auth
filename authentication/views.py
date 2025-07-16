
from django.core.cache import cache
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
import logging
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.settings import api_settings

logger = logging.getLogger('prod')

User = get_user_model()


logger = logging.getLogger(__name__)


class AccessTokenObtainView(APIView):

    permission_classes = [permissions.AllowAny]
    provider = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        user = request.user
        logger.info(
            f"User: {user.username} ({user.id}) attempting social login token obtain for provider {self.provider}.")

        social_account = SocialAccount.objects.filter(
            user=user, provider=self.provider).first()

        if not social_account:
            logger.error(
                f"No SocialAccount found for user {user.username} with provider {self.provider}")
            return Response(
                {"error": f"No SocialAccount found for {self.provider}. Please link your account first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"SocialAccount found: {social_account.uid}. Issuing JWT.")

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response_data = {
            'access': access_token,
            'user_info': {
                'email': user.email,
                'name': user.first_name,
            },
            "message": "Social login successful! JWTs issued."
        }

        logger.info(
            f"🎄Final response_data before sending🎆: Access token issued (starts with {access_token[:10]})...")
        logger.info(
            f"JWTs issued for user {user.username} ({user.id}). Access token: {access_token[:10]}... Refresh token: {refresh_token[:10]}...")
        response = Response(response_data, status=status.HTTP_200_OK)

        ttl_seconds = int(
            settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())

        try:

            jti = refresh['jti']
        except KeyError:
            logger.error(
                f"JTI claim not found in refresh token for user {user.id}.")
            return Response({"error": "Failed to process token (JTI missing)."}, status=status.HTTP_500_INTERNAL_ERROR)

        key = f"refresh_token:{user.id}:{jti}"

        cache.set(key, refresh_token, timeout=ttl_seconds)
        logger.info(
            f"✅ Redis에 사용자 {user.id}의 새 리프레시 토큰 저장 완료! 키: {key}, JTI: {jti}, TTL: {ttl_seconds}초")

        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=settings.DEBUG is False,
            samesite='Lax',
            max_age=ttl_seconds
        )

        return response


class GoogleAccessTokenObtainView(AccessTokenObtainView):
    provider = "google"


class KakaoAccessTokenObtainView(AccessTokenObtainView):
    provider = "kakao"


class NaverAccessTokenObtainView(AccessTokenObtainView):
    provider = "naver"


class GithubAccessTokenObtainView(AccessTokenObtainView):
    provider = "github"


logger = logging.getLogger(__name__)


class AccessTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token_from_cookie = request.COOKIES.get('refresh_token')

        if refresh_token_from_cookie is None:
            logger.warning(
                "Refresh token not found in cookies during refresh attempt.")
            return Response(
                {"detail": "Refresh token not found in cookies."},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_refresh_token_jti = None
        user_id = None
        try:
            old_refresh_token_obj = RefreshToken(refresh_token_from_cookie)
            old_refresh_token_jti = old_refresh_token_obj['jti']
            user_id = old_refresh_token_obj.get(
                settings.SIMPLE_JWT['USER_ID_CLAIM'])
        except Exception as e:
            logger.error(
                f"Error extracting JTI or user_id from old refresh token in cookie: {e}")

        mutable_data = request.data.copy()
        mutable_data['refresh'] = refresh_token_from_cookie
        request._data = mutable_data

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            new_access_token = response.data.get('access')

            new_refresh_token = response.data.get('refresh')

            if user_id and old_refresh_token_jti:

                old_redis_key = f"refresh_token:{user_id}:{old_refresh_token_jti}"
                cache.delete(old_redis_key)
                logger.info(f"✅ Redis에서 이전 리프레시 토큰 삭제 완료! 키: {old_redis_key}")
            else:
                logger.warning(
                    "Could not determine user ID or old JTI to delete previous refresh token from Redis.")

            if user_id and new_refresh_token:
                try:
                    new_refresh_token_obj = RefreshToken(new_refresh_token)
                    new_jti = new_refresh_token_obj['jti']
                except Exception as e:
                    logger.error(
                        f"Error extracting JTI from new refresh token: {e}")

                    logger.warning(
                        "Failed to process new refresh token for Redis/cookie update. User might need to re-login.")
                    return response

                ttl_seconds = int(
                    settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())

                new_redis_key = f"refresh_token:{user_id}:{new_jti}"
                cache.set(new_redis_key, new_refresh_token,
                          timeout=ttl_seconds)
                logger.info(
                    f"✅ Redis에 사용자 {user_id}의 새 리프레시 토큰 저장 완료! 키: {new_redis_key}, JTI: {new_jti}")

                response.set_cookie(
                    key='refresh_token',
                    value=new_refresh_token,
                    httponly=True,
                    secure=settings.DEBUG is False,
                    samesite='Lax',
                    max_age=ttl_seconds
                )
                logger.info(f"✅ 클라이언트 쿠키에 새로운 리프레시 토큰 설정 완료.")
            else:
                logger.warning(
                    "Could not determine user ID or new refresh token for Redis/cookie update.")

        return response


class AccessTokenVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Access token is valid"}, status=status.HTTP_200_OK)


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
