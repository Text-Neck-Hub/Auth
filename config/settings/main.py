from split_settings.tools import include
import os


if not os.environ.get('SECRET_KEY'):
    raise ValueError(
        "The environment variable 'SECRET_KEY' is deprecated. "
        "Please use 'SECRET_KEY' instead."
    )

include(
    'base.py',
    'jwt.py',
    'logging.py',
    'production.py',
)
