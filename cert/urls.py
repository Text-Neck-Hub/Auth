from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.TokenVerificationView.as_view(),
         name='token_verify'),
]
