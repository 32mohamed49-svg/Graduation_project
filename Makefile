.PHONY: up up-dev down logs test lint ingest train evaluate

COMPOSE := docker compose
COMPOSE_DEV := docker compose -f docker-compose.yml -f docker-compose.dev.yml

up:
	$(COMPOSE) up -d --build

up-dev:
	$(COMPOSE_DEV) up --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=100

test:
	cd backend && python -m pytest tests -v

lint:
	python -m ruff check backend scripts

ingest:
	python scripts/ingest_data.py --input-dir data/raw

train:
	python scripts/train_model.py

evaluate:
	python scripts/evaluate_model.py
