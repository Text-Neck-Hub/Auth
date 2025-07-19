from django.urls import path
from .. import views


urlpatterns = [

    path('refresh-token/revoke/', views.RefreshTokenRevokeView.as_view(),
         name='refresh_token_revoke'),

]
