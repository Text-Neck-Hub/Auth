from django.urls import path
from ..views.user_profile_view import UserProfileView


urlpatterns = [
    path('me/', UserProfileView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='user_profile'),
]
