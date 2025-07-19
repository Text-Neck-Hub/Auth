from django.urls import path
from ..views import AccessTokenObtainView, AccessTokenRefreshView


urlpatterns = [
    path('', AccessTokenObtainView.as_view(),

         name='access_token_obtain'),

    path('refresh/', AccessTokenRefreshView.as_view(),
         name='access_token_refresh'),

]
