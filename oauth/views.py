# myapp/views.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from allauth.socialaccount.models import SocialToken, SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings

logger = logging.getLogger('prod')

class SocialOAuthCallbackView(View):
    provider = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_callback_url(self, success=True, error=None):
        base_url = "https://www.textneckhub.p-e.kr/login/callback/"
        if success:
            return f"{base_url}?status=success"
        else:
            return f"{base_url}?status=error&message={error}"

    def get(self, request):
        user = request.user
        logger.info(f"User: {user.username} ({user.id}) attempting social login callback.")
        social_account = SocialAccount.objects.filter(
            user=user, provider=self.provider).first()

        if not social_account:
            logger.error(f"No SocialAccount found for user {user.username} with provider {self.provider}")
            return redirect(self.get_callback_url(success=False, error="NoSocialAccount"))

        logger.info(f"SocialAccount found: {social_account.uid}")
        token = SocialToken.objects.filter(account=social_account).first()

        if token:
            logger.info(f"SocialToken found for {self.provider}. Issuing JWT.")
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response_data = {
                'access': access_token,
                'user_info': {
                    'email': user.email,
                    'name': user.first_name,
                },
                "message": "소셜 로그인 성공! 🤩"
            }
            response = Response(response_data, status=status.HTTP_200_OK)

            refresh_token_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()

            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=settings.DEBUG is False,
                samesite='None',
                max_age=int(refresh_token_lifetime)
            )

            return response

        else:
            logger.error(f"No SocialToken found for SocialAccount {social_account.uid} with provider {self.provider}")
            return redirect(self.get_callback_url(success=False, error=f"No{self.provider.capitalize()}TokenFound"))


class GoogleOAuthCallbackView(SocialOAuthCallbackView):
    provider = "google"


class KakaoOAuthCallbackView(SocialOAuthCallbackView):
    provider = "kakao"


class NaverOAuthCallbackView(SocialOAuthCallbackView):
    provider = "naver"


class GithubOAuthCallbackView(SocialOAuthCallbackView):
    provider = "github"
