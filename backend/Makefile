# ============================================================
# Pizza Backend — Makefile
# FastAPI + SQLAlchemy + Alembic + PostgreSQL
# ============================================================

.DEFAULT_GOAL := help

PYTHON := python
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
RUFF := $(PYTHON) -m ruff
ALEMBIC := $(PYTHON) -m alembic
UVICORN := $(PYTHON) -m uvicorn

APP := app.main:app
HOST := 127.0.0.1
PORT := 8000


# ============================================================
# HELP
# ============================================================

.PHONY: help

help:
	@echo ""
	@echo "Pizza Backend"
	@echo "======================================"
	@echo ""
	@echo "Development:"
	@echo "  make dev              Run FastAPI with reload"
	@echo "  make run              Run FastAPI without reload"
	@echo ""
	@echo "Dependencies:"
	@echo "  make install          Install dependencies"
	@echo "  make freeze           Save dependencies to requirements.txt"
	@echo ""
	@echo "Code quality:"
	@echo "  make lint             Check code with Ruff"
	@echo "  make lint-fix         Fix Ruff errors automatically"
	@echo "  make format           Format code with Ruff"
	@echo "  make check            Run lint + tests"
	@echo ""
	@echo "Tests:"
	@echo "  make test             Run tests"
	@echo "  make test-v           Run tests in verbose mode"
	@echo ""
	@echo "Database:"
	@echo "  make migration name=\"message\""
	@echo "                        Create Alembic migration"
	@echo "  make migrate          Apply all migrations"
	@echo "  make downgrade        Rollback last migration"
	@echo "  make db-current       Show current migration"
	@echo "  make db-history       Show migration history"
	@echo "  make db-heads         Show migration heads"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up        Start Postgres + S3 storage"
	@echo "  make docker-down      Stop Docker services"
	@echo "  make docker-logs      Tail Docker logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove Python cache files"
	@echo ""


# ============================================================
# DEVELOPMENT
# ============================================================

.PHONY: dev run

dev:
	$(UVICORN) $(APP) --reload --host $(HOST) --port $(PORT)

run:
	$(UVICORN) $(APP) --host $(HOST) --port $(PORT)


# ============================================================
# DEPENDENCIES
# ============================================================

.PHONY: install freeze

install:
	$(PIP) install -r requirements.txt

freeze:
	$(PIP) freeze > requirements.txt


# ============================================================
# CODE QUALITY
# ============================================================

.PHONY: lint lint-fix format check

lint:
	$(RUFF) check .

lint-fix:
	$(RUFF) check . --fix

format:
	$(RUFF) format .

check: lint test


# ============================================================
# TESTS
# ============================================================

.PHONY: test test-v

test:
	$(PYTEST)

test-v:
	$(PYTEST) -v


# ============================================================
# DATABASE / ALEMBIC
# ============================================================

.PHONY: migration migrate downgrade db-current db-history db-heads

migration:
ifndef name
	$(error Usage: make migration name="migration message")
endif
	$(ALEMBIC) revision --autogenerate -m "$(name)"

migrate:
	$(ALEMBIC) upgrade head

downgrade:
	$(ALEMBIC) downgrade -1

db-current:
	$(ALEMBIC) current

db-history:
	$(ALEMBIC) history

db-heads:
	$(ALEMBIC) heads


# ============================================================
# DOCKER
# ============================================================

.PHONY: docker-up docker-down docker-logs

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# ============================================================
# CLEANUP
# ============================================================

.PHONY: clean

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
