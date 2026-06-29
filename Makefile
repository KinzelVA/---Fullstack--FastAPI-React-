.PHONY: backend-dev frontend-dev backend-test frontend-build docker-build docker-up docker-down lint

backend-dev:
python -m uvicorn backend.app.main:app --reload

frontend-dev:
cd frontend && npm run dev

backend-test:
python -m pytest backend/tests -q

frontend-build:
cd frontend && npm run build

docker-build:
docker compose build

docker-up:
docker compose up

docker-down:
docker compose down

lint:
python -m ruff check backend
