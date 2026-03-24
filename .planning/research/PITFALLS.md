# Domain Pitfalls

**Domain:** Flask nutrition tracking web app (brownfield, academic project)
**Researched:** 2026-03-24
**Confidence:** HIGH — based on direct codebase inspection + verified domain research

---

## Critical Pitfalls

Mistakes that cause rewrites, test failures, or academic grade penalties.

---

### Pitfall 1: Incomplete Auth Removal — Phantom `current_user` References

**What goes wrong:** The existing app has Flask-Login woven throughout at every layer. Removing the auth blueprint without purging every reference causes `NameError`/`AttributeError` crashes at runtime and import-time failures that break CI.

**Why it happens:** Auth is not isolated to one file. It is spread across:
- `app/__init__.py` — imports `LoginManager`, calls `login_manager.init_app(app)`
- `app/models.py` — `UserMixin`, `@login_manager.user_loader`, `werkzeug` password hashing
- `app/routes/auth.py` — entire blueprint (register/login/logout)
- `app/routes/main.py` — `current_user.is_authenticated` guard
- `app/routes/tracking.py` — `@login_required` on every route, `current_user.id` and `current_user.meals` throughout
- `app/templates/base.html` — `{% if current_user.is_authenticated %}` and `url_for('auth.logout')`
- `app/templates/dashboard.html` — `current_user.username`, `current_user.daily_calorie_goal`, `current_user.meals`

**Consequences:** App boots but crashes on first request; CI pytest fails immediately on import; Mypy flags unresolved references; Ruff flags unused imports.

**Prevention:**
1. Do a full-codebase grep for `current_user`, `login_required`, `login_manager`, `UserMixin`, `flask_login`, `LoginManager`, `logout_user`, `login_user` before considering auth removal "done"
2. Remove Flask-Login and Werkzeug password-hashing imports from requirements.txt after removal
3. Replace template `{% if current_user.is_authenticated %}` blocks — in the single-user model, these blocks are always-true, so just render the nav links unconditionally
4. The `db.func.date(db.func.now())` call in `dashboard.html` is SQLAlchemy logic inside a Jinja template — move this to the route function, not the template

**Detection:** `from app import create_app` failing in pytest conftest is the first signal. Run `grep -r "current_user\|login_required\|flask_login" app/` after each refactoring step.

**Phase:** Sprint 1 (Grundstruktur) — must be resolved before any other work proceeds.

---

### Pitfall 2: Wrong Mifflin-St-Jeor Formula Coefficients or Gender Constant

**What goes wrong:** The formula has two variants that differ by a constant (+5 for male, -161 for female). Swapping the constants, using the wrong sign, or confusing weight units (lbs vs kg) produces a systematically wrong BMR. Academic graders will check the formula output against known reference values.

**Why it happens:** Transcription errors when implementing from memory. The formula looks simple but the female constant (−161) is easy to misremember as −160 or −162.

**Correct formula (HIGH confidence — verified against Medscape calculator):**
```
BMR_male   = (10 × weight_kg) + (6.25 × height_cm) − (5 × age_years) + 5
BMR_female = (10 × weight_kg) + (6.25 × height_cm) − (5 × age_years) − 161
```

**PAL multipliers (must match exactly):**
```
1.2   — sedentary
1.375 — lightly active
1.55  — moderately active
1.725 — very active
1.9   — extra active
```

**Consequences:** Every downstream value (TDEE, macros, calorie goal) is wrong. Unit tests using reference values will fail. Academic grader will spot the error immediately.

**Prevention:**
- Implement as a pure function with no side effects (no Flask, no DB)
- Write unit tests using the exact reference values from Medscape or a published calculator: a 30-year-old, 70 kg, 175 cm male should yield BMR = 1673.75 kcal
- Test both male and female paths explicitly
- Store PAL values as a dict constant, not inline magic numbers

**Detection:** Any BMR result outside the range 1200–2200 kcal for a healthy adult is a red flag. Test coverage gap on the calculator module is a warning sign.

**Phase:** Sprint 1 (Bedarfsberechnung) — implement and test before touching the dashboard.

---

### Pitfall 3: Portion-to-Nutrition Scaling Not Isolated

