# Codebase Structure

**Analysis Date:** 2026-03-27

## Directory Layout

```
NutriTrack/
├── app/                    # Flask application package
│   ├── __init__.py         # Application factory (create_app)
│   ├── api_client.py       # Open Food Facts API wrapper
│   ├── calculator.py       # Pure BMR/TDEE/macro calculations
│   ├── forms.py            # WTForms form classes
│   ├── logging_config.py   # Logging setup
│   ├── models.py           # SQLAlchemy ORM models
│   ├── nutrition.py        # Pure nutrient scaling/summing
│   ├── routes.py           # All route handlers (single Blueprint)
│   ├── routes/             # Empty directory (unused legacy)
│   ├── static/             # Static assets
│   │   └── style.css       # Custom CSS (minimal, 18 lines)
│   └── templates/          # Jinja2 templates
│       ├── base.html       # Base layout with Bootstrap 5
│       ├── dashboard.html  # Main tracking dashboard
│       ├── food_form.html  # Add/edit food entry with search
│       ├── login.html      # Login page
│       ├── onboarding.html # Initial profile setup
│       ├── profile.html    # Edit profile
│       └── register.html   # Registration page
├── tests/                  # Test suite
│   ├── __init__.py         # Package marker
│   ├── conftest.py         # Pytest fixtures (app, client, auth_client)
│   ├── test_api_client.py  # API client unit tests
│   ├── test_auth.py        # Authentication route tests
│   ├── test_calculator.py  # Calculator unit tests
│   ├── test_integration.py # Integration tests (full request flows)
│   └── test_nutrition.py   # Nutrition module unit tests
├── docs/                   # Project documentation
│   ├── klassendiagramm.mmd         # Mermaid class diagram
│   └── sequenzdiagramm-ci.mmd      # Mermaid CI sequence diagram
├── instance/               # SQLite database directory (gitignored)
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI pipeline
├── .planning/              # GSD planning artifacts
├── config.py               # Config and TestConfig classes
├── run.py                  # Dev server entry point
├── wsgi.py                 # Production WSGI entry point
├── Procfile                # Heroku deployment config
├── pyproject.toml          # Black, Ruff, Mypy config
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Dev/test dependencies (includes runtime)
├── CLAUDE.md               # AI assistant instructions
└── .env.example            # Environment variable template
```

## Directory Purposes

**`app/`:**
- Purpose: All application source code
- Contains: Python modules (models, routes, forms, business logic, API client)
- Key files: `__init__.py` (factory), `routes.py` (all endpoints), `models.py` (schema)

**`app/templates/`:**
- Purpose: Jinja2 HTML templates
- Contains: 7 templates extending `base.html`
- Key files: `base.html` (layout), `dashboard.html` (main view), `food_form.html` (food entry with JS search)

**`app/static/`:**
- Purpose: Static assets served by Flask
- Contains: Single CSS file
- Key files: `style.css` (minimal custom overrides on top of Bootstrap)

**`app/routes/`:**
- Purpose: Empty legacy directory (routes are in `app/routes.py` not `app/routes/`)
- Contains: Only `__pycache__/`

**`tests/`:**
- Purpose: All test files
- Contains: conftest fixtures + 4 test modules
- Key files: `conftest.py` (app/client/auth_client fixtures)

**`docs/`:**
- Purpose: Mermaid diagrams for project documentation requirements
- Contains: Class diagram and CI sequence diagram

**`instance/`:**
- Purpose: SQLite database file storage
- Generated: Yes (by SQLAlchemy `db.create_all()`)
- Committed: No (gitignored)

## Key File Locations

**Entry Points:**
- `run.py`: Development server (`python run.py`)
- `wsgi.py`: Production WSGI app object for gunicorn
- `app/__init__.py`: Application factory `create_app()`

**Configuration:**
- `config.py`: `Config` (production) and `TestConfig` (testing) classes
- `pyproject.toml`: Black, Ruff, Mypy tool settings
- `.github/workflows/ci.yml`: CI pipeline definition
- `Procfile`: Heroku deployment command

**Core Logic:**
- `app/calculator.py`: BMR, TDEE, goal modifier, macro calculation (pure functions)
- `app/nutrition.py`: Nutrient scaling, daily summation, progress status (pure functions)
- `app/api_client.py`: Open Food Facts search wrapper

**Data Layer:**
- `app/models.py`: `User`, `UserProfile`, `DailyGoal`, `FoodEntry`
- `app/forms.py`: `LoginForm`, `RegisterForm`, `OnboardingForm`, `FoodEntryForm`, `DeleteForm`

**Routes:**
- `app/routes.py`: All route handlers on single `Blueprint("main", __name__)`

**Testing:**
- `tests/conftest.py`: Shared fixtures
- `tests/test_calculator.py`: Calculator unit tests
- `tests/test_nutrition.py`: Nutrition module unit tests
- `tests/test_api_client.py`: API client tests (with mocking)
- `tests/test_auth.py`: Auth route tests
- `tests/test_integration.py`: Full-flow integration tests

## Naming Conventions

**Files:**
- snake_case for all Python modules: `api_client.py`, `logging_config.py`
- snake_case for templates: `food_form.html`, `base.html`
- Single `routes.py` file (not split into route modules)

**Directories:**
- Lowercase: `app/`, `tests/`, `docs/`, `instance/`

**Test files:**
- `test_{module_name}.py` pattern matching the module under test

## Where to Add New Code

**New Route:**
- Add to `app/routes.py` on the existing `bp` Blueprint
- If routes.py grows too large, consider splitting into `app/routes/` package with sub-blueprints

**New Template:**
- Place in `app/templates/`
- Extend `base.html` with `{% extends "base.html" %}`
- Use `{% block title %}`, `{% block content %}`, `{% block scripts %}`

**New Model:**
- Add class to `app/models.py`
- Use `Mapped[]` type annotations with `mapped_column()`
- Schema auto-created by `db.create_all()` in factory

**New Form:**
- Add class to `app/forms.py`
- Extend `FlaskForm`
- Use WTForms validators

**New Business Logic (Pure Functions):**
- Add to `app/calculator.py` or `app/nutrition.py` depending on domain
- Keep zero Flask imports in these modules
- Or create new `app/{module}.py` for distinct domains

**New External API Integration:**
- Follow `app/api_client.py` pattern
- Use `requests` library
- Catch all exceptions, log errors, return safe defaults

**New Tests:**
- Place in `tests/test_{module}.py`
- Use fixtures from `tests/conftest.py` (`app`, `client`, `auth_client`)

**Static Assets:**
- Place in `app/static/`
- Reference via `url_for('static', filename='...')`

## Special Directories

**`instance/`:**
- Purpose: SQLite database file (`nutritrack.db`)
- Generated: Yes
- Committed: No

**`.planning/`:**
- Purpose: GSD workflow planning artifacts
- Generated: By Claude/GSD commands
- Committed: Yes

**`venv/`:**
- Purpose: Python virtual environment
- Generated: Yes
- Committed: No

**`.github/workflows/`:**
- Purpose: GitHub Actions CI configuration
- Generated: No
- Committed: Yes

---

*Structure analysis: 2026-03-27*
