# Technology Stack

**Project:** NutriTrack
**Researched:** 2026-03-24
**Brownfield context:** Existing Flask app with auth system (Flask-Login, Flask-WTF) that must be restructured into a single-user app without authentication.

---

## Recommended Stack

### Core Framework

| Technology | Current Version | Latest Stable | Purpose | Why |
|------------|----------------|---------------|---------|-----|
| Flask | 3.1.0 | **3.1.3** | Web framework | Project-constrained. 3.1.x is the active release series; update from 3.1.0 to 3.1.3 for bug fixes. Requires Python 3.9+. |
| Flask-SQLAlchemy | 3.1.1 | **3.1.1** | ORM / DB integration | Project-constrained. 3.1.1 is current; no update needed. Wraps SQLAlchemy 2.x with Flask lifecycle management. |
| Werkzeug | 3.1.3 | 3.x (bundled) | WSGI utilities | Flask dependency; version must track Flask. No direct dependency needed in requirements.txt — managed by Flask. |
| python-dotenv | 1.0.1 | **1.2.2** | Env-var / .env loading | Already in requirements.txt; update to 1.2.2 for Python 3.14 support and symlink fixes. |

**Confidence:** HIGH — verified against PyPI (March 2026).

### Database

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| SQLite | stdlib (3.45+) | Persistent storage | Project-constrained. No server, zero ops, single-user app — SQLite is the correct choice. File lives in `instance/nutritrack.db`. |
| SQLAlchemy | 2.x (via Flask-SQLAlchemy 3.1.1) | ORM | Provides type-safe query API, migration path if DB ever changes. Use `db.session.get()` not deprecated `Model.query`. |

**Confidence:** HIGH.

### Forms and Validation

| Technology | Current Version | Latest Stable | Purpose | Why |
|------------|----------------|---------------|---------|-----|
| Flask-WTF | 1.2.2 | **1.2.2** | Form classes + CSRF protection | Already in use; keep. CSRF protection matters even in single-user apps (browser-based XSRF). Provides `FlaskForm` base. |
| WTForms | (transitive via Flask-WTF) | — | Validators, field types | Do not import separately — let Flask-WTF manage the dependency. |

**Note on auth removal:** `RegistrationForm` and `LoginForm` in `forms.py` can be deleted. Their WTF dependency chain (email-validator) can be removed from requirements.txt once Email() validator is gone.

**Confidence:** HIGH.

### QA Toolchain

| Tool | Latest Stable | Purpose | Why / Config |
|------|---------------|---------|--------------|
| Black | **26.3.1** | Code formatter | Project-constrained. Zero-config formatter; run as `black .` in CI. Add `[tool.black] line-length = 88` to `pyproject.toml`. |
| Ruff | **0.15.7** | Linter (replaces Flake8/isort) | Project-constrained. Written in Rust; 100x faster than Flake8. Covers pycodestyle, pyflakes, isort rules, and more. Configure in `pyproject.toml` under `[tool.ruff]`. |
| Mypy | **1.19.1** | Static type checker | Project-constrained. Use `--strict` is too aggressive for brownfield; start with `--ignore-missing-imports` and `--disallow-untyped-defs`. Add `py.typed` marker if distributing. |

**Important:** Ruff and Black can overlap on formatting. Configure Ruff with `[tool.ruff.format]` disabled or set `select` to exclude formatter-owned rules (E1xx, W) to let Black own formatting. Ruff owns linting, Black owns formatting.

**Confidence:** HIGH — versions verified against PyPI (March 2026).

### Testing

| Tool | Latest Stable | Purpose | Why |
|------|---------------|---------|-----|
| pytest | **9.0.2** | Test runner | Project-constrained. De facto standard. Use `conftest.py` with `app` and `client` fixtures. |
| pytest-flask | **1.3.0** | Flask test fixtures | Provides `live_server`, `client`, and `app` fixtures. Version 1.3.0 added Flask 3.0 compatibility (removed deprecated `request_ctx`). Use `@pytest.mark.usefixtures("app")`. |

