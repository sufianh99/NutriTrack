# Project Research Summary

**Project:** NutriTrack
**Domain:** Single-user nutrition tracking web application (brownfield Flask, academic project)
**Researched:** 2026-03-24
**Confidence:** HIGH

## Executive Summary

NutriTrack is a brownfield Flask app being restructured from a multi-user auth-gated system into a single-user nutrition tracker. The core challenge is not building a nutrition tracker from scratch — it is surgically removing an auth layer that is woven through every module (models, routes, templates, init) while simultaneously adding the calorie calculation and food logging functionality the project spec requires. The recommended approach is to treat Sprint 1 as a demolition-and-foundation sprint: remove Flask-Login, rewrite models using SQLAlchemy 2.x `Mapped` types, implement the Mifflin-St-Jeor calculator as a pure Python module, and establish the pytest fixture pattern — all before touching the UI. Everything downstream depends on these foundations being correct.

The stack is constrained by the project spec and is appropriate: Flask 3.1.x, Flask-SQLAlchemy 3.1.1, SQLite, Flask-WTF for CSRF, and the `openfoodfacts` SDK for food search. The QA toolchain (Black, Ruff, Mypy, pytest) is well-defined and all versions are verified. The architecture follows a clean layered pattern: pure-Python business logic modules (`calculator.py`, `nutrition.py`) that routes delegate to, a single blueprint, and a flat module layout. This separation is what makes the mandatory unit tests straightforward and keeps Mypy happy.

The primary risks are: (1) incomplete auth removal causing runtime crashes and CI failures — this requires a grep-driven checklist, not a file-by-file review; (2) wrong Mifflin-St-Jeor formula constants producing systematically incorrect downstream values — must be unit-tested against a published reference value immediately; and (3) the Open Food Facts API being called without a service abstraction, causing flaky CI tests and potential rate-limiting during the demo. All three risks are avoidable with the patterns documented in the research.

---

## Key Findings

### Recommended Stack

The stack is project-constrained with minor version updates required. Flask should be updated from 3.1.0 to 3.1.3; python-dotenv from 1.0.1 to 1.2.2. Flask-Login must be removed entirely — it is not in scope and its presence will cause failures. The `openfoodfacts` SDK (5.0.1) is the recommended integration path for food search; it handles response normalization and is maintained by the Open Food Facts team, though its "beta API" caveat in the docs means calls should be wrapped in try/except.

The QA toolchain requires careful coordination: Black owns formatting (line-length 88), Ruff owns linting only — do not enable `ruff format` alongside Black or CI will conflict. Mypy should run with `--ignore-missing-imports` and `--disallow-untyped-defs`, not `--strict`, given the brownfield context.

**Core technologies:**
- Flask 3.1.3: web framework — project-constrained, update from 3.1.0
- Flask-SQLAlchemy 3.1.1: ORM — already at latest; use SQLAlchemy 2.x `Mapped[]` style throughout
- SQLite (stdlib): storage — correct for single-user, zero-ops
- Flask-WTF 1.2.2: forms and CSRF — keep even without auth; CSRF matters in browser apps
- openfoodfacts 5.0.1: food search SDK — preferred over raw `requests` calls
- pytest 9.0.2 + pytest-flask 1.3.0: test runner — Flask 3.0 compatible
- Black 26.3.1 + Ruff 0.15.7 + Mypy 1.19.1: QA toolchain — version-lock all three

**Remove:** Flask-Login 0.6.3, email-validator (transitive), werkzeug password hashing imports.

### Expected Features

All research aligns on the same feature set. The dependency chain is strict: profile data must exist before any calculation is possible, and calculations must be complete before the dashboard can display meaningful information. The feature set is well-bounded and achievable within the sprint structure.

**Must have (table stakes):**
- User profile (age, height, weight, sex, activity level, goal) — single row, onboarding flow on first run
- BMR calculation via Mifflin-St-Jeor — pure function, unit-testable, formula constants verified
- TDEE from BMR + PAL activity multiplier — five activity levels with defined constants
- Calorie goal with lose/maintain/gain modifier (−15%/0%/+10%) — project-defined values
- Macro goals: 25% protein / 30% fat / 45% carbs — project-defined split
- Manual food entry with gram-based portion input — name, amount_g, per-100g macros
- Portion scaling: `scaled = per_100g * amount_g / 100` — isolated to `nutrition.py`
- Daily nutrient summation — sum of all FoodEntry rows for a date
- Dashboard with actual vs. goal (Soll/Ist) for calories and macros
- Colour-coded progress indicators (grey/green/orange/red based on % of goal)
- SQLite persistence via restructured SQLAlchemy models

