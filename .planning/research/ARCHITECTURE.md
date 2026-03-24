# Architecture Patterns

**Domain:** Flask nutrition tracking web app (single-user, no auth)
**Researched:** 2026-03-24
**Context:** Brownfield — existing Flask app with auth scaffolding must be restructured to match project spec

---

## Recommended Architecture

Flat module layout inside `app/`, single Blueprint (or no blueprint), pure-Python business logic
modules that routes delegate to. No auth layer. No service layer abstraction beyond what the
project spec defines.

```
nutritrack/
├── app/
│   ├── __init__.py          # App factory — creates Flask app, registers blueprint, inits DB
│   ├── models.py            # SQLAlchemy models: UserProfile, FoodEntry, DailyGoal, FoodsCache
│   ├── routes.py            # Single blueprint: onboarding, dashboard, food CRUD, history
│   ├── calculator.py        # Pure functions — BMR/TDEE, macro split, goal modifier
│   ├── nutrition.py         # Pure functions — portion scaling, daily summation, status labels
│   ├── api_client.py        # Open Food Facts wrapper — search, fetch, normalize response
│   └── templates/
│       ├── base.html
│       ├── onboarding.html
│       ├── dashboard.html
│       ├── add_food.html
│       └── history.html
├── tests/
│   ├── test_calculator.py   # Unit tests for BMR, TDEE, macros, goal modifier
│   ├── test_nutrition.py    # Unit tests for portion scaling, daily sum
│   ├── test_status.py       # Unit tests for progress status/color logic
│   └── test_integration.py  # Flask test client — routes, DB round-trips
├── .github/
│   └── workflows/
│       └── ci.yml
├── config.py
├── requirements.txt
└── run.py
```

---

## Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| `__init__.py` (app factory) | Create Flask app, init SQLAlchemy, register blueprint | `models.py`, `routes.py`, `config.py` |
| `models.py` | SQLAlchemy schema — UserProfile, FoodEntry, DailyGoal, FoodsCache | `routes.py` (reads/writes), `__init__.py` (db object) |
| `routes.py` | HTTP layer — validate form input, call business logic, render templates | `models.py`, `calculator.py`, `nutrition.py`, `api_client.py`, templates |
| `calculator.py` | BMR/TDEE calculation, PAL factor application, goal modifier, macro split | No dependencies (pure functions, plain Python) |
| `nutrition.py` | Portion-scale raw per-100g values, sum daily entries, derive progress status (normal/green/orange-red) | No dependencies (pure functions, plain Python) |
| `api_client.py` | Search Open Food Facts by name, fetch by barcode, normalize response to internal dict | External HTTP only — no DB, no Flask context |
| `templates/` | Jinja2 HTML rendering — consume context variables passed by routes | Rendered by `routes.py` only |
| `tests/` | pytest suites — unit (calculator, nutrition, status) + integration (Flask test client) | `calculator.py`, `nutrition.py`, `routes.py` via Flask test client |

### Strict boundaries

- `calculator.py` and `nutrition.py` are import-only modules: no Flask imports, no DB imports, no side effects. This is what makes them unit-testable without an app context.
- `api_client.py` is stateless. It receives a query string, returns a normalized dict or raises an exception. No caching logic in this module — the optional `FoodsCache` table is populated by routes.
- `routes.py` is the only module allowed to touch `db.session`. Models are data containers; business logic lives in calculator/nutrition modules.

---

## Data Models (Target)

### UserProfile
Replaces the current auth-coupled `User` model. Stores body data and computed goal.
Single row (single-user app — no user_id FK needed on other tables, or use a constant id=1).

| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER PK | Always 1 in single-user mode |
| name | TEXT | Display name |
| age | INTEGER | For BMR formula |
| height_cm | FLOAT | For BMR formula |
| weight_kg | FLOAT | Current weight |
| gender | TEXT | 'male' / 'female' |
| activity_level | TEXT | 'sedentary' / 'light' / 'moderate' / 'active' / 'very_active' |
| goal | TEXT | 'lose' / 'maintain' / 'gain' |

### DailyGoal
Stores computed goals per day. Recalculated and upserted on profile save.

| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER PK | |
| date | DATE | Date the goals apply to |
| calorie_goal | FLOAT | kcal target |
| protein_goal | FLOAT | g target |
| fat_goal | FLOAT | g target |
| carb_goal | FLOAT | g target |

### FoodEntry
Replaces current `Meal` model. Stores per-entry nutrition values scaled to actual portion.

| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER PK | |
| date | DATE | Entry date (not datetime — day-level tracking) |
| food_name | TEXT | Display name |
| amount_g | FLOAT | Actual portion in grams |
| calories | FLOAT | Scaled to amount_g |
| protein | FLOAT | Scaled to amount_g |
| fat | FLOAT | Scaled to amount_g |
| carbs | FLOAT | Scaled to amount_g |

### FoodsCache (optional)
Local cache of Open Food Facts results to avoid repeated API calls.

| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER PK | |
| name | TEXT | Product name |
| kcal_per_100g | FLOAT | Base value |
| protein_per_100g | FLOAT | Base value |
| fat_per_100g | FLOAT | Base value |
| carbs_per_100g | FLOAT | Base value |

---

## Data Flow

### Flow 1: Onboarding / Profile Save

```
User submits onboarding form
  → routes.py validates form input
  → routes.py calls calculator.calculate_bmr(weight, height, age, gender)
  → routes.py calls calculator.calculate_tdee(bmr, activity_level)
  → routes.py calls calculator.apply_goal_modifier(tdee, goal)
  → routes.py calls calculator.calculate_macros(calorie_goal)
  → routes.py upserts UserProfile in DB
  → routes.py upserts DailyGoal for today in DB
  → redirect to dashboard
```

### Flow 2: Food Entry (Manual)

```
User submits add_food form (name, amount_g, kcal_per_100g, protein, fat, carbs)
  → routes.py validates form input
  → routes.py calls nutrition.scale_to_portion(per_100g_values, amount_g)
  → routes.py creates FoodEntry record with scaled values
  → db.session.add + commit
  → redirect to dashboard
```

### Flow 3: Food Search via API

```
User types food name in search field
  → routes.py calls api_client.search(query)
  → api_client sends GET request to Open Food Facts search endpoint
  → api_client normalizes response → list of dicts with per_100g values
  → routes.py renders results; user selects one
  → (optionally) routes.py caches result to FoodsCache
  → Flow 2 continues (pre-filled form or direct save)
```

### Flow 4: Dashboard Render

```
GET /dashboard
  → routes.py loads DailyGoal for today (or recalculates if missing)
  → routes.py queries FoodEntry WHERE date = today
  → routes.py calls nutrition.sum_daily(entries) → totals dict
  → routes.py calls nutrition.progress_status(totals, goals) → status dict with colors
  → render_template("dashboard.html", goals=..., totals=..., status=...)
  → Jinja2 renders progress bars with Bootstrap color classes
```

### Flow 5: History View

```
GET /history?date=YYYY-MM-DD
  → routes.py queries FoodEntry WHERE date = requested_date
  → routes.py loads DailyGoal for that date (if exists)
  → routes.py calls nutrition.sum_daily(entries)
  → render_template("history.html", ...)
```

---

## Calculation Logic (business rules in calculator.py)

### Mifflin-St-Jeor BMR
```python
# Male:   (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
# Female: (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
```

### PAL Activity Factors
```python
PAL_FACTORS = {
    "sedentary":   1.200,
    "light":       1.375,
    "moderate":    1.550,
    "active":      1.725,
    "very_active": 1.900,
}
# TDEE = BMR * PAL_FACTORS[activity_level]
```

### Goal Modifier
```python
GOAL_MODIFIERS = {
    "lose":     0.85,  # -15%
    "maintain": 1.00,
    "gain":     1.10,  # +10%
}
# calorie_goal = TDEE * GOAL_MODIFIERS[goal]
```

### Macro Split (25/30/45)
```python
# protein_goal_g = (calorie_goal * 0.25) / 4
# fat_goal_g     = (calorie_goal * 0.30) / 9
# carb_goal_g    = (calorie_goal * 0.45) / 4
```

