from split_settings.tools import include
import os


settings_module = os.environ.get(
    'DJANGO_SETTINGS_MODULE', 'config.settings.local'
)
if not os.environ.get('SECRET_KEY'):
    raise ValueError(
        "The environment variable 'SEKRET_KEY' is deprecated. "
        "Please use 'SECRET_KEY' instead."
    )

include(
    'base.py',
    'jwt.py',
    'logging.py',
    'production.py',
)