**What goes wrong:** Nutrition values (calories, protein, carbs, fat) per entry are stored as absolute values for the portion entered, but the calculation `(value_per_100g / 100) × amount_g` is duplicated in the route, the template, and potentially the model. When the formula needs changing, it breaks in one place but not others.

**Why it happens:** It feels natural to compute inline in the route. The calculation is simple enough that developers don't extract it.

**Consequences:** Rounding inconsistency across views; Mypy cannot type-check inline arithmetic properly; difficult to unit-test without HTTP request overhead; if Open Food Facts returns values per 100g (it does), conversion gets confused with per-portion storage.

**Prevention:**
- Extract a pure `calculate_nutrition(per_100g: NutritionPer100g, amount_g: float) -> NutritionAbsolute` function in a `calculator.py` module
- Store only the result (absolute values for the logged portion) in the database — do not store per-100g values alongside per-portion values in the same row
- Round to 1 decimal place at the output boundary (template), not at the calculation boundary

**Detection:** Two places in the codebase performing the `/ 100 * amount` pattern is the warning sign.

**Phase:** Sprint 2 (Tracking) — establish the pattern before the first food entry route is written.

---

### Pitfall 4: Mypy Fails on Flask-SQLAlchemy Model Attribute Access

**What goes wrong:** Mypy does not understand SQLAlchemy's dynamic column descriptors. `user.height_cm` is flagged as `Column[Float]` rather than `float | None`, causing type errors in arithmetic downstream (e.g., `height_cm * 6.25`).

**Why it happens:** Flask-SQLAlchemy performs runtime magic that static type checkers cannot see without plugin support. The `db.Column` descriptor returns the column type at class level but the actual Python type at instance level.

**Consequences:** CI Mypy step fails on the first arithmetic operation touching a model attribute. Fixing with `# type: ignore` everywhere defeats the purpose of Mypy and looks bad in an academic submission.

**Prevention:**
- Use SQLAlchemy 2.0 `Mapped` / `mapped_column` style with explicit Python type annotations:
  ```python
  from sqlalchemy.orm import Mapped, mapped_column
  height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
  ```
- This is natively understood by Mypy without plugins (HIGH confidence, SQLAlchemy 2.0 docs)
- Add `mypy.ini` or `[tool.mypy]` in `pyproject.toml` with `plugins = sqlalchemy.ext.mypy.plugin` as a fallback if staying on legacy style

**Detection:** `mypy app/` on the current codebase will show these immediately. Run Mypy locally before writing any business logic.

**Phase:** Sprint 1 (model rewrite) — must be resolved at the same time as auth removal.

---

### Pitfall 5: Black and Ruff Conflict in CI

**What goes wrong:** Black and Ruff both format code. When Black reformats a file that Ruff would format differently, the CI `--check` run fails on files that look fine locally (because one tool ran after the other).

**Why it happens:** Running `black .` locally before committing fixes Black's complaints, but if Ruff's formatter (`ruff format`) is also enabled and disagrees, or if Ruff's linter flags Black-formatted code (e.g., line length disagreement), both tools fail.

**Consequences:** CI is permanently red; graders see a failing pipeline badge.

**Prevention:**
- Use a single `pyproject.toml` with matching `line-length = 88` for both Black and Ruff
- Ruff's formatter is Black-compatible by design — if using `ruff format`, do not also run `black` (they are redundant)
- For this project, use Black for formatting + Ruff for linting only (not `ruff format`) — keeps roles clear
- Lock versions in requirements: `black==24.x`, `ruff==0.x` — floating versions cause CI drift

**Detection:** CI passes locally but fails on GitHub Actions. Usually caused by tool version mismatch between local environment and CI runner.

**Phase:** Sprint 3 (CI/CD) — configure once, add pre-commit hook to catch locally before push.

---

### Pitfall 6: SQLite Date Filtering Breaks with UTC Timezone Mismatch

**What goes wrong:** The existing `dashboard.html` filters meals with `db.func.date(db.func.now())` to show "today's" meals. SQLite's `now()` returns UTC time. If the user is in CET (UTC+1), meals logged after 23:00 local time appear on the wrong day.

**Why it happens:** The existing code stores `datetime.now(timezone.utc)` (correct), but then compares against `db.func.now()` in SQLite which also returns UTC — this works until you try to display "today" from the template using SQLite functions. The bigger risk is when date filtering moves to the route: using `datetime.today()` (local time) vs `datetime.now(timezone.utc)` (UTC) produces mismatches.

