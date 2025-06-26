from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v2/auth/', include('authentication.urls'), name='authentication'),
    path('accounts/', include('allauth.urls')),
    path('prometheus/', include('django_prometheus.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
