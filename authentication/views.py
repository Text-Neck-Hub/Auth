# myapp/views.py
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from allauth.socialaccount.models import SocialToken, SocialAccount

logger = logging.getLogger('prod')

User = get_user_model()


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
        response = Response(response_data, status=status.HTTP_200_OK)

        refresh_token_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(
        )

        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=settings.DEBUG is False,
            samesite='None',
            max_age=int(refresh_token_lifetime)
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


class AccessTokenVerificationView(TokenVerifyView):
    pass


class AccessTokenRefreshView(TokenRefreshView):
    pass


class RefreshTokenRevokeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token_value = request.data.get('refresh_token')

        if not refresh_token_value:
            return Response(
                {"error": "Refresh token is required for revocation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            outstanding_token = OutstandingToken.objects.get(
                token=refresh_token_value)

            if outstanding_token.user != request.user:
                logger.warning(
                    f"Attempted revocation of token not belonging to user {request.user.id}")
                return Response(
                    {"error": "Unauthorized token revocation attempt."},
                    status=status.HTTP_403_FORBIDDEN
                )

            BlacklistedToken.objects.get_or_create(token=outstanding_token)

            logger.info(f"Refresh token revoked for user {request.user.id}.")
            return Response(
                {"message": "Refresh token successfully revoked."},
                status=status.HTTP_200_OK
            )

        except OutstandingToken.DoesNotExist:
            logger.warning(
                f"Attempted to revoke non-existent or already revoked refresh token.")
            return Response(
                {"error": "Refresh token not found or already revoked."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f"Error revoking refresh token for user {request.user.id}: {e}")
            return Response(
                {"error": "An error occurred during token revocation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
