# HeatWatch Nigeria

Heat monitoring for Nigerian cities: a FastAPI service that ingests hourly weather data, computes heat-index metrics, and serves them through an authenticated REST API (dashboard coming next).

## Architecture

```mermaid
flowchart LR
  OM[Open-Meteo API] -->|hourly| ING[Ingestion job<br/>httpx + pandas]
  ING --> DB[(PostgreSQL)]
  DB --> API[FastAPI<br/>async + Pydantic]
  API -->|X-API-Key| DASH[Dashboard<br/>Next.js + Leaflet]
```

## Quick start

```bash
cp .env.example .env
docker compose up --build -d
docker compose run --rm ingest          # seeds cities, pulls the last 2 days
curl -H "X-API-Key: dev-key" http://localhost:8000/rankings/hottest
```

Interactive docs: http://localhost:8000/docs

## API

All routes except `/health` need an `X-API-Key` header.

| Route | Description |
|---|---|
| `GET /cities` | Tracked cities |
| `GET /cities/{slug}/temperature?from=&to=&limit=` | Hourly readings with heat index and risk category |
| `GET /cities/{slug}/heat-summary?days=7` | Current conditions, daily min/max/mean, anomaly |
| `GET /rankings/hottest?hours=24&limit=10` | Cities ranked by peak heat index |
| `GET /health` | Liveness check |

Heat index uses the US NWS Rothfusz regression; risk bands follow NWS categories. Timestamps are UTC.

## Develop and test

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

Tests run against in-memory SQLite, so no database is needed.

## Roadmap

- [x] Ingestion pipeline, heat metrics, authenticated API, tests, Docker, CI
- [ ] Dashboard: Next.js + Leaflet map + trend charts
- [ ] Redis caching on ranking and summary endpoints
- [ ] Alembic migrations
- [ ] Historical backfill (Open-Meteo archive) for a real climate baseline
- [ ] Deployment on AWS (S3 + CloudFront, EventBridge + Lambda, EC2/App Runner)
