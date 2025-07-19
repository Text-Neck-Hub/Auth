from django.urls import path, include
from .routers import (
    access_token_router,
    refresh_token_router,
    user_profile_router,
)


urlpatterns = [
    path('access-token/',
         include(access_token_router)),
    path('refresh-token/', include(refresh_token_router)),
    path('profile/', include(user_profile_router)),
]