### Portion Scaling (in nutrition.py)
```python
# scaled_value = (per_100g_value / 100.0) * amount_g
```

### Progress Status (in nutrition.py)
```python
# ratio = actual / goal
# < 0.95 → "normal" (Bootstrap default/blue)
# 0.95–1.05 → "success" (green)
# > 1.05 → "warning" or "danger" (orange-red)
```

---

## Patterns to Follow

### Pattern 1: App Factory with Single Blueprint
**What:** `create_app()` in `__init__.py` constructs and configures the Flask app. One blueprint handles all routes (no separate auth blueprint).
**When:** Always — enables pytest to create isolated app instances with test config.
**Example:**
```python
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    from app import routes
    app.register_blueprint(routes.bp)
    with app.app_context():
        db.create_all()
    return app
```

### Pattern 2: Pure-Function Business Logic Modules
**What:** `calculator.py` and `nutrition.py` contain only plain Python functions with no Flask or SQLAlchemy imports.
**When:** All calculation and transformation logic — never inline in route handlers.
**Why:** Directly testable with `pytest` without an app context. Type-checkable with Mypy. Formattable with Black/Ruff without import side effects.

### Pattern 3: Single-User Singleton via Constant ID
**What:** The app is single-user. UserProfile always has id=1. Routes check `UserProfile.query.get(1)`; if None, redirect to onboarding.
**When:** Every route that depends on a configured profile.
**Example:**
```python
profile = db.session.get(UserProfile, 1)
if profile is None:
    return redirect(url_for("main.onboarding"))
```

### Pattern 4: Date-Based Querying for Dashboard and History
**What:** FoodEntry rows are queried by `date` (Python `datetime.date`) not by `datetime`. This allows simple `WHERE date = today` queries and makes the history feature trivial.
**When:** All FoodEntry inserts and dashboard/history queries.

### Pattern 5: api_client Returns Normalized Dicts
**What:** `api_client.search(query)` returns `List[dict]` with keys `name`, `kcal_per_100g`, `protein_per_100g`, `fat_per_100g`, `carbs_per_100g`. If the API call fails (timeout, 404, malformed response), it raises a custom `APIError` exception — routes catch it and flash a user-friendly message.
**When:** Open Food Facts integration.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Business Logic in Route Handlers
**What:** Embedding BMR/TDEE calculation or macro splitting directly inside route functions.
**Why bad:** Cannot be unit-tested without a Flask request context. Duplicated if reused. Blocks Mypy type coverage.
**Instead:** Route handler calls `calculator.calculate_bmr(...)` and uses the return value.

### Anti-Pattern 2: Flask-Login / Auth Decorators
**What:** `@login_required` or `current_user` references anywhere in the codebase.
**Why bad:** The project spec explicitly excludes auth. These decorators will block all routes and cause test failures.
**Instead:** Replace with a simple `profile = db.session.get(UserProfile, 1); if not profile: redirect(onboarding)` guard.

### Anti-Pattern 3: user_id Foreign Keys on FoodEntry and DailyGoal
**What:** Carrying over the multi-user FK pattern from the existing `Meal` model.
**Why bad:** Adds unnecessary complexity. There is no User table in the target architecture (only UserProfile with a single row).
**Instead:** Omit user_id. Optionally keep it as a constant if the schema demands a FK, but single-row join is simpler.

### Anti-Pattern 4: Storing Nutrition Data Unscaled
**What:** Storing `kcal_per_100g` in FoodEntry and computing the scaled value at query time in templates.
**Why bad:** Jinja2 templates should not contain arithmetic. The `nutrition.py` module is where scaling happens.
**Instead:** Scale at write time in the route before inserting into the DB. Store final `calories`, `protein`, `fat`, `carbs` values.

### Anti-Pattern 5: Direct `requests` Calls Inside Routes
**What:** Calling `requests.get("https://world.openfoodfacts.org/...")` directly in a route function.
**Why bad:** Cannot be mocked for tests without monkeypatching routes. Mixes HTTP concerns with request handling.
**Instead:** Wrap in `api_client.py` with a well-defined interface. Tests mock `api_client.search`.

---

## Suggested Build Order

Dependencies flow upward — each layer must exist before the layer above it can be built.