**Should have (differentiators):**
- Open Food Facts API lookup — pre-fills food entry form from product search
- Daily history view by date — `/history?date=YYYY-MM-DD`
- Edit and delete food entries — correct mistakes
- Daily summary block (remaining kcal, macro percentages)
- Python `logging` module integration — per module, log profile saves and food events

**Defer (if time permits):**
- `/health` endpoint — 10 lines, do last
- Automated deployment (Render/Railway) — only if CD step needed for marks
- Monitoring script — lowest priority

**Explicitly cut (Won't Have):**
- Login/registration/sessions — remove existing auth system entirely
- Weight log model — remove `WeightLog`; profile `weight_kg` is sufficient
- Calorie/macro charts — colour-coded progress bars are sufficient visual feedback
- Barcode scanner, social features, AI recommendations

### Architecture Approach

The target architecture is a flat single-blueprint Flask app with strict module boundaries. Business logic lives exclusively in `calculator.py` (BMR/TDEE/macros) and `nutrition.py` (portion scaling, daily summation, progress status) — both are pure Python with no Flask or SQLAlchemy imports, making them directly unit-testable without an app context. Routes (`routes.py`) are the only module permitted to touch `db.session`. The `api_client.py` wrapper is stateless and raises a custom `APIError` on failure, which routes catch and flash to the user.

**Major components:**
1. `app/__init__.py` (app factory) — creates Flask app, registers single blueprint, inits SQLAlchemy; enables isolated test instances
2. `app/models.py` — `UserProfile` (single row, id=1), `FoodEntry` (date-keyed), `DailyGoal` (upserted on profile save), `FoodsCache` (optional API cache)
3. `app/calculator.py` — pure functions: `calculate_bmr`, `calculate_tdee`, `calculate_calorie_goal`, `calculate_macros`; no imports beyond stdlib
4. `app/nutrition.py` — pure functions: `scale_to_portion`, `sum_daily`, `progress_status`; no imports beyond stdlib
5. `app/routes.py` — single blueprint: onboarding, dashboard, food CRUD, history, API search; calls calculator/nutrition, reads/writes models
6. `app/api_client.py` — Open Food Facts wrapper: search by name, normalize to internal dict, raise `APIError` on failure
7. `tests/` — unit tests for calculator/nutrition (no app context needed) + integration tests via Flask test client

### Critical Pitfalls

1. **Incomplete auth removal (phantom `current_user`)** — Flask-Login references are spread across `__init__.py`, `models.py`, routes, and templates. After removal, grep the entire codebase for `current_user`, `login_required`, `flask_login`, `LoginManager`, `UserMixin` before declaring auth removal done. App must boot and serve a page on a fresh DB — this is the acceptance test.

2. **Wrong Mifflin-St-Jeor constants** — The female constant is −161 (not −160, not −162). A 30-year-old, 70 kg, 175 cm male must yield BMR = 1673.75 kcal. Write this test first, before implementing the route that calls it. Any BMR result outside 1200–2200 kcal for a healthy adult is a red flag.

3. **No profile on first run** — With auth removed, there is no registration flow to create a profile row. Every route that reads `UserProfile` will crash with `NoneType` if this is not handled. Implement an onboarding redirect guard (`if db.session.get(UserProfile, 1) is None: redirect(url_for("main.onboarding"))`) before any other route logic is written.

4. **Open Food Facts API called without mocking in tests** — The API is rate-limited at ~10 req/min. Any test hitting the real endpoint will cause flaky CI and potential IP bans. The `api_client.py` abstraction exists specifically to enable `unittest.mock.patch` on the service boundary in tests. Never call the real API in pytest.

5. **Black/Ruff formatting conflict in CI** — Both tools can claim ownership of formatting. Configure `pyproject.toml` with `line-length = 88` for both; use Black for formatting and Ruff for linting only (no `ruff format`). Lock both versions in `requirements-dev.txt`. A single misconfigured `pyproject.toml` means a permanently red CI badge.

---

## Implications for Roadmap

Based on research, the architecture's layered build order maps directly to a 4-sprint structure. Each sprint delivers a testable, demonstrable slice and clears blockers for the next.

### Phase 1: Foundation — Auth Removal, Models, Calculator
**Rationale:** Everything downstream depends on (a) the app booting cleanly without Flask-Login and (b) the calculator producing correct values. These are hard blockers — no dashboard, no tests, and no CI can work until this phase is complete. Start here, finish here before touching UI.
**Delivers:** Clean app boot on fresh DB; `UserProfile`, `FoodEntry`, `DailyGoal` models in SQLAlchemy 2.x `Mapped` style; `calculator.py` with BMR/TDEE/macro functions; 5+ unit tests passing; onboarding form and redirect guard; `requirements.txt` cleaned of Flask-Login.
**Addresses:** Profile setup, BMR/TDEE calculation, macro goals (all Must Have features)
**Avoids:** Pitfalls 1 (phantom auth), 2 (wrong BMR formula), 4 (Mypy on models), 8 (no profile on first run), 15 (stale requirements)

### Phase 2: Core Tracking Loop — Food Entry, Dashboard, History
**Rationale:** With the calculator and models in place, the food entry and dashboard flows are straightforward route + template work. Establishing `nutrition.py` (portion scaling, daily summation, progress status) as a pure module before writing any route ensures the anti-pattern of inline calculation is never introduced. Integration tests are written here.
**Delivers:** Manual food entry with portion scaling; daily nutrient summation; dashboard with Soll/Ist display and colour-coded progress bars; edit/delete entries; history view by date; `nutrition.py` module with unit tests.
**Uses:** Flask routes, SQLAlchemy date-keyed queries, Bootstrap colour classes for progress indicators
**Implements:** Data flows 2 (food entry), 4 (dashboard render), 5 (history view) from ARCHITECTURE.md
**Avoids:** Pitfalls 3 (inline scaling), 6 (UTC date mismatch), 9 (macro rounding), 11 (logic in templates), 12 (goal modifier applied twice), 13 (undefined progress thresholds)

### Phase 3: CI/CD and Quality Gates
**Rationale:** CI must be established before Sprint 4 adds external API complexity. A green pipeline at this stage proves the foundation is solid and gives a safety net for the final sprint. Diagrams produced now while the architecture is fresh, not retroactively.
**Delivers:** GitHub Actions workflow (Black check → Ruff lint → Mypy → pytest); `pyproject.toml` with coordinated Black/Ruff/Mypy config; `conftest.py` with in-memory SQLite fixtures; `WTF_CSRF_ENABLED = False` in TestConfig; `/health` endpoint; Klassendiagramm and Sequenzdiagramm CI/CD drafted.
**Avoids:** Pitfalls 5 (Black/Ruff conflict), 10 (DB state between tests), 14 (CSRF 400 in CI), 16 (diagrams as afterthoughts)

### Phase 4: Open Food Facts Integration and Polish
**Rationale:** The API integration is isolated to `api_client.py` and slots into the existing food entry flow without touching the calculator or dashboard. Deferring to Sprint 4 means CI is already green before adding external dependency complexity. Logging is added here as required by the project spec.
**Delivers:** `api_client.py` wrapping the `openfoodfacts` SDK; `FoodsCache` model for result caching; food search route pre-filling the add_food form; Python `logging` integration across all modules; mocked API tests; optional: automated deployment configuration.
**Avoids:** Pitfall 7 (live API in CI — mock at `api_client` boundary from day one)

### Phase Ordering Rationale

- Phase 1 before everything: auth removal and model rewrite are hard blockers; nothing can be tested or built on top of a broken app foundation.
- Phase 2 before CI: routes and templates must exist for integration tests to be meaningful; building CI against an empty app provides false confidence.
- Phase 3 before Phase 4: the API integration adds external complexity and rate-limiting risk; a green pipeline must exist before that complexity is introduced.
- The layered build order in ARCHITECTURE.md (Layers 0→1→2→3→4→5) maps exactly to this phase sequence: pure functions first, then models, then routes, then integration tests, then external API.

### Research Flags

Phases with standard patterns (skip additional research):
- **Phase 1:** Well-documented Flask app factory pattern; SQLAlchemy 2.x `Mapped` style is official and documented; Mifflin-St-Jeor formula constants verified against Medscape.
- **Phase 2:** Standard Flask CRUD patterns; date filtering and portion math are deterministic; no unknowns.
- **Phase 3:** GitHub Actions Python workflow is a solved problem; Black/Ruff/Mypy configuration is documented.

Phases that may need targeted research during planning:
- **Phase 4:** The `openfoodfacts` SDK carries a "beta API" caveat despite its 5.0.1 stable release. Verify the `api.product.text_search()` method signature against the live SDK before implementation — the interface may have changed. Specifically confirm which fields are reliably present in `nutriments` (some products have missing macro data). Rate limit policy is documented in a GitHub issue (not official policy) — treat as ~10 req/min until confirmed otherwise.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified against PyPI March 2026; project constraints are explicit in spec |
| Features | HIGH | Must Have features come directly from project spec and existing code audit; Should Have ordering is well-reasoned |
| Architecture | HIGH | Pattern is standard Flask; build order derived from direct dependency analysis of the codebase |
| Pitfalls | HIGH | Critical pitfalls identified from direct codebase inspection; formula verified against medical reference |

**Overall confidence:** HIGH

### Gaps to Address

- **openfoodfacts SDK field reliability:** The SDK normalizes responses but some products lack `proteins_100g`, `fat_100g`, or `carbohydrates_100g` fields. The route or `api_client.py` must handle missing nutriment data gracefully (return `None` or a default, not a `KeyError`). Validate actual API response structure against 2–3 real product queries before writing the integration.

- **Progress threshold values:** ARCHITECTURE.md and PITFALLS.md define slightly different threshold ranges (ARCHITECTURE: <0.95/0.95–1.05/>1.05; PITFALLS: <90%/90–100%/100–110%/>110%). These need to be reconciled into a single set of named constants before any template or `nutrition.py` code is written. The project spec's exact wording should be the deciding source.

- **Deployment target (optional):** If the grader requires a live URL, the deployment platform (Render, Railway, PythonAnywhere) needs to be chosen and configured. This is explicitly marked optional in the spec but should be decided at the start of Phase 3 so CI can include a CD step if needed.

---

## Sources

### Primary (HIGH confidence)
- Project specification: `nutritrack-projektdoku.md` — MoSCoW priorities, sprint plan, user stories, formula constants
- Existing codebase: `app/__init__.py`, `app/models.py`, `app/routes/`, `app/templates/` — direct inspection
- Flask PyPI: https://pypi.org/project/Flask/ — version 3.1.3 verified March 2026
- Flask-SQLAlchemy PyPI: https://pypi.org/project/Flask-SQLAlchemy/ — version 3.1.1 verified March 2026
- SQLAlchemy 2.0 Mapped annotations: https://docs.sqlalchemy.org/en/14/orm/extensions/mypy.html
- Mypy docs: https://mypy.readthedocs.io/en/stable/existing_code.html
- Flask application factory pattern: https://flask.palletsprojects.com/en/stable/patterns/
- Mifflin-St-Jeor reference values: https://reference.medscape.com/calculator/846/mifflin-st-jeor-equation
- pytest PyPI: https://pypi.org/project/pytest/ — version 9.0.2 verified March 2026
- pytest-flask PyPI: https://pypi.org/project/pytest-flask/ — version 1.3.0 verified March 2026
- Black PyPI: https://pypi.org/project/black/ — version 26.3.1 verified March 2026
- Ruff PyPI: https://pypi.org/project/ruff/ — version 0.15.7 verified March 2026
- Mypy PyPI: https://pypi.org/project/mypy/ — version 1.19.1 verified March 2026

### Secondary (MEDIUM confidence)
- openfoodfacts PyPI: https://pypi.org/project/openfoodfacts/ — version 5.0.1 verified; "beta API" caveat in docs despite stable classifier
- openfoodfacts Python SDK usage: https://openfoodfacts.github.io/openfoodfacts-python/usage/
- Open Food Facts API docs: https://openfoodfacts.github.io/openfoodfacts-server/api/ — v2 confirmed stable, v3 in development
- Flask large-app structure: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure
- pytest-flask-sqlalchemy: https://github.com/jeancochrane/pytest-flask-sqlalchemy — test isolation patterns

### Tertiary (LOW confidence)
- Open Food Facts rate limit: https://github.com/openfoodfacts/openfoodfacts-server/issues/8818 — ~10 req/min from GitHub issue, not official policy; treat as indicative
- Diet/nutrition app market context: https://media.market.us/diet-and-nutrition-apps-statistics/ — market data for consumer apps; different context from academic single-user tool

---
*Research completed: 2026-03-24*
*Ready for roadmap: yes*
