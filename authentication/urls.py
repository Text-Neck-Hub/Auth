from django.urls import path
from . import views

urlpatterns = [
    path('access-token/', views.GoogleAccessTokenObtainView.as_view(),
         name='access_token_obtain'),

    path('access-token/verify/', views.AccessTokenVerificationView.as_view(),
         name='access_token_verify'),

    path('access-token/refresh/', views.AccessTokenRefreshView.as_view(),
         name='access_token_refresh'),

    path('refresh-token/revoke/', views.RefreshTokenRevokeView.as_view(),
         name='refresh_token_revoke'),
]
