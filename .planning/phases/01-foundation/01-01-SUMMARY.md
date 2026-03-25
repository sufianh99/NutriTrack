---
phase: 01-foundation
plan: "01"
subsystem: database
tags: [flask, sqlalchemy, wtforms, sqlite, black, ruff, mypy]

# Dependency graph
requires: []
provides:
  - "Clean Flask app factory without Flask-Login"
  - "UserProfile, DailyGoal, FoodEntry models (SQLAlchemy 2.x Mapped style)"
  - "OnboardingForm with 6 fields and German labels"
  - "Single blueprint stub (app/routes.py) with index/onboarding/dashboard routes"
  - "pyproject.toml with Black, Ruff, Mypy configuration"
  - "requirements.txt updated to Flask 3.1.3, no Flask-Login"
  - "TestConfig in config.py for pytest"
affects:
  - "01-02 (calculator and nutrition modules)"
  - "01-03 (full route/template implementation)"

# Tech tracking
tech-stack:
  added:
    - "pyproject.toml (Black 88 line-length, Ruff E/F/I/W rules, Mypy ignore_missing_imports + disallow_untyped_defs)"
  patterns:
    - "SQLAlchemy 2.x Mapped[type] = mapped_column(...) style for all models"
    - "Single blueprint (main) registered in create_app via app/routes.py"
    - "db.session.get(Model, id) instead of Model.query (SQLAlchemy 2.x)"
    - "UserProfile always accessed via id=1 (single-user app)"

key-files:
  created:
    - "app/routes.py (single blueprint with index/onboarding/dashboard stubs)"
    - "app/templates/onboarding.html (stub, Plan 03 will implement full form)"
    - "pyproject.toml (QA tool configuration)"
    - "instance/.gitkeep (ensures SQLite directory exists)"
  modified:
    - "app/__init__.py (removed Flask-Login, clean app factory)"
    - "app/models.py (replaced User/Meal/WeightLog with UserProfile/DailyGoal/FoodEntry)"
    - "app/forms.py (replaced all forms with OnboardingForm)"
    - "app/templates/base.html (removed auth nav conditionals)"
    - "app/templates/dashboard.html (stub, removed current_user references)"
    - "requirements.txt (Flask 3.1.3, removed Flask-Login and Werkzeug pin)"
    - "config.py (added TestConfig for pytest)"

key-decisions:
  - "Flask-Login removed entirely — project spec says Won't Have: Login, single-user app"
  - "SQLAlchemy 2.x Mapped[] typed columns chosen for Mypy compatibility"
  - "Single flat app/routes.py replaces app/routes/ directory for simplicity"
  - "pyproject.toml uses Black for formatting, Ruff for linting (not ruff format)"

patterns-established:
  - "Auth-free: no login_required, no current_user, no LoginManager anywhere in codebase"
  - "OnboardingForm uses German labels for all user-facing text"
  - "Blueprint named 'main' — all routes prefixed with main.*"

requirements-completed:
  - RSTC-01
  - RSTC-02
  - RSTC-03

# Metrics
duration: 5min
completed: "2026-03-25"
---

# Phase 1 Plan 01: Foundation Cleanup Summary

**Flask-Login removed, replaced with UserProfile/DailyGoal/FoodEntry models (SQLAlchemy 2.x), OnboardingForm with German labels, and pyproject.toml QA config**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-25T08:05:10Z
- **Completed:** 2026-03-25T08:10:21Z
- **Tasks:** 1
- **Files modified:** 14 (7 modified, 7 deleted, 4 created)

## Accomplishments

