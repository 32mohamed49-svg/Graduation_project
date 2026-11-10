.PHONY: up up-dev down logs test lint ingest evaluate

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
	cd backend && python -m ruff check app tests ../scripts

ingest:
	python scripts/ingest_data.py --input-dir data/raw

evaluate:
	python scripts/evaluate_rag.py --dataset data/processed/eval_dataset.jsonl