**Consequences:** Meals from the previous evening don't appear; today's goal shows 0 kcal consumed even though food was logged. Difficult to spot in testing unless tests run near midnight or use non-UTC timezones.

**Prevention:**
- Store all datetimes as UTC (`datetime.now(timezone.utc)`) — already done correctly in the existing models
- Filter in Python, not SQLite: `entry.logged_at.date() == date.today()` — simple and timezone-safe for a local app
- Alternatively, decide on one timezone (UTC throughout) and be consistent
- Never mix `datetime.today()` and `datetime.now(timezone.utc)` in the same codebase

**Detection:** Add a test that logs a meal and then queries for today's meals — the count should be 1, not 0.

**Phase:** Sprint 2 (Tracking/Dashboard) — when implementing the daily summary query.

---

### Pitfall 7: Open Food Facts API Called Without Caching

**What goes wrong:** Each search query hits `https://world.openfoodfacts.org/cgi/search.pl` live. The search endpoint is rate-limited at 10 requests/minute (verified against Open Food Facts server issue tracker). In CI, integration tests that call the real API will fail intermittently or get the IP banned.

**Why it happens:** It is easy to write a `requests.get(OFF_URL, params={...})` call directly in the route. No one thinks about CI until the pipeline first runs.

**Consequences:** Flaky CI tests; potential IP ban during demo; slow page loads (API response time is 300–800ms); academic grader triggers a search and gets an error.

**Prevention:**
- Wrap all Open Food Facts calls in a service class (`FoodApiService`) with a local `foods_cache` SQLite table (already in the target schema per PROJECT.md)
- In tests, mock the API with `unittest.mock.patch` or `responses` library — never call the real API in pytest
- Add a `User-Agent` header identifying the app (OFF requires this per their terms of use)
- Cache search results by query string + timestamp; invalidate after 24 hours

**Detection:** Any test that makes a real HTTP call will be identifiable by the `requests` import without a corresponding mock. Look for `requests.get` calls outside a service class.

**Phase:** Sprint 4 (Erweiterungen) — but the service abstraction layer should be designed in Sprint 2 so tests are mockable from the start.

---

### Pitfall 8: Single-User Profile Not Bootstrapped — App Crashes on First Run

**What goes wrong:** After removing auth and removing the multi-user `User` model, the app has no user profile to reference. Routes that compute `daily_goals` or display the dashboard will crash with `NoneType has no attribute 'height_cm'` because no profile row exists.

**Why it happens:** The old app created a user on registration. The new single-user app must either (a) seed a default profile row at `db.create_all()` time, or (b) redirect to an onboarding flow if no profile exists. Neither is obvious without explicit design.

**Consequences:** The app crashes on first boot. Every route that reads the profile fails. Graders running the app fresh will see a 500 error immediately.

**Prevention:**
- At `create_all()` time, check if a `UserProfile` row exists; if not, insert a default placeholder row
- Or implement a `/onboarding` redirect: if `UserProfile.query.count() == 0`, redirect all routes to the onboarding form before allowing access to any other page
- The onboarding redirect approach is better for academic demonstration because it shows a complete user flow

**Detection:** `python run.py` on a fresh database then navigating to `/` — the app should not crash.

**Phase:** Sprint 1 (Grundstruktur) — the first thing after auth removal.

---

### Pitfall 9: Macro Split Rounding Sums to ≠ 100%

**What goes wrong:** The target macro split is Protein 25%, Fat 30%, Carbs 45%. When computing gram targets from the calorie goal, rounding each independently causes the gram-calorie sum to differ from the total by a few kcal.

**Example of the bug:**
```
Goal: 2000 kcal
Protein: 2000 * 0.25 / 4 = 125.0 g  → 500 kcal
Fat:     2000 * 0.30 / 9 = 66.67 g  → rounds to 66.7 → 600.3 kcal
Carbs:   2000 * 0.45 / 4 = 225.0 g  → 900 kcal
Total displayed: 2000.3 kcal  (off by 0.3)
```
This is a minor numerical issue but academic graders reviewing the formula closely will notice.

**Prevention:**
- Round gram values to 1 decimal using `round(value, 1)` consistently
- Display macro targets as both grams and kcal equivalent in the UI so the user (and grader) can verify
- Calorie constants: Protein = 4 kcal/g, Carbs = 4 kcal/g, Fat = 9 kcal/g — use named constants, not inline magic numbers