```
Layer 0 (No dependencies):
  calculator.py      ← pure functions, no imports
  nutrition.py       ← pure functions, no imports

Layer 1 (Depends on Layer 0):
  tests/test_calculator.py   ← import calculator, run immediately
  tests/test_nutrition.py    ← import nutrition, run immediately
  tests/test_status.py       ← import nutrition.progress_status

Layer 2 (Depends on Flask + SQLAlchemy setup):
  config.py          ← constants only
  app/__init__.py    ← app factory, db object
  app/models.py      ← SQLAlchemy schema

Layer 3 (Depends on Layers 0+2):
  app/routes.py      ← calls calculator, nutrition, reads/writes models
  app/templates/     ← consumes route context

Layer 4 (Depends on Layer 3):
  tests/test_integration.py  ← Flask test client, requires running app

Layer 5 (Depends on Layer 3, optional):
  app/api_client.py  ← standalone HTTP wrapper, plugged into routes
  app/models.py      ← add FoodsCache table when api_client lands
```

**Implication for sprint phases:**
- Sprint 1: Layers 0 + 1 + 2 (calculator, models, unit tests). Auth removal happens here.
- Sprint 2: Layer 3 (routes, templates, dashboard). Integration tests.
- Sprint 3: CI/CD pipeline validates all layers.
- Sprint 4: Layer 5 (api_client, FoodsCache).

---

## Refactoring: Current → Target

The existing codebase must be restructured. Key deltas:

| Current | Target | Action |
|---------|--------|--------|
| `app/routes/auth.py` (Blueprint) | Deleted | Remove entirely |
| `app/routes/main.py` + `app/routes/tracking.py` | `app/routes.py` (single file) | Merge, remove login_required, add profile guard |
| `app/models.py` (User + Meal + WeightLog) | `app/models.py` (UserProfile + FoodEntry + DailyGoal + FoodsCache) | Redesign; remove UserMixin, login_manager |
| `app/forms.py` (RegistrationForm, LoginForm + tracking forms) | `app/forms.py` (ProfileForm, FoodEntryForm only) | Remove auth forms |
| `app/__init__.py` (login_manager) | `app/__init__.py` (no login_manager) | Remove Flask-Login init |
| No calculator module | `app/calculator.py` | Create new |
| No nutrition module | `app/nutrition.py` | Create new |
| No api_client module | `app/api_client.py` | Create new (Sprint 4) |
| No tests | `tests/` directory | Create new |
| No CI | `.github/workflows/ci.yml` | Create new (Sprint 3) |

---

## Scalability Considerations

This is an academic single-user project. Scalability is not a goal. Document for completeness:

| Concern | Single user (current scope) | If multi-user later |
|---------|----------------------------|---------------------|
| Data isolation | Not needed — one UserProfile row | Add user_id FK back to FoodEntry and DailyGoal |
| Auth | Removed per spec | Re-add Flask-Login or Flask-JWT |
| Database | SQLite is fine | Swap to PostgreSQL via DATABASE_URL env var (SQLAlchemy handles this) |
| Concurrency | Not applicable | SQLite WAL mode or migrate to PostgreSQL |

---

## Sources

- Project specification: `nutritrack-projektdoku.md` (sections 7, 8, 9) — HIGH confidence
- Existing codebase: `app/__init__.py`, `app/models.py`, `app/routes/` — HIGH confidence (direct inspection)
- Mifflin-St-Jeor formula constants: [NCI/DCCPS REE-PAL reference](https://cancercontrol.cancer.gov/brp/research/group-evaluated-measures/adopt/ree-pal) — HIGH confidence
- Open Food Facts Python SDK: [openfoodfacts on PyPI](https://pypi.org/project/openfoodfacts/) and [GitHub](https://github.com/openfoodfacts/openfoodfacts-python) — MEDIUM confidence (SDK approach is optional; direct `requests` to REST API is equally valid)
- Flask application factory pattern: [Flask official patterns docs](https://flask.palletsprojects.com/en/stable/patterns/) — HIGH confidence
- Flask large-app structure: [Miguel Grinberg Mega-Tutorial Part XV](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure) — MEDIUM confidence
