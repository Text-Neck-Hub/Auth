from django.urls import path
from . import views

urlpatterns = [
    path('access-token/', views.AccessTokenObtainView.as_view(),
         name='access_token_obtain'),

    path('verify/', views.AccessTokenVerificationView.as_view(),
         name='access_token_verify'),

    path('refresh/', views.AccessTokenRefreshView.as_view(),
         name='access_token_refresh'),

    path('revoke/', views.RefreshTokenRevokeView.as_view(),
         name='refresh_token_revoke'),
]
