from .views import (
    GoogleOAuthCallbackView,
    KakaoOAuthCallbackView,
    NaverOAuthCallbackView,
    GithubOAuthCallbackView,
)
import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import AnonymousUser


User = get_user_model()


@pytest.mark.django_db
class TestSocialOAuthCallbackView:
    def setup_method(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpass")

    @patch("allauth.socialaccount.models.SocialAccount.objects.filter")
    @patch("allauth.socialaccount.models.SocialToken.objects.filter")
    @patch("rest_framework_simplejwt.tokens.RefreshToken.for_user")
    @pytest.mark.parametrize("view_cls,provider", [
        (GoogleOAuthCallbackView, "google"),
        (KakaoOAuthCallbackView, "kakao"),
        (NaverOAuthCallbackView, "naver"),
        (GithubOAuthCallbackView, "github"),
    ])
    def test_success_callback(self, mock_for_user, mock_token_filter, mock_account_filter, view_cls, provider):

        mock_account = MagicMock()
        mock_account_filter.return_value.first.return_value = mock_account
        mock_token = MagicMock()
        mock_token_filter.return_value.first.return_value = mock_token

        mock_refresh = MagicMock()
        mock_refresh.access_token = "access"
        mock_refresh.__str__.return_value = "refresh"
        mock_for_user.return_value = mock_refresh

        request = self.factory.get(f"/v1/callback/{provider}/")
        request.user = self.user

        response = view_cls.as_view()(request)
        assert response.status_code == 302
        assert "access_token=access" in response.url
        assert "refresh_token=refresh" in response.url

    @patch("allauth.socialaccount.models.SocialAccount.objects.filter")
    @pytest.mark.parametrize("view_cls,provider", [
        (GoogleOAuthCallbackView, "google"),
        (KakaoOAuthCallbackView, "kakao"),
        (NaverOAuthCallbackView, "naver"),
        (GithubOAuthCallbackView, "github"),
    ])
    def test_no_social_account(self, mock_account_filter, view_cls, provider):
        mock_account_filter.return_value.first.return_value = None

        request = self.factory.get(f"/v1/callback/{provider}/")
        request.user = self.user

        response = view_cls.as_view()(request)
        assert response.status_code == 302
        assert "error=NoSocialAccount" in response.url

    @patch("allauth.socialaccount.models.SocialAccount.objects.filter")
    @patch("allauth.socialaccount.models.SocialToken.objects.filter")
    @pytest.mark.parametrize("view_cls,provider", [
        (GoogleOAuthCallbackView, "google"),
        (KakaoOAuthCallbackView, "kakao"),
        (NaverOAuthCallbackView, "naver"),
        (GithubOAuthCallbackView, "github"),
    ])
    def test_no_social_token(self, mock_token_filter, mock_account_filter, view_cls, provider):
        mock_account = MagicMock()
        mock_account_filter.return_value.first.return_value = mock_account
        mock_token_filter.return_value.first.return_value = None

        request = self.factory.get(f"/v1/callback/{provider}/")
        request.user = self.user

        response = view_cls.as_view()(request)
        assert response.status_code == 302
        assert f"error=No{provider.capitalize()}TokenFound" in response.url

    @pytest.mark.parametrize("view_cls", [
        GoogleOAuthCallbackView,
        KakaoOAuthCallbackView,
        NaverOAuthCallbackView,
        GithubOAuthCallbackView,
    ])
    def test_login_required(self, view_cls):
        request = self.factory.get("/v1/callback/google/")
        request.user = AnonymousUser()

        response = view_cls.as_view()(request)
        assert response.status_code == 302
        assert "/accounts/login/" in response.url
