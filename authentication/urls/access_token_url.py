from django.urls import path
from .. import views


urlpatterns = [
    path('/', views.AccessTokenObtainView.as_view(),
         name='access_token_obtain'),

    path('/refresh/', views.AccessTokenRefreshView.as_view(),
         name='access_token_refresh'),

]
