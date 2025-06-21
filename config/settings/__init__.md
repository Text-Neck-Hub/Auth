
---

## ⚙️ 환경 설정 (Settings)

우리 프로젝트는 **환경 변수**를 사용해서 개발, 프로덕션 등 다양한 환경에 맞는 설정을 유연하게 적용하고 있어요! ✨

특히 `DJANGO_SETTINGS_MODULE` 이라는 환경 변수를 사용해서 어떤 설정 파일을 불러올지 결정한답니다!

### 설정 로딩 방식 이해하기

프로젝트의 `config/settings/__init__.py` 파일에 있는 다음 코드가 바로 이 역할을 수행해요.

```python
# config/settings/__init__.py

import os
from importlib import import_module

# 1. 'DJANGO_SETTINGS_MODULE' 환경 변수 값을 읽어와요.
#    만약 이 환경 변수가 설정되어 있지 않으면 기본값으로 'config.settings.local'을 사용해요.
settings_module = os.environ.get(
    'DJANGO_SETTINGS_MODULE', 'config.settings.local')

try:
    # 2. importlib.import_module() 함수를 사용해서
    #    settings_module 변수에 저장된 이름(문자열)에 해당하는 파이썬 모듈(파일)을 동적으로 임포트해요.
    #    이렇게 임포트된 모듈 객체가 settings_module_object 변수에 담겨요.
    settings_module_object = import_module(settings_module)

    # 3. 임포트된 모듈 객체(settings_module_object) 안에 있는 모든 이름들을 살펴봐요.
    for setting in dir(settings_module_object):
        # 4. 그 이름이 모두 대문자인지 확인해요. (Django 설정 변수는 보통 대문자!)
        if setting.isupper():
            # 5. 대문자인 이름(setting)에 해당하는 값(getattr)을 임포트된 모듈에서 가져와서,
            #    현재 settings/__init__.py 파일의 전역 변수(globals())로 만들어줘요.
            #    이렇게 해야 Django가 settings.DEBUG, settings.SECRET_KEY 등으로 접근할 때 값을 찾을 수 있어요!
            globals()[setting] = getattr(settings_module_object, setting)

except ImportError as e:
    # 6. 만약 settings_module에 지정된 이름의 모듈(파일)을 찾거나 임포트할 수 없으면,
    #    자세한 에러 메시지를 출력하고 프로그램을 종료해요.
    raise ImportError(
        f"Could not import settings '{settings_module}'. "
        f"It isn't on your PYTHONPATH."
    ) from e

```

### 이게 왜 필요할까요?

*   **유연성:** `DJANGO_SETTINGS_MODULE` 환경 변수 값만 바꿔주면, 코드 수정 없이 개발/프로덕션/스테이징 등 다양한 환경의 설정 파일을 쉽게 전환할 수 있어요.
*   **확장성:** 새로운 환경을 추가하고 싶을 때, 해당 환경의 설정 파일만 만들고 `DJANGO_SETTINGS_MODULE` 값만 지정해주면 돼요. `__init__.py` 코드를 수정할 필요가 없답니다!
*   **명확성:** `settings` 패키지를 임포트했을 때, 실제 사용되는 설정 변수들(`DEBUG`, `INSTALLED_APPS` 등)이 `__init__.py`의 전역 네임스페이스에 바로 노출되어 어떤 설정이 적용되었는지 파악하기 쉬워요.

### 사용 방법

애플리케이션을 실행할 때 `DJANGO_SETTINGS_MODULE` 환경 변수에 사용하고 싶은 설정 파일의 경로를 지정해주세요.

*   **개발 환경 (local.py 사용):**
    ```bash
    # 환경 변수 미설정 시 기본값(config.settings.local) 사용
    python manage.py runserver
    # 또는 명시적으로 지정
    DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver
    ```
*   **프로덕션 환경 (production.py 사용):**
    ```bash
    # 프로덕션에 필요한 다른 환경 변수들과 함께 지정
    SECRET_KEY='...' DATABASE_URL='...' DJANGO_SETTINGS_MODULE=config.settings.production gunicorn config.wsgi:application --bind 0.0.0.0:8000
    ```
*   **Docker Compose 사용 시:**
    `docker-compose.yml` 파일의 해당 서비스 설정에 `environment` 또는 `env_file` 옵션을 사용해서 `DJANGO_SETTINGS_MODULE` 값을 지정해주세요. (자세한 내용은 Docker 설정 부분을 참고해주세요!)

---