**Detection:** Unit test: compute macros for a 2000 kcal goal, verify `protein_kcal + fat_kcal + carbs_kcal` is within 1 kcal of 2000.

**Phase:** Sprint 1 (Bedarfsberechnung) — part of the calculator module unit tests.

---

### Pitfall 10: pytest Fixtures Leave Database State Between Tests

**What goes wrong:** Tests that commit data to a shared SQLite database leave rows that pollute subsequent tests. A test checking "0 meals today" passes in isolation but fails when run after a test that inserts a meal.

**Why it happens:** SQLite in-memory databases reset between connections, but if the test suite uses a file-based database (or a shared in-memory connection), state persists between tests unless explicitly cleaned.

**Consequences:** Tests pass individually (`pytest tests/test_calculator.py`) but fail collectively (`pytest`). CI fails; local runs pass — the classic flaky test problem.

**Prevention:**
- Use `TESTING = True` config with `SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"`
- Use a `conftest.py` fixture with function scope that calls `db.create_all()` in setup and `db.drop_all()` in teardown:
  ```python
  @pytest.fixture
  def app():
      app = create_app(TestConfig)
      with app.app_context():
          db.create_all()
          yield app
          db.drop_all()
  ```
- Keep calculator unit tests (pure functions) in a separate file from route integration tests — pure function tests never need DB setup

**Detection:** Test order dependency — run `pytest --randomly-seed=12345` to detect order-sensitive failures.

**Phase:** Sprint 3 (CI/CD) — but the fixture pattern must be established in Sprint 1 with the first tests written.

---

## Moderate Pitfalls

---

### Pitfall 11: Business Logic in Jinja2 Templates

**What goes wrong:** The existing `dashboard.html` has SQLAlchemy queries (`db.func.date(Meal.logged_at)`) directly inside Jinja2 templates via the `inject_models` context processor. This pattern passes `db` and model classes to every template globally.

**Prevention:** Move all database queries into route functions. Templates should receive only pre-computed Python values (lists, dicts, scalars). The `inject_models` context processor in `__init__.py` should be removed entirely during refactoring.

**Phase:** Sprint 1 (Grundstruktur refactor).

---

### Pitfall 12: Calorie Goal Modifier Applied Twice or Not At All

**What goes wrong:** The target calorie goal is TDEE modified by the user's goal (lose/maintain/gain). The modifiers per PROJECT.md are −15%/0%/+10%. If the modifier is applied when saving to the database AND also when displaying, the user sees double-modified values. If it is never stored and only computed at display time, the dashboard recalculates on every request.

**Prevention:** Store the final calorie goal (after modifier) in `daily_goals.calories_target`. Recalculate and update this value only when the user explicitly updates their profile.

**Phase:** Sprint 1 (Bedarfsberechnung) — define the data flow once and document it.

---

### Pitfall 13: Color-Coded Progress Thresholds Undefined or Inconsistent

**What goes wrong:** The "traffic light" progress display (normal/grün/orange-rot) requires defined thresholds. Without explicit thresholds agreed upon upfront, the template logic uses magic numbers that differ from what the grader expects based on the project spec.

**Prevention:** Define thresholds as named constants before writing any template logic:
- Green: intake ≥ 90% and ≤ 100% of goal
- Orange: intake > 100% and ≤ 110% of goal
- Red: intake > 110% of goal
- Grey/default: intake < 90% (under target)
These thresholds should appear in the project documentation and be verified by unit test.

**Phase:** Sprint 2 (Dashboard) — define constants before template work.

---

## Minor Pitfalls

---

### Pitfall 14: Missing `SECRET_KEY` in CI Environment

**What goes wrong:** Flask-WTF forms require a `SECRET_KEY` for CSRF tokens. The existing config falls back to `"dev-secret-key-change-in-production"`. If CI tests POST to form routes without this key set, CSRF validation fails with a 400 error.

**Prevention:** Set `WTF_CSRF_ENABLED = False` in the test config (`TestConfig`), not in production config. Alternatively, use `app.config["WTF_CSRF_ENABLED"] = False` only in the test fixture.

**Phase:** Sprint 3 (CI/CD setup).

---

