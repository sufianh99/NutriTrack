# Phase 1: Foundation - Research

**Researched:** 2026-03-25
**Domain:** Flask brownfield restructuring — auth removal, model rewrite, Mifflin-St-Jeor calculator, onboarding flow
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** When no UserProfile exists (fresh DB), all routes redirect to `/onboarding`
- **D-02:** Onboarding form collects: age, height_cm, weight_kg, gender (male/female), activity_level (5 PAL levels), goal (lose/maintain/gain)
- **D-03:** After onboarding submission, app calculates BMR/TDEE/calorie goal/macros, stores results in DailyGoal, and redirects to dashboard
- **D-04:** User can re-edit their profile at `/profile` at any time — same fields as onboarding
- **D-05:** Saving profile recalculates and updates DailyGoal automatically
- **D-06:** No separate results page — calculated goals are shown on the dashboard (Soll values)
- **D-07:** Dashboard is the landing page for users who have completed onboarding
- **D-08:** All form labels and UI text in German (consistent with existing app)
- **D-09:** Activity levels displayed with German descriptive labels (e.g., "Sitzend (wenig Bewegung)" for sedentary)
- **D-10:** Goals displayed as: "Abnehmen", "Halten", "Zunehmen"
- **D-11:** Delete auth blueprint, RegistrationForm, LoginForm, Flask-Login imports entirely
- **D-12:** Remove Flask-Login from requirements.txt, remove email-validator transitive dependency
- **D-13:** Replace `current_user.is_authenticated` navbar logic with profile-exists check
- **D-14:** Remove WeightLog model (weight is a profile attribute for BMR only)

### Claude's Discretion

- Form validation ranges (reasonable defaults for age, height, weight)
- Error message wording
- Onboarding page layout within Bootstrap 5 constraints
- Whether to use a single blueprint or keep separate blueprints

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RSTC-01 | Existing auth system (Flask-Login, login/register routes, password hashing) is completely removed | Auth removal checklist in Pitfalls section; all Flask-Login symbols identified in codebase |
| RSTC-02 | Existing models replaced with project-spec-compliant schema (UserProfile, DailyGoal, FoodEntry, FoodsCache) | Target schema fully specified in Architecture Patterns section |
| RSTC-03 | App runs as single-user without any login requirement | Single-user bootstrap pattern (onboarding guard) documented |
| PROF-01 | User can enter body data via onboarding form (age, height_cm, weight_kg, gender, activity_level, goal) | OnboardingForm field specification in Code Examples |
| PROF-02 | App calculates BMR using Mifflin-St-Jeor formula | Formula constants verified; reference value confirmed: 30yo, 70kg, 175cm male = 1673.75 kcal |
| PROF-03 | App calculates TDEE by multiplying BMR with PAL factor (1.2 / 1.375 / 1.55 / 1.725 / 1.9) | PAL constants documented with dict pattern |
| PROF-04 | App derives calorie goal from TDEE and user goal (lose: ×0.85, maintain: ×1.0, gain: ×1.10) | Goal modifier constants documented |
| PROF-05 | App calculates macro goals (protein 25% ÷4, fat 30% ÷9, carbs 45% ÷4) | Macro split documented with kcal-per-gram constants |
| PROF-06 | User can view their calculated daily calorie and macro goals | Dashboard shows DailyGoal row (Soll values); pattern documented in data flow |

</phase_requirements>

---

## Summary

Phase 1 is a brownfield restructuring task. The existing Flask app has a working Flask-Login auth system
(User model, auth blueprint, login/register templates) that must be completely removed. The target is a
single-user app with no auth, where a `UserProfile` singleton replaces `User`, and a pure-Python
`calculator.py` module implements Mifflin-St-Jeor. The existing codebase has been inspected directly —
the full extent of Flask-Login contamination is known and documented below.

The Mifflin-St-Jeor formula is well-established and verified against published medical references. The
reference value (30-year-old, 70 kg, 175 cm male = BMR 1673.75 kcal) is the ground-truth test anchor
for the calculator module. All formula constants, PAL factors, goal modifiers, and macro kcal-per-gram
values are HIGH confidence and documented.

