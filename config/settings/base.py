import os
import logging
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = 'django-insecure-tbuqcb4-2$t-l&@qs_if)y4v&opr9bdlbvu#-*m)r8hca*$nle'
DEBUG = True
ALLOWED_HOSTS = ["*"]

# 💖 네가 만든 ColoredFormatter는 그대로 사용! 💖


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        # super().format(record)는 포매터에 정의된 'format' 문자열을 사용해!
        return f"{log_color}{super().format(record)}{self.RESET}"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # 기존 로거 비활성화 안 함!

    "formatters": {
        "colored": {  # 💖 콘솔 출력을 위한 색상 포매터! 💖
            "()": ColoredFormatter,
            # ColoredFormatter가 사용할 기본 형식
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "verbose": {  # 💖 파일 저장을 위한 상세 포매터! 💖
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {  # 💖 간단한 포매터 (필요시 사용)! 💖
            "format": "{levelname} {message}",
            "style": "{",
        },
    },

    "handlers": {
        "console": {  # 💖 콘솔 출력 핸들러! 💖
            "class": "logging.StreamHandler",
            "formatter": "colored",  # 색상 포매터 적용!
            "level": "DEBUG",  # 개발 시에는 DEBUG 레벨까지 모두 출력!
        },
        "file": {  # 💖 일반 로그 파일 핸들러 (RotatingFileHandler로 변경)! 💖
            "class": "logging.handlers.RotatingFileHandler",  # 파일 크기 제한 및 자동 로테이션!
            # 💖 컨테이너 내부 경로! 💖
            "filename": os.path.join('/app/logs', 'debug.log'),
            "maxBytes": 1024 * 1024 * 5,  # 5MB
            "backupCount": 5,  # 최대 5개까지 백업 파일 유지
            "formatter": "verbose",
            "level": "INFO",  # 파일에는 INFO 레벨 이상만 저장하는 게 일반적이야!
        },
        "error_file": {  # 💖 에러 로그 전용 파일 핸들러 추가! 💖
            "class": "logging.handlers.RotatingFileHandler",
            # 💖 컨테이너 내부 경로! 💖
            "filename": os.path.join('/app/logs', 'error.log'),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
            "level": "ERROR",  # ERROR 레벨 이상만 저장!
        },
    },

    "loggers": {
        "prod": {  # 💖 네 프로젝트/앱 로거! 💖
            "handlers": ["console", "file", "error_file"],  # 모든 핸들러 연결!
            "level": "DEBUG",  # 개발 시에는 DEBUG 레벨까지 모두 로깅!
            "propagate": False,  # 💖 상위 로거로 전파하지 않음 (중복 방지)! 💖
        },
        "django": {  # 💖 장고 프레임워크 자체 로거! 💖
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {  # 💖 HTTP 요청 관련 로거 (404, 500 에러 등)! 💖
            "handlers": ["console", "error_file"],  # 콘솔과 에러 파일로!
            "level": "ERROR",  # ERROR 레벨 이상만 처리!
            "propagate": False,
        },
        # 💖 써드파티 앱 로거 (필요시 추가)! 💖
        # 'allauth': {
        #     'handlers': ['console', 'file'],
        #     'level': 'INFO',
        #     'propagate': False,
        # },
        # 'django_prometheus': {
        #     'handlers': ['console', 'file'],
        #     'level': 'INFO',
        #     'propagate': False,
        # },
        "": {  # 💖 루트 로거 (모든 로거의 부모)! 💖
            "handlers": ["console", "file"],  # 콘솔과 일반 파일로!
            "level": "INFO",  # INFO 레벨 이상 모든 로그 처리!
            "propagate": False,  # 루트 로거는 보통 propagate를 False로 두지 않아!
            # 하지만 명시적으로 핸들러를 연결했으니 괜찮아!
        },
    },
}
VANILA_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'django_prometheus',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.kakao',
    'channels'
]

LOCAL_APPS = ['oauth', 'cert']

INSTALLED_APPS = VANILA_APPS + THIRD_PARTY_APPS + LOCAL_APPS

VANILA_MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
THIRD_PARTY_MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware',
                          'allauth.account.middleware.AccountMiddleware']
MIDDLEWARE = VANILA_MIDDLEWARE + THIRD_PARTY_MIDDLEWARE


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        # ✨ 여기! django_prometheus를 붙여줬어!
        'ENGINE': 'django_prometheus.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5), # 액세스 토큰 유효 기간 (짧게!)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1), # 리프레시 토큰 유효 기간 (길게!)
    'ROTATE_REFRESH_TOKENS': False, # 리프레시 토큰 갱신 시 새 리프레시 토큰 발급 여부 (보안상 True 권장)
    'BLACKLIST_AFTER_ROTATION': False, # 리프레시 토큰 갱신 시 이전 토큰 블랙리스트 처리 여부 (보안상 True 권장)
    'UPDATE_LAST_LOGIN': False, # 마지막 로그인 시간 업데이트 여부

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY, # Django SECRET_KEY 사용
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',), # 인증 헤더 타입
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
        'FETCH_USERINFO': True,
    },
    'kakao': {
        'SCOPE': [
            'profile_nickname',
            'account_email',
        ],
        'AUTH_PARAMS': {},
        'OAUTH_PKCE_ENABLED': True,
        'FETCH_USERINFO': True,
    }
}

SOCIALACCOUNT_STORE_TOKENS = True
ROOT_URLCONF = 'config.urls'
LOGIN_REDIRECT_URL = '/v2/callback/google/'

SITE_ID = 7
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
