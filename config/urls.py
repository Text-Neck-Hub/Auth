from django.contrib import admin
from django.urls import path, include
import django_prometheus.urls
from django.conf.urls.static import static

from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/callback/', include('oauth.urls'), name='oauth'),
    path('accounts/', include('allauth.urls')),
    path('prometheus/', include('django_prometheus.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
