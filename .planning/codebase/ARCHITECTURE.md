# Architecture

**Analysis Date:** 2026-03-27

## Pattern Overview

**Overall:** Monolithic Flask application with Application Factory pattern

**Key Characteristics:**
- Single Flask Blueprint (`main`) handles all routes in `app/routes.py`
- Application Factory in `app/__init__.py` via `create_app(config_class)`
- Pure-function modules (`app/calculator.py`, `app/nutrition.py`) with zero Flask dependencies
- SQLAlchemy ORM models with `Mapped[]` type annotations
- Server-side rendering via Jinja2 templates with Bootstrap 5
- Flask-Login for session-based authentication

## Layers

**Presentation Layer (Templates):**
- Purpose: Server-rendered HTML UI
- Location: `app/templates/`
- Contains: Jinja2 templates extending `base.html`
- Depends on: Flask context variables, Bootstrap 5 CDN
- Used by: Route handlers via `render_template()`

**Route Layer (Controllers):**
- Purpose: HTTP request handling, form processing, redirects
- Location: `app/routes.py`
- Contains: All route definitions on a single `Blueprint("main", __name__)`
- Depends on: Models, Forms, Calculator, Nutrition, API Client
- Used by: Flask URL dispatcher

**Form Layer:**
- Purpose: Input validation, CSRF protection
- Location: `app/forms.py`
- Contains: `FlaskForm` subclasses (`LoginForm`, `RegisterForm`, `OnboardingForm`, `FoodEntryForm`, `DeleteForm`)
- Depends on: Flask-WTF, WTForms validators
- Used by: Route handlers

**Model Layer (ORM):**
- Purpose: Database schema and data access
- Location: `app/models.py`
- Contains: `User`, `UserProfile`, `DailyGoal`, `FoodEntry` models
- Depends on: Flask-SQLAlchemy, SQLAlchemy `Mapped[]`
- Used by: Route handlers via `db.session`

**Business Logic Layer:**
- Purpose: Pure calculation functions with no framework dependencies
- Location: `app/calculator.py` (BMR, TDEE, macros), `app/nutrition.py` (scaling, summation, status)
- Contains: Stateless functions operating on primitive types
- Depends on: Nothing (no imports from Flask or app)
- Used by: Route handlers in `app/routes.py`

**External API Layer:**
- Purpose: Open Food Facts product search
- Location: `app/api_client.py`
- Contains: `search_food()`, `_fetch_products()`, `_extract_name()`, `APIError`
- Depends on: `requests` library
- Used by: `/api/food-search` route in `app/routes.py`

**Configuration Layer:**
- Purpose: App settings and environment binding
- Location: `config.py` (root)
- Contains: `Config` and `TestConfig` classes
- Depends on: `os.environ`
- Used by: `create_app()` in `app/__init__.py`

## Data Flow

**Onboarding/Profile Update:**

1. User submits `OnboardingForm` via POST to `/onboarding` or `/profile`
2. Route handler calls `_save_profile_and_goals(form)` in `app/routes.py`
3. Helper creates/updates `UserProfile` in DB
4. Helper calls `calculate_bmr()` -> `calculate_tdee()` -> `apply_goal_modifier()` -> `calculate_macros()` from `app/calculator.py`
5. Helper creates/updates `DailyGoal` for today
6. Redirect to `/dashboard`

**Food Tracking:**

1. User searches food via `/api/food-search?q=...` (AJAX from `food_form.html`)
2. `search_food()` in `app/api_client.py` queries Open Food Facts, returns JSON
3. Client-side JS auto-fills form fields from selected result
4. User submits `FoodEntryForm` via POST to `/food/add`
5. Route handler creates `FoodEntry` in DB
6. Redirect to `/dashboard`

**Dashboard Rendering:**

1. GET `/dashboard` (optional `?date=YYYY-MM-DD`)
2. Load `UserProfile`, `DailyGoal` (always today's), `FoodEntry` list for display date
3. Call `scale_nutrients()` for each entry, then `sum_daily_nutrients()` from `app/nutrition.py`
4. Call `progress_status()` to compute traffic-light colors
5. Compute remaining amounts and percentages inline in route handler
6. Render `dashboard.html` with all computed data

**Authentication:**

1. Register: POST `/register` -> create `User` with hashed password -> auto-login -> redirect `/onboarding`
2. Login: POST `/login` -> verify password hash -> `login_user()` -> redirect to index
3. All app routes decorated with `@login_required`

**State Management:**
- Server-side sessions via Flask-Login (session cookie)
- All state persisted in SQLite via SQLAlchemy ORM
- No client-side state management

## Key Abstractions

**User Profile + Daily Goal:**
- Purpose: Separate user identity from nutritional profile and calculated goals
- Examples: `app/models.py` (`User`, `UserProfile`, `DailyGoal`)
- Pattern: One-to-many from `User` to `UserProfile` and `DailyGoal` (via `user_id` FK), though ORM relationships are not declared (raw FK queries used)

**Per-100g Nutrient Storage:**
- Purpose: Store food nutrition data normalized to 100g, scale at display time
- Examples: `app/models.py` `FoodEntry` columns (`calories_per_100g`, etc.)
- Pattern: Raw values stored; `app/nutrition.py` `scale_nutrients()` computes actual intake

**Traffic-Light Status:**
- Purpose: Visual feedback on goal progress (green/red/neutral)
- Examples: `app/nutrition.py` `progress_status()`
- Pattern: Returns Bootstrap class strings (`""`, `"success"`, `"danger"`) based on actual/goal ratio thresholds (< 90%, 90-100%, > 100%)

## Entry Points

**Development Server:**
- Location: `run.py`
- Triggers: `python run.py`
- Responsibilities: Creates app via factory, runs with `debug=True`

**Production Server:**
- Location: `wsgi.py`
- Triggers: `gunicorn wsgi:app` (via `Procfile`)
- Responsibilities: Creates app via factory, exposes `app` for WSGI

**Application Factory:**
- Location: `app/__init__.py` `create_app(config_class)`
- Triggers: Called by `run.py`, `wsgi.py`, and test fixtures
- Responsibilities: Initializes Flask app, extensions (SQLAlchemy, LoginManager, logging), registers blueprint, creates DB tables

## Error Handling

**Strategy:** Flash messages for user-facing errors; Python logging for system errors

**Patterns:**
- Form validation errors surfaced via WTForms validators and flash messages
- API errors (`app/api_client.py`): All exceptions caught, logged, empty list returned (never raises to caller)
- Missing profile: Redirects to `/onboarding`
- Missing food entry (edit/delete): Flash warning + redirect to dashboard
- Invalid date param: Falls back to `date.today()`
- Duplicate username on register: Flash "Benutzername bereits vergeben"

## Cross-Cutting Concerns

**Logging:** Python `logging` module, `"nutritrack"` logger, INFO level, StreamHandler configured in `app/logging_config.py`

**Validation:** Flask-WTF forms with WTForms validators (`DataRequired`, `Length`, `NumberRange`, `EqualTo`). CSRF enabled for all forms (disabled in `TestConfig`).

**Authentication:** Flask-Login with `@login_required` on all app routes. Password hashing via Werkzeug. User loader via `db.session.get(User, int(user_id))`.

---

*Architecture analysis: 2026-03-27*
