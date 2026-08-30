# Oil Spill Detection & AIS Attribution Platform — Backend

FastAPI-based backend monolith utilizing PostGIS, OpenDrift/GNOME drift hindcasting, and AIS data correlation pipelines for ship attribution.

## Tech Stack
- **Framework:** FastAPI, Pydantic v2
- **Database & Geospatial:** PostgreSQL 16 + PostGIS, SQLAlchemy 2, GeoAlchemy2, Shapely, GeoPandas, PyProj
- **Authentication:** JWT, Argon2id
- **Containerization:** Docker & Docker Compose

## Getting Started

### Local Setup with Docker Compose
1. Ensure Docker and Docker Compose are installed.
2. Copy the environment file:
   ```bash
   cp .env.example .env
   ```
3. Boot the API and Database:
   ```bash
   docker compose up --build
   ```
4. Run migrations and seed fixtures:
   ```bash
   docker compose exec api python scripts/seed_fixtures.py
   ```
5. View API docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

### Local Dev Setup (Virtualenv)
If you prefer to run the API outside Docker:
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -e ".[dev]"
   ```
2. Make sure you have PostgreSQL with PostGIS extension installed and running, then apply migrations.
   ```bash
   alembic upgrade head
   ```
3. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Running Tests
To run the test suite:
```bash
pytest tests/ -v
```
