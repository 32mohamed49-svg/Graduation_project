# Graduation project — HAQI

HAQI is an Arabic Retrieval-Augmented Generation (RAG) assistant designed to help citizens navigate Egyptian/Arabic government services and public rights. The MVP focuses on the **civil status sector** (e.g., national IDs, birth/marriage/death certificates, family records, required documents, fees, and procedures).

## Architecture Overview

```text
React + Vite Frontend (Nginx)
          |
          v  REST API (/api/v1)
FastAPI Backend (RAG Orchestrator)
   ├── Ingestion & Arabic Normalization
   ├── Overlapping Text Chunking
   ├── Embeddings Client
   ├── Vector Retrieval  --->  Qdrant (Vector DB, persistent named volume)
   └── Prompt Builder & LLM Client
```

See [docs/architecture.md](docs/architecture.md) and [docs/api.md](docs/api.md) for detailed design and API contracts.

## Folder Guide

| Path | Purpose |
|---|---|
| `backend/` | FastAPI service, schemas, business services, RAG modules, unit tests, and production Dockerfile |
| `frontend/` | React + Vite + TypeScript web interface and multi-stage Nginx Dockerfile |
| `data/raw/` | Raw source documents for ingestion (gitignored except `.gitkeep`) |
| `data/processed/` | Processed chunks, evaluation sets, and intermediate exports (gitignored except `.gitkeep`) |
| `notebooks/` | Jupyter experiments and RAG evaluation notebooks |
| `scripts/` | Standalone CLI scripts (`ingest_data.py`, `evaluate_rag.py`) |
| `docs/` | Architecture notes, API contracts, and domain documentation |
| `legacy/supply_chain/` | Preserved prior coursework files from team repository history |

## Prerequisites

- Docker & Docker Compose v2 (for containerized runs)
- Python 3.11+ (for local backend development and CLI scripts)
- Node.js 20+ & npm (for local frontend development)

## Quick Start (Docker)

1. Copy the root environment template and fill in your credentials:

   ```bash
   cp .env.example .env
   ```

2. Build and start Qdrant, backend, and frontend:

   ```bash
   make up
   ```

3. For hot-reload development mode:

   ```bash
   make up-dev
   ```

4. View logs or stop services:

   ```bash
   make logs
   make down
   ```

## Local Development (Without Docker)

### Backend

```bash
cd backend
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Run tests and linter:

```bash
make test
make lint
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

### Data Ingestion & Evaluation

Place raw civil-status documents under `data/raw/`, set `QDRANT_HOST=localhost` in `.env` when running scripts on the host, then run:

```bash
python scripts/ingest_data.py --input-dir data/raw
python scripts/evaluate_rag.py --dataset data/processed/eval_dataset.jsonl
```
