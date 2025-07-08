# Auth/app/config/urls.py (Auth 서비스의 최상위 urls.py)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 🚨🚨🚨 Admin 페이지의 외부 노출 경로를 지정합니다. 🚨🚨🚨
# Nginx의 location /auth-admin/ { proxy_pass http://auth:8000/auth-admin/; } 에 대응
# 즉, Django 앱은 /auth-admin/ 경로로 Admin 페이지를 제공합니다.
admin.site.root_path = '/auth-admin/' # 👈 Nginx가 이 경로로 직접 프록시!

urlpatterns = [
    # 🚨🚨🚨 Admin 페이지는 내부적으로 /auth-admin/ 경로로 제공합니다. 🚨🚨🚨
    # Nginx가 /auth-admin/ 요청을 그대로 http://auth:8000/auth-admin/ 으로 전달합니다.
    path('auth-admin/', admin.site.urls), # Admin 페이지의 실제 내부 경로

    # API 엔드포인트 (Nginx가 /auth/를 제거하고 /v2/를 전달)
    path('v2/', include('authentication.urls')), # authentication 앱의 API URL

    path('accounts/', include('allauth.urls')), # allauth 관련 URL (OAuth 콜백 등)
    path('prometheus/', include('django_prometheus.urls')), # Prometheus 메트릭
]

# DEBUG 모드에서만 정적 파일 서빙 (프로덕션에서는 Nginx가 담당)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)