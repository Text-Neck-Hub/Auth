.PHONY: run test coverage coverage-html clean

run:
	uv run uvicorn config.asgi:application --reload --host 0.0.0.0 --port 8001
migrate:
	uv run python manage.py migrate
	uv run python manage.py makemigrations

collect:
	uv run python manage.py collectstatic --noinput

test:
	uv run pytest --disable-warnings

coverage:
	uv run pytest --cov=oauth --cov-report=term-missing --disable-warnings

coverage-html:
	uv run pytest --cov=oauth --cov-report=html --disable-warnings

clean:
	uv run rm -rf .pytest_cache .coverage htmlcov