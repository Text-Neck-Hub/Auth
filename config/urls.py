from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('auth/admin/', admin.site.urls),
    path('auth/v2/', include('authentication.urls')),
    path('auth/accounts/', include('allauth.urls')),
    path('auth/prometheus/', include('django_prometheus.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