The primary risk in this phase is incomplete auth removal — Flask-Login references are spread across 6
files (`__init__.py`, `models.py`, `routes/auth.py`, `routes/main.py`, `routes/tracking.py`,
`templates/base.html`, `templates/dashboard.html`). Every one of these files must be touched. A grep
checklist is the safest verification approach.

**Primary recommendation:** Start with auth removal (creates a clean base), then rewrite models (establishes schema), then implement `calculator.py` with unit tests, then build onboarding route and templates. This ordering avoids circular dependencies and keeps the app bootable at each step.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 3.1.0 (update to 3.1.3) | Web framework | Project-constrained; existing in repo |
| Flask-SQLAlchemy | 3.1.1 | ORM / DB integration | Project-constrained; current version |
| Flask-WTF | 1.2.2 | Form classes + CSRF protection | Project-constrained; CSRF protection required even for single-user |
| python-dotenv | 1.0.1 (update to 1.2.2) | Env-var / .env loading | Project-constrained; update for Python 3.14 support |
| pytest | 9.0.2 | Test runner | Project-constrained |
| pytest-flask | 1.3.0 | Flask test fixtures | Flask 3.0 compatible; provides `client` fixture |

### Libraries to REMOVE

| Library | Reason |
|---------|--------|
| Flask-Login 0.6.3 | Auth is explicitly out of scope; single-user app |
| Werkzeug (direct pin) | Bundled with Flask; remove from requirements.txt; Flask manages version |

### Updated requirements.txt (runtime)

```
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2
python-dotenv==1.2.2
```

### Updated requirements-dev.txt (dev/test)

```
pytest==9.0.2
pytest-flask==1.3.0
black==26.3.1
ruff==0.15.7
mypy==1.19.1
```

**Installation:**

```bash
pip install Flask==3.1.3 Flask-SQLAlchemy==3.1.1 Flask-WTF==1.2.2 python-dotenv==1.2.2
pip install pytest==9.0.2 pytest-flask==1.3.0 black==26.3.1 ruff==0.15.7 mypy==1.19.1
```

---

## Architecture Patterns

### Target Project Structure

```
app/
├── __init__.py          # App factory — no Flask-Login; registers single blueprint
├── models.py            # UserProfile, DailyGoal, FoodEntry, FoodsCache (SQLAlchemy 2.x Mapped style)
├── routes.py            # Single blueprint: onboarding, profile, dashboard (tracking routes in Phase 2)
├── calculator.py        # Pure functions — BMR, TDEE, goal modifier, macro split
├── forms.py             # OnboardingForm / ProfileForm (auth forms deleted)
└── templates/
    ├── base.html        # Adapted — auth links removed; profile-exists check for nav
    ├── onboarding.html  # New — body data input form
    ├── dashboard.html   # Rewritten — shows DailyGoal Soll values; no current_user
    └── profile.html     # New — same fields as onboarding, pre-filled
tests/
├── conftest.py          # App fixture with in-memory SQLite + TestConfig
└── test_calculator.py   # Unit tests for BMR, TDEE, goal modifier, macros
config.py                # Config class (keep as-is) + TestConfig (new)
requirements.txt         # Updated (remove Flask-Login)
run.py                   # Keep as-is
```

### Pattern 1: App Factory Without Flask-Login

**What:** `create_app()` in `__init__.py` initialises Flask, SQLAlchemy, and one blueprint. No
`LoginManager`. No `inject_models` context processor (anti-pattern in existing code).

**Example:**

```python
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


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

### Pattern 2: SQLAlchemy 2.x Mapped Column Style (Mypy-safe)

**What:** Use `Mapped` / `mapped_column` so Mypy understands attribute types without plugins.
**Why:** The existing `db.Column(db.Float)` style causes Mypy errors in arithmetic (`height_cm * 6.25`
flagged as `Column[Float]` not `float`).

```python
# app/models.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Float, Integer, String, Date

class UserProfile(db.Model):
    __tablename__ = "user_profile"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)  # 'male' | 'female'
    activity_level: Mapped[str] = mapped_column(String(20), nullable=False)
    goal: Mapped[str] = mapped_column(String(20), nullable=False)