### Pitfall 15: `requirements.txt` Contains Removed Auth Dependencies

**What goes wrong:** After removing Flask-Login and Werkzeug password hashing, `requirements.txt` still lists `Flask-Login==0.6.3`. Mypy or import-time checks on a clean CI environment install these unnecessary packages. Graders reading requirements.txt see dependencies that don't match the codebase.

**Prevention:** After auth removal, audit `requirements.txt` against actual imports. Add `pip-check` or manually verify `pip install -r requirements.txt && python -c "from app import create_app"` succeeds on a clean environment.

**Phase:** Sprint 1 (cleanup step after auth removal).

---

### Pitfall 16: Classendiagramm and Sequenzdiagramm as Afterthoughts

**What goes wrong:** The mandatory diagrams (Klassendiagramm, Sequenzdiagramm CI/CD) are produced from memory at submission time and don't match the actual code structure.

**Prevention:** Generate the class diagram from the final model structure before the last sprint. The CI/CD sequence diagram should be drafted when the GitHub Actions workflow is first written (Sprint 3), not retroactively.

**Phase:** Sprint 3 (CI/CD) for the sequence diagram; Sprint 4 final review for the class diagram.

---

## Phase-Specific Warnings

| Phase | Topic | Likely Pitfall | Mitigation |
|-------|-------|---------------|------------|
| Sprint 1 | Auth removal | Incomplete `current_user` purge (Pitfall 1) | Grep-driven checklist; app must boot on fresh DB |
| Sprint 1 | Model rewrite | Mypy failing on Column types (Pitfall 4) | Use SQLAlchemy 2.0 `Mapped` style from the start |
| Sprint 1 | Calculator | Wrong Mifflin-St-Jeor constant (Pitfall 2) | Unit test against reference value immediately |
| Sprint 1 | Single-user bootstrap | No profile on first run (Pitfall 8) | Onboarding redirect before any route logic |
| Sprint 2 | Portion math | Inline calculation duplication (Pitfall 3) | `calculator.py` module; pure functions only |
| Sprint 2 | Dashboard date filter | UTC/local time mismatch (Pitfall 6) | Python-side date comparison, not SQLite `now()` |
| Sprint 2 | Macro display | Rounding inconsistency (Pitfall 9) | Named constants for kcal-per-gram values |
| Sprint 3 | CI tooling | Black/Ruff conflict (Pitfall 5) | Single `pyproject.toml`; Black format + Ruff lint only |
| Sprint 3 | Test isolation | DB state leaking between tests (Pitfall 10) | In-memory SQLite + `drop_all()` in fixture teardown |
| Sprint 3 | CSRF in tests | 400 errors on POST tests (Pitfall 14) | `WTF_CSRF_ENABLED = False` in TestConfig |
| Sprint 4 | Open Food Facts | Live API calls in CI (Pitfall 7) | Mock at service layer; never hit real API in pytest |

---

## Sources

- Open Food Facts rate limit: [Define a rate-limit policy · Issue #8818](https://github.com/openfoodfacts/openfoodfacts-server/issues/8818) — MEDIUM confidence (GitHub issue, not official policy page)
- Mifflin-St-Jeor reference values: [Medscape Mifflin-St-Jeor Calculator](https://reference.medscape.com/calculator/846/mifflin-st-jeor-equation) — HIGH confidence (medical reference tool)
- SQLAlchemy 2.0 Mapped type annotations: [Mypy / Pep-484 Support for ORM Mappings](https://docs.sqlalchemy.org/en/14/orm/extensions/mypy.html) — HIGH confidence (official SQLAlchemy docs)
- Flask-SQLAlchemy test isolation: [pytest-flask-sqlalchemy](https://github.com/jeancochrane/pytest-flask-sqlalchemy) — MEDIUM confidence (well-maintained community plugin)
- Mypy on existing codebases: [Using mypy with an existing codebase](https://mypy.readthedocs.io/en/stable/existing_code.html) — HIGH confidence (official Mypy docs)
- Black/Ruff conflict issue: [Black stops looking for config at first pyproject.toml](https://github.com/psf/black/issues/2863) — HIGH confidence (official project issue tracker)
- Codebase inspection: direct analysis of `app/models.py`, `app/routes/`, `app/templates/`, `config.py`, `requirements.txt` in this repository — HIGH confidence
