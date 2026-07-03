# AGENTS.md

This file provides guidance to AI agents working with code in this repository.

## Project Overview

PPD Forms (Типовые формы для отчетов ППД) — a FastAPI web service for generating standard reservoir pressure maintenance (PPD) reports. It loads data from PostgreSQL (local) and Oracle (OFM) databases, processes it via background workers, and produces CSV/Excel reports.

## Commands

```bash
# Install dependencies (all groups)
poetry install --with web,worker,dev --no-root

# Run web server
poetry run task uvicorn

# Run background worker
poetry run task worker

# Run database migrations
poetry run task migrate

# Generate a migration
poetry run task makemigrations

# Initialize seed data
poetry run task initialize

# Run tests (requires Docker for testcontainers)
poetry run pytest

# Run a single test file
poetry run pytest tests/unit/mapper/test_base_mapper.py

# Lint/format (via pre-commit or manually)
poetry run pre-commit run --all-files
poetry run black --line-length=79 app/ tests/
poetry run isort --profile=black --line-length=79 app/ tests/
poetry run flake8 app/
poetry run mypy app/

# Run with Docker (full stack: DB, Redis, web, worker)
docker-compose --profile api -f docker-compose-local.yml up -d --build

# Run migrations via Docker
docker-compose --profile migration -f docker-compose-local.yml up -d --build
```

## Architecture

Two processes run simultaneously:
- **Web** (`app/main.py` → `init_api`) — FastAPI app serving REST endpoints and HTML pages via Jinja2 templates
- **Worker** (`app/worker.py` → `WorkerSettings`) — arq worker consuming jobs from Redis, executing report generation

### Layer Structure

```
app/
├── api/                  # Presentation layer
│   ├── config/           # API settings (auth, CORS)
│   ├── dependencies/     # FastAPI dependency injection providers
│   ├── endpoints/        # Route handlers (auth, database, excel, job, report, uneft, users)
│   ├── middlewares/      # Middleware setup
│   ├── models/           # Pydantic request/response schemas
│   └── utils/            # Validators
├── common/               # Shared config (paths)
├── core/                 # Business logic
│   ├── config/           # App-level settings (AppSettings, MmbSettings)
│   ├── models/           # DTOs, enums, schemas
│   ├── services/         # Domain services
│   │   ├── cron/         # Scheduled tasks (refresh tables, clean files)
│   │   ├── entrypoints/  # Job dispatch: arq registry + DB/CSV data loading
│   │   └── reports/      # Report generation logic (profile, matbal, matrix, mmb, etc.)
│   └── utils/            # Process pool manager for CPU-bound work
└── infrastructure/       # Data access layer
    ├── db/
    │   ├── config/       # DB settings (PostgresSettings, OracleSettings)
    │   ├── dao/          # Data Access Objects
    │   │   ├── local/    # PostgreSQL DAOs (one per table, extends BaseDAO)
    │   │   ├── sql/       # Oracle/OFM DAOs + SQL querysets + DB reporters
    │   │   └── complex/   # Composite DAOs (initializers, loaders, reporters combining multiple sources)
    │   ├── factories/    # Session pool factories (async local, sync OFM)
    │   ├── mappers/      # Name-mapping system (field/reservoir/layer/GTM replacements)
    │   ├── migrations/   # Alembic migrations
    │   └── models/       # SQLAlchemy ORM models (local/ = PostgreSQL, ofm/ = Oracle reflected)
    ├── files/
    │   ├── config/       # CSV settings
    │   └── dao/          # File-based DAOs (csv/, excel/, reporters/)
    ├── log/               # Structured logging (structlog + rotating file handler)
    ├── redis/             # Redis/arq config, factories, DAO (ArqDAO, ScheduledJobsDAO)
    ├── holder.py          # HolderDAO — service locator providing all DAO instances
    └── provider.py        # DbProvider — creates and manages session pools
```

### Key Patterns

- **HolderDAO** (`app/infrastructure/holder.py`): Central service locator. Accepts `**kwargs` (sessions, pools, paths) and exposes properties for every DAO. Different context managers in `DbProvider` inject different session combinations (local only, OFM only, OFM+local, OFM+Redis).

- **WorkRegistry** (`app/core/services/entrypoints/registry.py`): Decorator-based registry mapping route strings (e.g. `"report:profile"`, `"excel:ns_ppd:refresh"`) to async handler functions. The worker's `perform_work` looks up `response.task.route_url` in this registry.

- **BaseDAO** (`app/infrastructure/db/dao/local/base.py`): Generic `BaseDAO[Model, DataModel]` with standard CRUD. Individual DAOs extend it with custom queries.

- **Mappers** (`app/infrastructure/db/mappers/`): Name-replacement system that maps OFM well/field/reservoir names to local naming conventions. Initialized at startup via `initialize_mapper()`.

- **Config pattern**: All settings use `pydantic_settings.BaseSettings` reading from `.env` file. Factory functions (`get_postgres_settings`, `get_redis_settings`, etc.) are `@lru_cache`d singletons.

- **DTO/Schema split**: `app/core/models/dto/` contains internal data transfer objects used by workers. `app/core/models/schemas/` contains API request validation models. `app/api/models/responses.py` contains API response models.

### Data Flow

1. API endpoint creates a `TaskXxx` DTO and `JobStamp`, wraps in a typed `Response`
2. Response is enqueued to Redis via `ArqDAO.enqueue_task()`
3. Worker picks up job, calls `perform_work()` which dispatches to the registered handler via `WorkRegistry`
4. Handler acquires a `HolderDAO` context (with appropriate sessions), calls domain service
5. Domain service uses DAOs to query data, generates report files (CSV/Excel)
6. Job status tracked via arq's `Job` API; clients poll via REST or WebSocket

### Database

- **Local DB**: PostgreSQL (async, SQLAlchemy 2.0 + asyncpg). Models in `app/infrastructure/db/models/local/`. Migrations via Alembic at `app/infrastructure/db/migrations/`.
- **OFM DB**: Oracle (sync, oracledb). Models are auto-reflected at startup via `Reflected.prepare()`. The OFM connection is optional — if unavailable, OFM-related features degrade gracefully.

### Testing

- `tests/unit/` — unit tests (mappers, no DB required)
- `tests/integration/` — integration tests using testcontainers (PostgreSQL + Redis containers)
- `tests/mocks/` — mock DAOs and holders for integration tests
- `tests/fixtures/` — test data and task fixtures
- Integration tests spin up real PostgreSQL and Redis containers via `testcontainers`

### Pre-commit Hooks

Runs black (line-length=79), isort (profile=black, line-length=79), flake8 (max-complexity=10, ignore W503/E203), and trailing-whitespace/end-of-file-fixer. Migrations directory is excluded from formatting.
