from .base import *
from .jwt import *
DEBUG = True
ALLOWED_HOSTS = ["*"]
DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