**Minimum test requirement:** 5 unit tests + integration tests. Recommended split: pure-Python unit tests for Mifflin-St-Jeor calculator logic (no Flask context needed), integration tests for route responses and DB writes via `client` fixture.

**Confidence:** HIGH — versions verified against PyPI.

### Open Food Facts Integration

| Technology | Latest Stable | Purpose | Why |
|------------|---------------|---------|-----|
| openfoodfacts | **5.0.1** | Product search / nutrition lookup | Official Python SDK from the OFF project. Production/Stable as of March 2026. Provides `API.product.text_search(query)` and `API.product.get(barcode)`. Pin exact version. |
| requests | **2.32.5** | HTTP fallback / raw API calls | Only needed if NOT using the `openfoodfacts` SDK. Prefer SDK — it handles rate limiting and response normalization. Keep as transitive dependency. |

**SDK usage pattern:**
```python
import openfoodfacts

api = openfoodfacts.API(user_agent="NutriTrack/1.0")
results = api.product.text_search("Vollmilch")
# results["products"] → list of dicts with "nutriments" key
# nutriments: {"energy-kcal_100g": ..., "proteins_100g": ..., "fat_100g": ..., "carbohydrates_100g": ...}
```

**Note:** The SDK documentation still carries a "beta API" caveat despite the 5.0.1 production/stable PyPI classifier. Pin to `openfoodfacts==5.0.1` and wrap calls in try/except to handle products with missing nutriment data gracefully.

**Confidence:** MEDIUM — version verified against PyPI; API stability caveat from official docs.

### CI/CD

| Technology | Purpose | Why |
|------------|---------|-----|
| GitHub Actions | CI pipeline | Project-constrained. Use `ubuntu-latest` runner. Recommended job order: `black --check .` → `ruff check .` → `mypy app/` → `pytest`. |

**Recommended workflow structure:**
```yaml
jobs:
  qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: black --check .
      - run: ruff check .
      - run: mypy app/ --ignore-missing-imports
      - run: pytest
```

**Confidence:** HIGH.

---

## Libraries to REMOVE from This Project

| Library | Reason to Remove | What Replaces It |
|---------|-----------------|------------------|
| Flask-Login 0.6.3 | Auth is explicitly out of scope ("Won't Have"). Removing eliminates `login_required` decorators, `current_user` references, `LoginManager`, and `UserMixin`. | Session variable or `g` object for single-user profile state. |
| `email-validator` (transitive via Flask-WTF Email()) | Only needed for RegistrationForm / LoginForm which are deleted. | Nothing — those forms are removed. |

---

## Data Model Changes Required

The existing `User` model conflates auth identity (username, email, password_hash) with profile data (height_cm, target_weight_kg, daily_calorie_goal). For a single-user app:

**Recommended:** Replace `User` with a `UserProfile` model containing only nutrition-relevant fields:

```python
class UserProfile(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    age: Mapped[int] = mapped_column(nullable=False)
    height_cm: Mapped[float] = mapped_column(nullable=False)
    weight_kg: Mapped[float] = mapped_column(nullable=False)
    sex: Mapped[str] = mapped_column(String(10), nullable=False)  # "male" / "female"
    activity_level: Mapped[float] = mapped_column(nullable=False)  # PAL: 1.2–1.9
    goal: Mapped[str] = mapped_column(String(20), nullable=False)  # "lose" / "maintain" / "gain"
    # Computed and stored at save time:
    bmr_kcal: Mapped[float] = mapped_column(nullable=True)
    tdee_kcal: Mapped[float] = mapped_column(nullable=True)
    calorie_goal_kcal: Mapped[float] = mapped_column(nullable=True)
```

Use SQLAlchemy 2.x `Mapped[]` type annotations — they work with Mypy out of the box and are the current recommended API.

---

## Mifflin-St-Jeor Implementation Pattern

The formula must live in a pure Python module (`app/calculator.py`) with no Flask dependencies. This enables unit testing without app context.

