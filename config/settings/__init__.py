import os
import glob

settings_module = os.environ.get(
    'DJANGO_SETTINGS_MODULE', 'config.settings.local'
)

try:
    from importlib import import_module

    # 메인 settings 모듈 import
    settings_module_object = import_module(settings_module)
    for setting in dir(settings_module_object):
        if setting.isupper():
            globals()[setting] = getattr(settings_module_object, setting)

    # settings 디렉토리 내의 모든 .py 파일을 동적으로 import (특정 파일 제외)
    settings_dir = os.path.dirname(__file__)
    for path in glob.glob(os.path.join(settings_dir, '*.py')):
        module_name = os.path.splitext(os.path.basename(path))[0]
        if module_name in ('__init__', 'base'):
            continue
        try:
            extra_module = import_module(f'config.settings.{module_name}')
            for setting in dir(extra_module):
                if setting.isupper():
                    globals()[setting] = getattr(extra_module, setting)
        except ImportError:
            pass

except ImportError as e:
    raise ImportError(
        f"Could not import settings '{settings_module}'. "
        f"It isn't on your PYTHONPATH."
    ) from e
