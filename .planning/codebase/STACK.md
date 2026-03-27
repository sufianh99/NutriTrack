# Technology Stack

**Analysis Date:** 2026-03-27

## Languages

**Primary:**
- Python 3.14 (venv runtime) / CI targets 3.12 - All application code

**Secondary:**
- HTML (Jinja2 templates) - Server-rendered UI in `app/templates/`
- CSS - Minimal custom styles in `app/static/style.css`
- JavaScript - Inline in `app/templates/food_form.html` for Open Food Facts search autocomplete

## Runtime

**Environment:**
- Python 3.14 (local venv at `venv/`)
- Python 3.12 (CI via `actions/setup-python@v5` in `.github/workflows/ci.yml`)

**Package Manager:**
- pip
- Lockfile: missing (no `requirements.lock` or `pip-tools` constraints file)

## Frameworks

**Core:**
- Flask 3.1.3 - Web framework (`requirements.txt`)
- Flask-SQLAlchemy 3.1.1 - ORM integration (`requirements.txt`)
- Flask-WTF 1.2.2 - Form handling and CSRF protection (`requirements.txt`)
- Flask-Login 0.6.3 - Authentication session management (`requirements.txt`)

**Testing:**
- pytest 9.0.2 - Test runner (`requirements-dev.txt`)
- pytest-flask 1.3.0 - Flask test fixtures (`requirements-dev.txt`)

**Build/Dev:**
- Black 26.3.1 - Code formatter (`requirements-dev.txt`)
- Ruff 0.15.7 - Linter (`requirements-dev.txt`)
- Mypy 1.19.1 - Static type checker (`requirements-dev.txt`)

## Key Dependencies

**Critical:**
- SQLAlchemy 2.0.48 (transitive via Flask-SQLAlchemy) - ORM with `Mapped[]` type annotations
- Werkzeug 3.1.3 (transitive via Flask) - WSGI utilities, password hashing
- requests 2.32.5 - HTTP client for Open Food Facts API calls in `app/api_client.py`
- openfoodfacts 5.0.1 - Listed in `requirements.txt` but NOT currently imported; `app/api_client.py` uses raw `requests` instead

**Infrastructure:**
- gunicorn 23.0.0 - Production WSGI server (`Procfile`: `web: gunicorn wsgi:app`)
- python-dotenv 1.2.2 - Environment variable loading

**Transitive (notable):**
- Jinja2 3.1.6 - Template engine (via Flask)
- WTForms 3.2.1 - Form fields and validators (via Flask-WTF)
- itsdangerous 2.2.0 - Session signing (via Flask)

## Configuration

**Environment:**
- `.env.example` present (do not read contents)
- `config.py` defines `Config` and `TestConfig` classes
- `SECRET_KEY` from env var with dev fallback
- `DATABASE_URL` from env var, defaults to `sqlite:///instance/nutritrack.db`
- `SQLALCHEMY_TRACK_MODIFICATIONS = False`

**Build:**
- `pyproject.toml` - Black (`line-length = 88`), Ruff (`select = ["E", "F", "I", "W"]`), Mypy (`ignore_missing_imports`, `disallow_untyped_defs`)
- `.github/workflows/ci.yml` - CI pipeline definition
- `Procfile` - Heroku/PaaS deployment

**Test:**
- `config.py` `TestConfig` - `TESTING=True`, in-memory SQLite, CSRF disabled

## Platform Requirements

**Development:**
- Python 3.12+ (3.14 used locally)
- `pip install -r requirements-dev.txt`
- Run: `python run.py` (debug mode)

**Production:**
- Heroku-compatible PaaS (Procfile with gunicorn)
- Environment variables: `SECRET_KEY`, optionally `DATABASE_URL`
- SQLite file storage at `instance/nutritrack.db`

---

*Stack analysis: 2026-03-27*
