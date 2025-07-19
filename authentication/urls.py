from django.urls import path, include

app_name = 'authentication'

urlpatterns = [
    path('access-token/',
         include(f'{app_name}.urls.access_token_urls')),
    path('refresh-token/', include(f'{app_name}.urls.refresh_token_urls')),
    path('profile/', include(f'{app_name}.urls.user_profile_urls')),
]
