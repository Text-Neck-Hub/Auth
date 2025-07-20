from .base import *
import os
import dj_database_url
from .jwt import *
from .logging import *
DEBUG = False

allowed_hosts_string = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = allowed_hosts_string.split(
    ',') + ['210.94.252.178'] if allowed_hosts_string else ['*']

DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
}



LOGIN_REDIRECT_URL = 'https://www.textneckhub.p-e.kr/auth/callback/'
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True

CSRF_COOKIE_DOMAIN = ".textneckhub.p-e.kr"
SESSION_COOKIE_DOMAIN = ".textneckhub.p-e.kr"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

CSRF_TRUSTED_ORIGINS = [
    "https://www.textneckhub.p-e.kr",
    "https://textneckhub.p-e.kr",
    "https://api.textneckhub.p-e.kr",
]
CORS_ALLOWED_ORIGINS = [
    "https://www.textneckhub.p-e.kr",
]
CORS_ALLOW_CREDENTIALS = True


USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
