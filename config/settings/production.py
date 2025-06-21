

from .base import *
import os
import dj_database_url
DEBUG = False


allowed_hosts_string = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = allowed_hosts_string.split(',') if allowed_hosts_string else []


SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:

    raise EnvironmentError("SECRET_KEY 환경변수가 설정되지 않았습니다.")


DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise EnvironmentError("DATABASE_URL 환경변수가 설정되지 않았습니다.")

DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
}


STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