```python
# app/calculator.py
from dataclasses import dataclass

PAL_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

GOAL_MODIFIERS = {
    "lose": 0.85,      # -15%
    "maintain": 1.0,
    "gain": 1.10,      # +10%
}

def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """Mifflin-St Jeor BMR. sex: 'male' or 'female'."""
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    return base + 5 if sex == "male" else base - 161

def calculate_tdee(bmr: float, pal_key: str) -> float:
    return bmr * PAL_FACTORS[pal_key]

def calculate_calorie_goal(tdee: float, goal_key: str) -> float:
    return tdee * GOAL_MODIFIERS[goal_key]

def calculate_macros(calorie_goal: float) -> dict[str, float]:
    """25% protein, 30% fat, 45% carbs."""
    return {
        "protein_g": (calorie_goal * 0.25) / 4,
        "fat_g": (calorie_goal * 0.30) / 9,
        "carbs_g": (calorie_goal * 0.45) / 4,
    }
```

This structure makes the 5 required unit tests straightforward: one per function, with male/female branches.

**Confidence:** HIGH — formula constants verified against multiple medical reference sources.

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| ORM | Flask-SQLAlchemy | Raw SQLite (sqlite3) | SQLAlchemy 2.x Mapped[] types give Mypy compatibility for free; no migration needed as it's already in use |
| Form handling | Flask-WTF | Raw HTML forms + request.form | Flask-WTF CSRF protection is worth the dependency even for single-user; already integrated |
| API client | openfoodfacts SDK | Direct requests to api.openfoodfacts.org | SDK handles response normalization, field naming inconsistencies, and is maintained by OFF team |
| Type checking | Mypy | Pyright | Mypy is the project constraint; Pyright has better IDE integration but Mypy is sufficient for CI |
| Linter | Ruff | Flake8 + isort + pylint | Ruff replaces all three at 100x speed; Flake8 is effectively deprecated for new projects |

---

## Final requirements.txt (Recommended)

```
# Runtime
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2
python-dotenv==1.2.2
openfoodfacts==5.0.1
```

```
# requirements-dev.txt
pytest==9.0.2
pytest-flask==1.3.0
black==26.3.1
ruff==0.15.7
mypy==1.19.1
```

**Note:** Werkzeug is a Flask dependency — do not pin it separately unless a specific version is needed. Flask-Login should be removed entirely.

---

## Sources

- Flask PyPI: https://pypi.org/project/Flask/ (verified March 2026, version 3.1.3)
- Flask-SQLAlchemy PyPI: https://pypi.org/project/Flask-SQLAlchemy/ (verified March 2026, version 3.1.1)
- Flask-WTF PyPI: https://pypi.org/project/Flask-WTF/ (verified March 2026, version 1.2.2)
- openfoodfacts PyPI: https://pypi.org/project/openfoodfacts/ (verified March 2026, version 5.0.1)
- openfoodfacts Python SDK usage docs: https://openfoodfacts.github.io/openfoodfacts-python/usage/
- pytest PyPI: https://pypi.org/project/pytest/ (verified March 2026, version 9.0.2)
- pytest-flask PyPI: https://pypi.org/project/pytest-flask/ (verified March 2026, version 1.3.0)
- Black PyPI: https://pypi.org/project/black/ (verified March 2026, version 26.3.1)
- Ruff PyPI: https://pypi.org/project/ruff/ (verified March 2026, version 0.15.7)
- Mypy PyPI: https://pypi.org/project/mypy/ (verified March 2026, version 1.19.1)
- python-dotenv PyPI: https://pypi.org/project/python-dotenv/ (verified March 2026, version 1.2.2)
- Flask official docs — project layout: https://flask.palletsprojects.com/en/stable/tutorial/layout/
- Flask official docs — testing: https://flask.palletsprojects.com/en/stable/testing/
- Ruff FAQ (Black overlap guidance): https://docs.astral.sh/ruff/faq/
