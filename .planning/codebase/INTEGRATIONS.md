# External Integrations

**Analysis Date:** 2026-03-27

## APIs & External Services

**Food Data:**
- Open Food Facts - Product search and nutrition data lookup
  - Client: Raw `requests` library in `app/api_client.py` (NOT the `openfoodfacts` SDK despite it being in `requirements.txt`)
  - Primary URL: `https://search.openfoodfacts.org/search` (Elasticsearch proxy)
  - Fallback URL: `https://world.openfoodfacts.org/api/v2/search`
  - Auth: None (public API)
  - User-Agent: `NutriTrack/1.0`
  - Timeout: 8 seconds
  - Rate limiting: Not implemented client-side
  - Error handling: All exceptions caught and logged; returns empty list on failure

**CDN:**
- Bootstrap 5.3.3 - CSS and JS loaded from `cdn.jsdelivr.net` in `app/templates/base.html`
  - CSS: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css`
  - JS: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js`

## Data Storage

**Databases:**
- SQLite (stdlib)
  - Connection: `DATABASE_URL` env var, default `sqlite:///instance/nutritrack.db`
  - Client: Flask-SQLAlchemy / SQLAlchemy 2.x with `Mapped[]` column types
  - Schema: Auto-created via `db.create_all()` in `app/__init__.py`
  - Tables: `user`, `user_profile`, `daily_goal`, `food_entry` (defined in `app/models.py`)

**File Storage:**
- Local filesystem only (`instance/` directory for SQLite DB)

**Caching:**
- None

## Authentication & Identity

**Auth Provider:**
- Custom (Flask-Login)
  - Implementation: Username/password with Werkzeug `generate_password_hash` / `check_password_hash`
  - Session management: Flask-Login `LoginManager` in `app/__init__.py`
  - User loader: `db.session.get(User, int(user_id))` in `app/__init__.py`
  - Login view: `main.login`
  - All app routes (except `/register`, `/login`, `/health`) require `@login_required`

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry or similar)

**Logs:**
- Python `logging` module via custom `app/logging_config.py`
- Logger name: `"nutritrack"`
- Level: INFO
- Format: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`
- Output: StreamHandler (stdout/stderr)
- Events logged: user register, login, logout, profile save, food entry add/update/delete, API errors

## CI/CD & Deployment

**Hosting:**
- Heroku-compatible PaaS (Procfile: `web: gunicorn wsgi:app`)

**CI Pipeline:**
- GitHub Actions (`.github/workflows/ci.yml`)
- Trigger: push/PR to `main` branch
- Runner: `ubuntu-latest`
- Python: 3.12
- Steps (in order):
  1. `black --check .` - Format check
  2. `ruff check .` - Lint
  3. `mypy app/` - Type check
  4. `pytest tests/ -v --tb=short` - Tests

## Environment Configuration

**Required env vars:**
- `SECRET_KEY` - Flask session signing (has dev fallback in `config.py`)
- `DATABASE_URL` - Database connection string (optional, defaults to local SQLite)

**Secrets location:**
- `.env.example` present as template
- No secrets management service

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Health Check

- `GET /health` returns `{"status": "ok"}` with HTTP 200 (`app/routes.py` line 94-97)

---

*Integration audit: 2026-03-27*