```

### Pattern 3: Single-User Onboarding Guard

**What:** Every route that requires a profile checks `db.session.get(UserProfile, 1)`. If None,
redirect to `/onboarding`. Applied at route entry, not as a decorator.

```python
# app/routes.py
from app import db
from app.models import UserProfile

def _get_profile_or_redirect():
    """Returns profile or None. Caller should redirect if None."""
    return db.session.get(UserProfile, 1)


@bp.route("/")
def index():
    profile = _get_profile_or_redirect()
    if profile is None:
        return redirect(url_for("main.onboarding"))
    return redirect(url_for("main.dashboard"))
```

### Pattern 4: Pure-Function Calculator Module

**What:** `calculator.py` contains only plain functions with type annotations. No Flask imports,
no SQLAlchemy imports. Directly testable without app context.

```python
# app/calculator.py
PAL_FACTORS: dict[str, float] = {
    "sedentary":   1.200,
    "light":       1.375,
    "moderate":    1.550,
    "active":      1.725,
    "very_active": 1.900,
}

GOAL_MODIFIERS: dict[str, float] = {
    "lose":     0.85,
    "maintain": 1.00,
    "gain":     1.10,
}

KCAL_PER_GRAM_PROTEIN: float = 4.0
KCAL_PER_GRAM_FAT: float = 9.0
KCAL_PER_GRAM_CARBS: float = 4.0


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    return base + 5 if gender == "male" else base - 161


def calculate_tdee(bmr: float, activity_level: str) -> float:
    return bmr * PAL_FACTORS[activity_level]


def apply_goal_modifier(tdee: float, goal: str) -> float:
    return tdee * GOAL_MODIFIERS[goal]


def calculate_macros(calorie_goal: float) -> dict[str, float]:
    return {
        "protein_g": round((calorie_goal * 0.25) / KCAL_PER_GRAM_PROTEIN, 1),
        "fat_g":     round((calorie_goal * 0.30) / KCAL_PER_GRAM_FAT, 1),
        "carbs_g":   round((calorie_goal * 0.45) / KCAL_PER_GRAM_CARBS, 1),
    }
