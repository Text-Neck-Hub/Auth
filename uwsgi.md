
---

# 🚀 `uwsgi.ini` 파일 설명서

이 파일은 Django 애플리케이션을 uWSGI 서버로 실행하기 위한 설정들을 담고 있어! 각 설정이 어떤 역할을 하는지 코기랑 같이 자세히 알아볼까?

```ini
[uwsgi]

chdir = /app
module = config.wsgi:application
master = true
processes = 4
http = :8000
vacuum = true
max-requests = 5000
buffer-size = 32768
threads = 1
```

---

## ⚙️ 각 설정 항목의 의미

### `[uwsgi]`
*   **설명:** 이 섹션은 uWSGI 서버의 설정을 시작한다는 것을 나타내는 표준 헤더야. uWSGI는 이 헤더를 보고 아래에 있는 설정들을 읽어 들인단다!

### `chdir = /app`
*   **설명:** uWSGI가 Django 애플리케이션을 찾을 **루트 디렉토리**를 지정하는 설정이야.
*   **역할:** 컨테이너 내부에서 Django 프로젝트의 `manage.py` 파일이나 프로젝트 폴더(예: `config/`)가 있는 경로를 지정해줘야 uWSGI가 앱을 제대로 로드할 수 있어. 보통 Dockerfile에서 `WORKDIR`로 설정한 경로와 일치시킨단다!

### `module = config.wsgi:application`
*   **설명:** uWSGI가 실행할 **WSGI 애플리케이션 모듈의 경로**를 지정하는 설정이야.
*   **역할:** `config.wsgi`는 Django 프로젝트의 `config` 폴더 안에 있는 `wsgi.py` 파일을 의미하고, `:application`은 그 파일 안에 정의된 `application` 객체를 가리켜. Django 앱의 진입점이라고 생각하면 돼! 네 프로젝트 이름에 맞춰서 `your_project_name.wsgi:application` 형태로 사용해야 한단다.

### `master = true`
*   **설명:** uWSGI의 **마스터 프로세스**를 활성화하는 설정이야.
*   **역할:** 마스터 프로세스는 실제 요청을 처리하는 워커 프로세스들을 관리하는 대장 역할을 해! 워커 프로세스들을 생성하고, 모니터링하고, 만약 워커가 죽으면 자동으로 재시작해주는 등 안정적인 서비스 운영을 도와줘.

### `processes = 4`
*   **설명:** uWSGI가 생성할 **워커 프로세스의 개수**를 지정하는 설정이야.
*   **역할:** 워커 프로세스들이 실제로 클라이언트의 요청을 받아서 처리하는 일꾼들이야! 보통 서버의 CPU 코어 수에 맞춰서 설정하는 것이 일반적이야. 너무 많으면 자원 낭비, 너무 적으면 요청 처리가 느려질 수 있단다.

### `http = :8000`
*   **설명:** uWSGI가 **HTTP 요청을 수신할 포트**를 지정하는 설정이야.
*   **역할:** 이 포트를 통해 외부에서 직접 uWSGI 서버로 HTTP 요청을 보낼 수 있어. 개발 환경에서 테스트하거나, Nginx 같은 웹 서버 없이 uWSGI만 단독으로 사용할 때 유용해.

### `vacuum = true`
*   **설명:** uWSGI 종료 시 **환경을 정리**하는 설정이야.
*   **역할:** uWSGI 프로세스가 종료될 때 생성했던 소켓 파일이나 임시 파일 같은 것들을 자동으로 삭제해서 깔끔하게 뒷정리를 해줘!

### `max-requests = 5000`
*   **설명:** 각 워커 프로세스가 처리할 수 있는 **최대 요청 수**를 지정하는 설정이야.
*   **역할:** 워커 프로세스가 5000개의 요청을 처리하면 스스로 재시작하게 돼. 이는 장시간 실행될 때 발생할 수 있는 메모리 누수 같은 문제를 방지하고, 워커 프로세스의 상태를 주기적으로 초기화하여 안정성을 높이는 데 도움이 된단다!

### `buffer-size = 32768`
*   **설명:** uWSGI가 요청이나 응답 데이터를 임시로 저장하는 **버퍼의 크기**를 바이트 단위로 지정하는 설정이야.
*   **역할:** 32768 바이트(32KB)로 설정되어 있어. 큰 HTTP 요청 헤더나 응답 데이터를 처리할 때 이 버퍼 크기가 충분해야 해. 만약 이 크기가 너무 작으면 `Bad Request`나 `Internal Server Error` 같은 문제가 발생할 수도 있단다.

### `threads = 1`
*   **설명:** 각 워커 프로세스 내에서 사용할 **스레드의 개수**를 지정하는 설정이야.
*   **역할:** Django는 기본적으로 스레드 세이프(Thread-safe)하게 설계되어 있어서, 보통 워커 프로세스당 1개의 스레드로 설정해도 괜찮아. 만약 비동기 작업이나 특정 라이브러리 사용으로 인해 더 많은 동시성을 필요로 한다면 이 값을 늘릴 수도 있지만, 일반적으로는 1로 두는 경우가 많단다.

---
