from django.urls import path
from . import views

urlpatterns = [
    path('google/', views.GoogleOAuthCallbackView.as_view(),
         name='google_oauth_callback'),
]
