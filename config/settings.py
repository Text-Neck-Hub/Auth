import os
from .settings import *

DJANGO_ENV = os.environ.get('DJANGO_ENV', 'local')

if DJANGO_ENV == 'production':
    from .settings.production import *
else:
    from .settings.local import *
