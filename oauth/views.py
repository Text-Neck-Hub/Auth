from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from allauth.socialaccount.models import SocialToken, SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken


class SocialOAuthCallbackView(View):
    provider = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_callback_url(self, success=True, **kwargs):
        base_url = "http://127.0.0.1:3000/login/callback/"
        if success:
            params = f"?access_token={kwargs.get('access_token')}&refresh_token={kwargs.get('refresh_token')}"
        else:
            params = f"?error={kwargs.get('error')}"
        return base_url + params

    def get(self, request):
        user = request.user
        social_account = SocialAccount.objects.filter(
            user=user, provider=self.provider).first()

        if not social_account:
            return redirect(self.get_callback_url(success=False, error="NoSocialAccount"))

        token = SocialToken.objects.filter(account=social_account).first()

        if token:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            return redirect(self.get_callback_url(
                success=True,
                access_token=access_token,
                refresh_token=refresh_token
            ))
        else:
            return redirect(self.get_callback_url(success=False, error=f"No{self.provider.capitalize()}TokenFound"))


class GoogleOAuthCallbackView(SocialOAuthCallbackView):
    provider = "google"


class KakaoOAuthCallbackView(SocialOAuthCallbackView):
    provider = "kakao"


class NaverOAuthCallbackView(SocialOAuthCallbackView):
    provider = "naver"


class GithubOAuthCallbackView(SocialOAuthCallbackView):
    provider = "github"
