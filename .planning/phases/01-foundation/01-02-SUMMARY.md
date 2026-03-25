---
phase: 01-foundation
plan: 02
subsystem: testing
tags: [python, pytest, mifflin-st-jeor, calculator, tdd, bmr, tdee, macros]

# Dependency graph
requires: []
provides:
  - Pure-function BMR/TDEE/macro calculator module (app/calculator.py)
  - pytest test suite with 10 passing unit tests (tests/test_calculator.py)
  - conftest.py with app/client fixtures for Flask integration tests
  - TestConfig class in config.py for in-memory SQLite test isolation
affects:
  - 01-03 (uses calculator functions in routes)
  - Phase 2 tracking loop (nutrition calculations build on this)
  - CI/CD pipeline (Phase 3 runs these tests)

# Tech tracking
tech-stack:
  added: [pytest, pytest-flask, flask-sqlalchemy, flask-login, flask-wtf]
  patterns:
    - TDD RED-GREEN-REFACTOR cycle for pure-function modules
    - Pure Python calculator modules with no Flask/SQLAlchemy imports
    - pytest.approx for floating-point BMR/TDEE comparison

key-files:
  created:
    - app/calculator.py
    - tests/__init__.py
    - tests/conftest.py
    - tests/test_calculator.py
  modified:
    - config.py

key-decisions:
  - "Use 1648.75 as reference BMR (standard Mifflin-St-Jeor formula) not 1673.75 (project spec typo)"
  - "Female constant is -161 verified by male-female difference test (166 = 5 - (-161))"
  - "Macros: protein 25%/4kcal, fat 30%/9kcal, carbs 45%/4kcal — rounded to 1 decimal"
  - "Lazy imports in conftest.py fixtures to avoid flask_sqlalchemy import errors in pure-Python tests"

patterns-established:
  - "Pure module pattern: calculator.py has no Flask/SQLAlchemy imports — independently testable"
  - "TestConfig: in-memory SQLite + WTF_CSRF_ENABLED=False for isolated test runs"
  - "pytest.approx with abs=0.01 for BMR/TDEE float comparisons"

requirements-completed: [PROF-02, PROF-03, PROF-04, PROF-05]

# Metrics
duration: 8min
completed: 2026-03-25
---

# Phase 01 Plan 02: Calculator Module Summary

**Mifflin-St-Jeor BMR/TDEE/macro calculator as pure Python module with 10 passing TDD unit tests**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-25T08:05:11Z
- **Completed:** 2026-03-25T08:13:00Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 5

## Accomplishments

- Implemented `calculate_bmr` with correct male (+5) and female (-161) constants; reference value 1648.75 verified
- Implemented `calculate_tdee` with all 5 PAL factors (sedentary 1.2 through very_active 1.9)
- Implemented `apply_goal_modifier` with lose/maintain/gain modifiers (0.85/1.00/1.10)
- Implemented `calculate_macros` with 25%/30%/45% split, rounded to 1 decimal place
- All 10 unit tests pass; module is importable without Flask or SQLAlchemy

## Task Commits

Each TDD phase committed atomically:

1. **RED phase: failing tests** - `52a7b6b` (test)
2. **GREEN phase: implementation + TestConfig** - `12fa723` (feat)

_TDD task: 2 commits (test RED, feat GREEN)_

## Files Created/Modified

- `app/calculator.py` - Pure-function BMR/TDEE/macro calculator, no Flask/SQLAlchemy imports
- `tests/__init__.py` - Empty package marker for tests directory
- `tests/conftest.py` - pytest fixtures (app, client) with lazy imports
- `tests/test_calculator.py` - 10 unit tests covering all calculator functions
- `config.py` - Added TestConfig (in-memory SQLite, CSRF disabled)

## Decisions Made

- **BMR reference value 1648.75 not 1673.75:** Standard Mifflin-St-Jeor formula for 30yo/70kg/175cm male yields 1648.75. Project spec value 1673.75 appears to be a typo; the formula is authoritative.
- **Lazy fixture imports in conftest.py:** Placing `from app import create_app, db` inside fixture functions (not at module top level) allows calculator tests to run even if flask_sqlalchemy installation is missing. Protects test collection.
- **installed flask-sqlalchemy and related packages:** System Python lacked flask_sqlalchemy; installed from requirements.txt to enable app package imports.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Missing packages prevented test collection**
- **Found during:** Task 1 (RED phase)
- **Issue:** System Python had Flask but not flask_sqlalchemy, flask_login, flask_wtf — importing `app` package triggered ModuleNotFoundError during test collection
- **Fix:** Installed all packages from requirements.txt via pip; moved conftest.py Flask imports inside fixtures to isolate pure-Python tests from Flask dependency
- **Files modified:** tests/conftest.py (lazy imports), pip environment
- **Verification:** `pytest tests/test_calculator.py -v` collects and runs 10 tests
- **Committed in:** 52a7b6b (RED phase commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Required to enable test execution. No scope creep. Calculator tests remain purely independent of Flask fixtures.

## Issues Encountered

- `flask_sqlalchemy` not installed on system Python — resolved by installing requirements.txt dependencies (Rule 3 deviation).
- conftest.py imports restructured to lazy (inside fixtures) to prevent collection errors in pure-Python test contexts.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Calculator module complete and tested; ready for Plan 03 (Flask app restructuring / routes)
- All 10 unit tests pass; provides test infrastructure baseline for CI/CD (Phase 3)
- conftest.py app/client fixtures available for integration tests in later plans

---
*Phase: 01-foundation*
*Completed: 2026-03-25*
