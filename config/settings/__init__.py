import os


settings_module = os.environ.get(
    'DJANGO_SETTINGS_MODULE', 'config.settings.local')

try:
    from importlib import import_module
    settings_module_object = import_module('config.settings.production')
    
    for setting in dir(settings_module_object):
        print(f"Loading setting: {setting}")
        if setting.isupper():
            
            globals()[setting] = getattr(settings_module_object, setting)

except ImportError as e:

    raise ImportError(
        f"Could not import settings '{settings_module}'. "
        f"It isn't on your PYTHONPATH."
    ) from e