- Removed all Flask-Login auth code (LoginManager, login_required, current_user, UserMixin) — zero grep hits remaining
- Replaced legacy User/Meal/WeightLog models with UserProfile/DailyGoal/FoodEntry using SQLAlchemy 2.x Mapped type annotations
- Created OnboardingForm with all 6 body data fields and German labels (Alter, Groesse, Gewicht, Geschlecht, Aktivitaetslevel, Ziel)
- App boots cleanly on fresh SQLite DB (`python -c "from app import create_app; app = create_app()"` exits 0)
- Created pyproject.toml with Black (88), Ruff (E/F/I/W), Mypy (ignore_missing_imports + disallow_untyped_defs) configuration

## Task Commits

Each task was committed atomically:

1. **Task 1: Remove auth system, rewrite models/forms/routes, update deps** - `81a12f7` (feat)

## Files Created/Modified

- `app/__init__.py` - Clean app factory: db only, single blueprint, no Flask-Login
- `app/models.py` - UserProfile, DailyGoal, FoodEntry with Mapped[] type annotations
- `app/forms.py` - OnboardingForm only (6 fields, German labels, proper validators)
- `app/routes.py` - Single 'main' blueprint stub with index/onboarding/dashboard routes
- `app/templates/base.html` - Navbar with Dashboard + Profil links, no auth conditionals
- `app/templates/dashboard.html` - Minimal stub (Plan 03 implements full dashboard)
- `app/templates/onboarding.html` - Minimal stub (Plan 03 implements full form)
- `requirements.txt` - Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Flask-WTF 1.2.2, python-dotenv 1.2.2
- `config.py` - Config class + TestConfig (TESTING=True, in-memory SQLite, WTF_CSRF_ENABLED=False)
- `pyproject.toml` - QA tool configuration (Black, Ruff, Mypy)
- `instance/.gitkeep` - Ensures instance directory exists for SQLite
- Deleted: `app/routes/` directory (auth.py, main.py, tracking.py, __init__.py)
- Deleted: `app/templates/auth/` (login.html, register.html)
- Deleted: `app/templates/tracking/` (add_meal.html, add_weight.html, history.html, profile.html)
- Deleted: `app/templates/index.html`

## Decisions Made

- Used proper German umlauts in OnboardingForm labels (Größe, Männlich, Weiblich, Mäßig aktiv, Aktivitätslevel) for correct user-facing text
- Kept Bootstrap 5 CDN and footer unchanged from base.html restructure
- dashboard.html and onboarding.html intentionally stubbed — Plan 03 will implement full content

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created missing instance/ directory**
- **Found during:** Task 1 (app boot verification)
- **Issue:** The worktree did not have an `instance/` directory; SQLite `db.create_all()` fails with `OperationalError: unable to open database file` without it
- **Fix:** Created `instance/` directory with `.gitkeep` placeholder file
- **Files modified:** `instance/.gitkeep` (created)
- **Verification:** App boots successfully after fix
- **Committed in:** `81a12f7` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary for app to boot on fresh checkout. No scope creep.

## Issues Encountered

None beyond the auto-fixed instance directory issue above.

## User Setup Required

None - no external service configuration required.

## Known Stubs

- `app/templates/onboarding.html` — stub placeholder, Plan 03 will implement the full OnboardingForm template
- `app/templates/dashboard.html` — stub placeholder, Plan 03 will implement the full dashboard with Soll/Ist-Vergleich
- `app/routes.py` onboarding/dashboard routes — GET-only stubs, Plan 03 adds POST handling and calculator wiring

These stubs are intentional. Plan 01's goal (bootable app, clean foundation) is achieved. Full UI delivered in Plan 03.

## Next Phase Readiness

- Foundation complete — app boots with no auth, new models, and OnboardingForm
- Plan 02 can now create `app/calculator.py` and `app/nutrition.py` (pure Python, no Flask context needed)
- Plan 03 can wire the OnboardingForm POST handler, calculator, and full templates
- QA tools (Black, Ruff, Mypy) configured and ready for CI pipeline (Plan 03)
- TestConfig available for pytest fixtures (Plan 02)

---
*Phase: 01-foundation*
*Completed: 2026-03-25*
