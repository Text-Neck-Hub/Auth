from django.urls import path
from . import views


urlpatterns = [
    path('access-token/', views.AccessTokenObtainView.as_view(),
         name='access_token_obtain'),

    path('access-token/refresh/', views.AccessTokenRefreshView.as_view(),
         name='access_token_refresh'),

    path('refresh-token/revoke/', views.RefreshTokenRevokeView.as_view(),
         name='refresh_token_revoke'),

    path(
        'me/', views.UserProfileView.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='user_profile'),
]
