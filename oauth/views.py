from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from allauth.socialaccount.models import SocialToken, SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
import logging
logger = logging.getLogger('prod')

class SocialOAuthCallbackView(View):
    provider = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_callback_url(self, success=True, **kwargs):
        base_url = "https://www.textneckhub.p-e.kr/login/callback/"
        logger.info(f"Redirecting to {base_url} with success={success} and kwargs={kwargs}")
        if success:
            params = f"?access_token={kwargs.get('access_token')}&refresh_token={kwargs.get('refresh_token')}"
        else:
            params = f"?error={kwargs.get('error')}"
        return base_url + params

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
            return redirect(self.get_callback_url(
                success=True,
                access_token=access_token,
                refresh_token=refresh_token
            ))
        else:
            logger.error(f"No SocialToken found for SocialAccount {social_account.uid} with provider {self.provider}")
            return redirect(self.get_callback_url(success=False, error=f"No{self.provider.capitalize()}TokenFound"))


class GoogleOAuthCallbackView(SocialOAuthCallbackView):
    provider = "Google"


class KakaoOAuthCallbackView(SocialOAuthCallbackView):
    provider = "Kakao"


class NaverOAuthCallbackView(SocialOAuthCallbackView):
    provider = "Naver"


class GithubOAuthCallbackView(SocialOAuthCallbackView):
    provider = "Github"
