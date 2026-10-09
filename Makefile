.PHONY: help up down restart logs ps test test-backend test-frontend build migrate clean

help:
	@echo "Enterprise Document Intelligence Platform - Command Center"
	@echo "==========================================================="
	@echo "make up             Start all services in background via Docker Compose"
	@echo "make down           Stop and remove all containers"
	@echo "make restart        Restart all containers"
	@echo "make logs           Follow application logs"
	@echo "make ps             Check container health and statuses"
	@echo "make migrate        Run database migrations with Alembic"
	@echo "make build          Build both backend and frontend images"
	@echo "make test           Run both backend and frontend tests"
	@echo "make test-backend   Run pytest test suite"
	@echo "make test-frontend  Run frontend build check"
	@echo "make clean          Remove temporary files and caches"

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

ps:
	docker compose ps

migrate:
	docker compose exec api alembic upgrade head

build:
	docker compose build

test-backend:
	python -m pytest -v

test-frontend:
	cd frontend && npm run build

test: test-backend test-frontend

clean:
	rm -rf .pytest_cache app/__pycache__ frontend/dist frontend/node_modules/.vite