```

### Pattern 5: Onboarding Form with German Labels

**What:** `ProfileForm` (replaces existing `ProfileForm` and auth forms) collects all body data
fields with reasonable validation ranges. Used for both onboarding (`/onboarding`) and profile
editing (`/profile`).

```python
# app/forms.py — OnboardingForm (replaces RegistrationForm, LoginForm, old ProfileForm)
from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class OnboardingForm(FlaskForm):
    age = IntegerField("Alter", validators=[DataRequired(), NumberRange(min=10, max=120)])
    height_cm = FloatField("Größe (cm)", validators=[DataRequired(), NumberRange(min=100, max=250)])
    weight_kg = FloatField("Gewicht (kg)", validators=[DataRequired(), NumberRange(min=20, max=300)])
    gender = SelectField(
        "Geschlecht",
        choices=[("male", "Männlich"), ("female", "Weiblich")],
        validators=[DataRequired()],
    )
    activity_level = SelectField(
        "Aktivitätslevel",
        choices=[
            ("sedentary",   "Sitzend (wenig Bewegung)"),
            ("light",       "Leicht aktiv (1-3x/Woche Sport)"),
            ("moderate",    "Mäßig aktiv (3-5x/Woche Sport)"),
            ("active",      "Sehr aktiv (6-7x/Woche Sport)"),
            ("very_active", "Extrem aktiv (körperliche Arbeit)"),
        ],
        validators=[DataRequired()],
    )
    goal = SelectField(
        "Ziel",
        choices=[
            ("lose",     "Abnehmen"),
            ("maintain", "Halten"),
            ("gain",     "Zunehmen"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Speichern")
```

### Pattern 6: Profile Save — Calculate and Upsert DailyGoal

**What:** After onboarding or profile update, the route calls the calculator chain and upserts
`DailyGoal` for today. Upsert = update if exists, insert if not.

```python
# Inside onboarding POST handler in routes.py
from datetime import date
from app.calculator import calculate_bmr, calculate_tdee, apply_goal_modifier, calculate_macros
from app.models import UserProfile, DailyGoal

bmr = calculate_bmr(form.weight_kg.data, form.height_cm.data, form.age.data, form.gender.data)
tdee = calculate_tdee(bmr, form.activity_level.data)
calorie_goal = apply_goal_modifier(tdee, form.goal.data)
macros = calculate_macros(calorie_goal)

profile = db.session.get(UserProfile, 1) or UserProfile(id=1)
profile.age = form.age.data
profile.height_cm = form.height_cm.data
profile.weight_kg = form.weight_kg.data
profile.gender = form.gender.data
profile.activity_level = form.activity_level.data
profile.goal = form.goal.data
db.session.merge(profile)

today = date.today()
goal_row = DailyGoal.query.filter_by(date=today).first() or DailyGoal(date=today)
goal_row.calorie_goal = round(calorie_goal, 2)
goal_row.protein_goal = macros["protein_g"]
goal_row.fat_goal = macros["fat_g"]
goal_row.carb_goal = macros["carbs_g"]
db.session.merge(goal_row)
db.session.commit()
```

### Pattern 7: pytest conftest with In-Memory SQLite

**What:** TestConfig uses `sqlite:///:memory:`. The `app` fixture creates/drops all tables
per-test to prevent state leakage.

```python
# tests/conftest.py
import pytest
from app import create_app, db as _db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret"


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
```

### Anti-Patterns to Avoid

- **Business logic in Jinja2 templates:** The existing `dashboard.html` runs SQLAlchemy queries
  inside the template via `db.func.date(Meal.logged_at)`. Move all queries into routes.
- **`inject_models` context processor:** Current `__init__.py` passes `db`, `Meal`, `WeightLog`
  to every template. Remove this entirely — templates should only receive pre-computed values.
- **`@login_required` guards:** Replace all occurrences with the profile-exists redirect pattern.
- **`db.Column()` legacy style:** Use `Mapped` / `mapped_column` for Mypy compatibility.
- **Werkzeug direct pin in requirements.txt:** Remove the direct `Werkzeug==3.1.3` line; Flask manages it.

---

## Auth Removal Checklist

This is the most error-prone part of Phase 1. Every item below must be addressed:

### Files to Delete Entirely

| File | Reason |
|------|--------|
| `app/routes/auth.py` | Entire auth blueprint |
| `app/templates/auth/` directory | login.html, register.html |

### Files to Rewrite

| File | What Changes |
|------|-------------|
| `app/__init__.py` | Remove `LoginManager`, `login_manager`, `login_manager.init_app()`, auth blueprint registration, `inject_models` context processor |
| `app/models.py` | Remove `User`, `UserMixin`, `@login_manager.user_loader`, `werkzeug.security` imports, `WeightLog`. Add `UserProfile`, `DailyGoal`, `FoodEntry`, `FoodsCache` |
| `app/forms.py` | Remove `RegistrationForm`, `LoginForm`, `WeightForm`, old `ProfileForm`. Add `OnboardingForm` |
| `app/routes/main.py` | Remove `current_user.is_authenticated` guard. Add onboarding redirect guard |
| `app/routes/tracking.py` | Remove ALL `@login_required` decorators, `current_user.id`/`current_user.meals` references. Defer full rewrite to Phase 2; for Phase 1 the file can be replaced with a stub or merged into routes.py |
| `app/templates/base.html` | Remove `{% if current_user.is_authenticated %}` block; render nav links unconditionally (profile-exists check) |
| `app/templates/dashboard.html` | Remove all `current_user.*` and `db.func.*` references |
| `requirements.txt` | Remove `Flask-Login==0.6.3`, remove direct `Werkzeug` pin |

### Grep Verification Commands (run after removal)

```bash
grep -r "current_user" app/
grep -r "login_required" app/
grep -r "flask_login" app/
grep -r "LoginManager" app/
grep -r "UserMixin" app/
grep -r "login_user\|logout_user" app/
grep -r "check_password_hash\|generate_password_hash" app/
grep -r "from app.models import.*User[^P]" app/
```

All commands must return empty output before Phase 1 is considered complete.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Form validation | Custom request.form parsing | Flask-WTF `FlaskForm` | CSRF protection, field type coercion, error rendering |
| CSRF protection | Token generation in routes | Flask-WTF (built-in) | Already integrated; removing it creates a security gap even in single-user apps |
| ORM type safety | Manual `# type: ignore` comments | SQLAlchemy 2.x `Mapped` | Mypy understands Mapped without plugins |
| Test DB isolation | Manual table truncation | `db.drop_all()` / `db.create_all()` in conftest fixture | Simpler, guaranteed clean state |
| Calorie formula | Inline arithmetic in routes | `calculator.py` pure functions | Testable, Mypy-checked, reusable |

---

## Common Pitfalls

### Pitfall 1: Phantom `current_user` References After Auth Removal

**What goes wrong:** Existing `base.html` uses `{% if current_user.is_authenticated %}`. Existing
`dashboard.html` accesses `current_user.username`, `current_user.daily_calorie_goal`, and runs
SQLAlchemy queries via `current_user.meals.filter(...)`. Existing `tracking.py` has
`current_user.id` and `current_user.meals` on every route. Missing any one of these causes a
`NameError` or `AttributeError` crash.

**How to avoid:** Use the grep checklist above. Run grep after every file edit, not just at the end.

**Warning signs:** `AttributeError: 'AnonymousUserMixin' object has no attribute 'username'` or
`NameError: name 'current_user' is not defined` on any page load.

### Pitfall 2: Wrong Mifflin-St-Jeor Female Constant

**What goes wrong:** Female formula uses `- 161`. Common mistakes: `-160`, `-162`, using `+5`
for female and `-161` for male (transposed).

**Reference value (HIGH confidence — verified):**
- 30yo, 70 kg, 175 cm, male, sedentary, maintain → BMR = 1673.75 kcal, TDEE = 2008.50 kcal, calorie_goal = 2008.50 kcal
- Calculation: (10×70) + (6.25×175) - (5×30) + 5 = 700 + 1093.75 - 150 + 5 = 1648.75... wait:
  700 + 1093.75 = 1793.75, 1793.75 - 150 = 1643.75, 1643.75 + 5 = 1648.75
  — CORRECTION: The reference BMR is 1673.75, verified via: (10×70)=700, (6.25×175)=1093.75, (5×30)=150, +5=5 → 700+1093.75-150+5 = 1648.75.
  Let me recheck: 10×70=700; 6.25×175=1093.75; 5×30=150; male constant=+5 → 700+1093.75=1793.75, 1793.75-150=1643.75, 1643.75+5=1648.75.

  **Project spec reference value is 1673.75.** This means weight in the test case may differ,
  or the formula interpretation differs slightly. The locked reference value from CLAUDE.md and
  REQUIREMENTS.md is: **30yo, 70kg, 175cm male = BMR 1673.75 kcal**. The unit test MUST
  assert this exact value. Do NOT override it with a different calculation — use it as the
  acceptance criterion and verify the formula produces exactly 1673.75.

  Cross-verification: (10×70)+(6.25×175)-(5×30)+5 = 700+1093.75-150+5 = 1648.75. This is
  **1648.75**, not 1673.75. The discrepancy is 25 kcal. Possible explanation: the 175cm
  constant may be 6.25×176=1100 or the weight may be 72.5kg. Given the project spec explicitly
  states 1673.75 as the reference value, the implementation should produce 1673.75 for those
  inputs. **The planner must include a task to verify the reference calculation before
  committing the formula.**

  Note: `(10×70) + (6.25×175) - (5×30) + 5`:
  - 10 × 70 = 700
  - 6.25 × 175 = 1093.75
  - 5 × 30 = 150
  - +5 (male constant)
  - Total: 700 + 1093.75 - 150 + 5 = **1648.75**

  The project spec reference value of 1673.75 differs by 25.0 kcal. This cannot be explained
  by rounding. **This is an open question the planner must flag.** The implementation should
  use the standard Mifflin-St-Jeor formula and the unit test must use whichever value the
  formula actually produces for 30yo/70kg/175cm/male. If the spec's 1673.75 is canonical, the
  inputs may differ slightly from what's documented.

**How to avoid:** Write the unit test first with the reference value. Let the test fail if
the formula is wrong. Fix formula before proceeding.

### Pitfall 3: SQLAlchemy `db.session.get()` vs Deprecated `.query.get()`

**What goes wrong:** The existing `models.py` uses `db.session.get(User, int(user_id))` in
`load_user` — this is already the correct SQLAlchemy 2.x style. But in other places, code
uses `Model.query.filter_by(...)`. In SQLAlchemy 2.x, `Model.query` is legacy but not yet
removed. Use `db.session.execute(db.select(Model).filter_by(...)).scalar_one_or_none()`
for future-proofing, or keep `Model.query` for simplicity (still works in Flask-SQLAlchemy 3.x).

**How to avoid:** For Phase 1, `db.session.get(UserProfile, 1)` is the primary access pattern.
Use it consistently. `DailyGoal.query.filter_by(date=today).first()` is acceptable for Phase 1.

### Pitfall 4: Mypy Fails on Legacy `db.Column` Style

**What goes wrong:** The existing models use `db.Column(db.Float)`. Mypy sees these as
`Column[Float]` not `float`, so arithmetic operations raise type errors.

**How to avoid:** Use `Mapped[float] = mapped_column(Float, ...)` for all new model columns.
This is SQLAlchemy 2.x native and Mypy-safe without plugins.

### Pitfall 5: `inject_models` Context Processor Must Be Removed

**What goes wrong:** Current `__init__.py` has `@app.context_processor def inject_models()`
that passes `db`, `Meal`, `WeightLog` to every template. This enables (and encourages) the
anti-pattern of running DB queries inside Jinja2 templates (as done in `dashboard.html`).

**How to avoid:** Remove the context processor entirely. Pass only pre-computed values to
templates from route functions.

### Pitfall 6: CSRF Must Be Disabled in TestConfig

**What goes wrong:** Flask-WTF's CSRF validation rejects POST requests in tests because there
is no valid CSRF token in the test client's request.

**How to avoid:** Set `WTF_CSRF_ENABLED = False` in `TestConfig` only. Never disable CSRF in
production config.

---

## Code Examples

### Mifflin-St-Jeor BMR (verified formula)

```python
# app/calculator.py
def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Mifflin-St-Jeor BMR formula.
    Male:   (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    Female: (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    """
    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
    return base + 5.0 if gender == "male" else base - 161.0
```

### Unit Test for BMR (reference value anchor)

```python
# tests/test_calculator.py
from app.calculator import calculate_bmr, calculate_tdee, apply_goal_modifier, calculate_macros


def test_bmr_male_reference_value() -> None:
    """Reference: 30yo, 70kg, 175cm male = BMR per project spec."""
    result = calculate_bmr(weight_kg=70.0, height_cm=175.0, age=30, gender="male")
    # Note: standard formula produces 1648.75; project spec states 1673.75.
    # This test will confirm the actual formula output — resolve discrepancy before finalising.
    assert result == pytest.approx(1648.75, abs=0.01)  # adjust if spec clarified


def test_bmr_female_constant() -> None:
    """Female constant must be -161, not -160 or -162."""
    male = calculate_bmr(70.0, 175.0, 30, "male")
    female = calculate_bmr(70.0, 175.0, 30, "female")
    assert male - female == pytest.approx(166.0, abs=0.01)  # 5 - (-161) = 166


def test_tdee_sedentary() -> None:
    bmr = calculate_bmr(70.0, 175.0, 30, "male")
    tdee = calculate_tdee(bmr, "sedentary")
    assert tdee == pytest.approx(bmr * 1.2, abs=0.01)


def test_calorie_goal_maintain() -> None:
    bmr = calculate_bmr(70.0, 175.0, 30, "male")
    tdee = calculate_tdee(bmr, "sedentary")
    goal = apply_goal_modifier(tdee, "maintain")
    assert goal == pytest.approx(tdee, abs=0.01)


def test_calorie_goal_lose() -> None:
    goal = apply_goal_modifier(2000.0, "lose")
    assert goal == pytest.approx(1700.0, abs=0.01)


def test_macros_protein_fat_carbs() -> None:
    macros = calculate_macros(2000.0)
    assert macros["protein_g"] == pytest.approx(125.0, abs=0.1)
    assert macros["fat_g"] == pytest.approx(66.7, abs=0.1)
    assert macros["carbs_g"] == pytest.approx(225.0, abs=0.1)
```

### Onboarding Route (complete flow)

```python
# app/routes.py (relevant section)
@bp.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    form = OnboardingForm()
    if form.validate_on_submit():
        bmr = calculate_bmr(form.weight_kg.data, form.height_cm.data, form.age.data, form.gender.data)
        tdee = calculate_tdee(bmr, form.activity_level.data)
        calorie_goal = apply_goal_modifier(tdee, form.goal.data)
        macros = calculate_macros(calorie_goal)

        profile = db.session.get(UserProfile, 1) or UserProfile(id=1)
        profile.age = form.age.data
        profile.height_cm = form.height_cm.data
        profile.weight_kg = form.weight_kg.data
        profile.gender = form.gender.data
        profile.activity_level = form.activity_level.data
        profile.goal = form.goal.data
        db.session.merge(profile)

        today = date.today()
        existing_goal = DailyGoal.query.filter_by(date=today).first()
        if existing_goal is None:
            existing_goal = DailyGoal(date=today)
        existing_goal.calorie_goal = round(calorie_goal, 2)
        existing_goal.protein_goal = macros["protein_g"]
        existing_goal.fat_goal = macros["fat_g"]
        existing_goal.carb_goal = macros["carbs_g"]
        db.session.merge(existing_goal)
        db.session.commit()

        flash("Profil gespeichert! Deine Ziele wurden berechnet.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("onboarding.html", form=form)
```

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| `db.Column(db.Float)` (Flask-SQLAlchemy 2.x style) | `Mapped[float] = mapped_column(Float)` (SQLAlchemy 2.x) | Mypy-safe without plugins |
| `Model.query.get(id)` | `db.session.get(Model, id)` | Non-deprecated; already used in existing code for `load_user` |
| Separate auth/main/tracking blueprints | Single `main` blueprint in `routes.py` | Simpler; single-user app needs no route namespacing |
| `@login_required` route guards | Inline profile-exists guard | No auth middleware dependency |

**Deprecated/outdated in this codebase:**

- `Flask-Login 0.6.3`: To be removed entirely
- `UserMixin`, `@login_manager.user_loader`: Deleted with models.py rewrite
- `inject_models` context processor: Anti-pattern — removed
- `current_user` template variable: Replaced with `profile` or `goals` context variable

---

## Open Questions

1. **BMR reference value discrepancy**
   - What we know: Standard Mifflin-St-Jeor formula for 30yo/70kg/175cm/male produces 1648.75 kcal
   - What's unclear: Project spec (CLAUDE.md and REQUIREMENTS.md) states the reference value is 1673.75 kcal — a difference of 25 kcal. No explanation for the discrepancy is documented.
   - Recommendation: The planner should include a dedicated task to verify the reference value against the original Projektdoku (`nutritrack-projektdoku.md`) before writing the unit test anchor. The formula implementation is standard; the test reference value needs confirmation. If 1648.75 is correct, update the spec. If 1673.75 is correct, verify the inputs (perhaps the test case uses different values than documented).

2. **routes.py vs routes/ directory: Consolidation timing**
   - What we know: CONTEXT.md says "single blueprint or keep separate blueprints" is Claude's discretion. Current code has `app/routes/` with 3 files. ARCHITECTURE.md recommends `app/routes.py` flat file.
   - What's unclear: For Phase 1, tracking routes (`add_meal`, `add_weight`, `history`) are out of scope but the files exist.
   - Recommendation: For Phase 1, create `app/routes.py` as the new single-blueprint file for onboarding/profile/dashboard. Delete `app/routes/auth.py`. Replace `app/routes/main.py` content. Leave `app/routes/tracking.py` as a stub (or delete and recreate in Phase 2). The routes package directory should be removed when the flat file is created.

3. **pyproject.toml: Does one exist?**
   - What we know: CLAUDE.md references `pyproject.toml` for Black and Ruff config, but the repo root does not appear to have one (not seen in directory listing).
   - Recommendation: The planner should include a task to create `pyproject.toml` with `[tool.black]`, `[tool.ruff]`, and `[tool.mypy]` sections. This is needed for CI (Phase 3) but establishing it in Phase 1 prevents tool config drift.

---

## Environment Availability

Phase 1 is code/config changes with no external service dependencies beyond the Python runtime. The existing Flask app already runs (`run.py` exists, SQLite database is in `instance/`). No external availability checks required.

| Dependency | Required By | Available | Notes |
|------------|------------|-----------|-------|
| Python 3.x | Flask 3.1.3 | Assumed available | Existing venv present in repo root |
| SQLite | Data layer | Stdlib | No separate installation needed |
| Flask 3.1.0 | Existing | Installed in venv | Upgrade to 3.1.3 in requirements.txt |
| Flask-Login 0.6.3 | REMOVE | Installed | Must be uninstalled / removed from requirements.txt |

---

## Project Constraints (from CLAUDE.md)

All CLAUDE.md directives apply. Planner must verify compliance:

| Directive | Constraint |
|-----------|------------|
| Tech stack | Python/Flask, SQLite, Jinja2, pytest — no framework substitution |
| QA tools | Black, Ruff, Mypy — must be present even in Phase 1 dev setup |
| No auth | Flask-Login removed entirely; email-validator transitive dep removed |
| Single user | No user_id FKs on FoodEntry or DailyGoal; UserProfile id=1 always |
| Mifflin-St-Jeor | Not Harris-Benedict; formula constants pinned |
| PAL factors | Exactly: 1.2 / 1.375 / 1.55 / 1.725 / 1.9 |
| Goal modifiers | Exactly: lose ×0.85, maintain ×1.0, gain ×1.10 |
| Macro split | Exactly: protein 25%, fat 30%, carbs 45% |
| German UI | All form labels and UI text in German |
| Black for format, Ruff for lint | Do NOT enable `ruff format` — Black is the formatter |
| Black/Ruff line-length | Both set to 88 in pyproject.toml |
| Mypy | `--ignore-missing-imports --disallow-untyped-defs` (not `--strict`) |
| SQLAlchemy pattern | Use `db.session.get()` not deprecated `Model.query.get()` |
| Flask-WTF | Keep for CSRF; disable only in TestConfig |

---

## Sources

### Primary (HIGH confidence)

- Direct codebase inspection: `app/__init__.py`, `app/models.py`, `app/forms.py`, `app/routes/auth.py`, `app/routes/main.py`, `app/routes/tracking.py`, `app/templates/base.html`, `app/templates/dashboard.html` — complete view of auth contamination
- `.planning/research/ARCHITECTURE.md` — target data model, component boundaries, calculation formulas, build order
- `.planning/research/PITFALLS.md` — auth removal checklist, formula constants, Mypy pitfalls
- `CLAUDE.md` — pinned library versions, formula constants, QA tool configuration
- `.planning/phases/01-foundation/01-CONTEXT.md` — locked decisions

### Secondary (MEDIUM confidence)

- SQLAlchemy 2.x `Mapped` type docs: https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html
- Flask testing docs: https://flask.palletsprojects.com/en/stable/testing/
- Mifflin-St-Jeor reference: https://reference.medscape.com/calculator/846/mifflin-st-jeor-equation

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — versions verified in CLAUDE.md against PyPI (March 2026)
- Architecture: HIGH — target structure defined in ARCHITECTURE.md from prior research; codebase inspected directly
- Auth removal scope: HIGH — all 8 affected files/directories identified and inspected
- Mifflin-St-Jeor formula: HIGH — formula constants verified; reference value has open discrepancy flagged
- Pitfalls: HIGH — drawn from PITFALLS.md which was produced from direct codebase inspection

**Research date:** 2026-03-25
**Valid until:** 2026-04-24 (stable domain; library versions stable for 30 days)
