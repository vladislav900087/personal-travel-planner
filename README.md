# Personal Travel Planner

Web application for planning multi-city trips: destinations, itineraries, places, budgets, expenses and travel documents.

## Stack

- **Backend:** Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Infrastructure:** Docker Compose, GitHub Actions

## Quick start

```bash
# 1. copy env file
cp .env.example .env

# 2. start services
docker compose up --build

# 3. check it works
curl http://localhost:8000/health
```

Backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

## Tests

```bash
cd backend
pip install ".[dev]"
pytest -v
```

## Project structure

```
backend/
  app/
    api/          # routes
    application/  # use cases
    domain/       # business rules
    models/       # SQLAlchemy models
    schemas/      # Pydantic schemas
    core/         # config, security
    tasks/        # background jobs
  tests/
frontend/
docs/
```
