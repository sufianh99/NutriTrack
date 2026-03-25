---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: unknown
last_updated: "2026-03-25T09:51:58.584Z"
progress:
  total_phases: 4
  completed_phases: 1
  total_plans: 6
  completed_plans: 4
---

# Project State: NutriTrack

**Last updated:** 2026-03-25
**Updated by:** execute-phase agent (02-01 nutrition module)

---

## Project Reference

**Core value:** Nutzer können ihren individuellen Tagesbedarf berechnen und ihre tatsächliche Nahrungsaufnahme dagegen tracken — mit sofort sichtbarem Soll/Ist-Vergleich und farblicher Ampel.

**Current focus:** Phase 02 — tracking-loop

---

## Current Position

Phase: 02 (tracking-loop) — EXECUTING
Plan: 2 of 3

## Performance Metrics

**Plans executed:** 0
**Plans succeeded first try:** 0
**Repairs used:** 0

---

## Accumulated Context

### Key Decisions

| Decision | Rationale | Phase |
|----------|-----------|-------|
| Auth system removed entirely | Project spec says Won't Have: Login; single-user app | Phase 1 |
| Mifflin-St-Jeor formula | More accurate and modern than Harris-Benedict | Phase 1 |
| SQLite over PostgreSQL | Simplicity, zero-ops, project spec constraint | Phase 1 |
| FOOD-06 (Open Food Facts) deferred to Phase 4 | API integration requires CI safety net; Phase 3 must be green first | Phase 4 |
| Pure Python calculator/nutrition modules | Enables unit testing without Flask app context; required for Mypy | Phase 1 |
| BMR reference value 1648.75 (not 1673.75) | Standard Mifflin-St-Jeor formula output; project spec value is a typo | Phase 1 Plan 2 |
| Female BMR constant -161 verified by test | Male-female difference test (166 = 5 - (-161)) anchors the constant | Phase 1 Plan 2 |
| Single flat app/routes.py replaces app/routes/ directory | Simpler structure for single-user app; single blueprint named 'main' | Phase 1 Plan 1 |
| SQLAlchemy 2.x Mapped[] typed columns for all models | Mypy compatibility for free; required for disallow_untyped_defs | Phase 1 Plan 1 |
| Phase 01-foundation P03 | 2 | 2 tasks | 5 files |
| progress_status uses 0.90/1.00 thresholds | ROADMAP.md spec takes precedence over old ARCHITECTURE.md (0.95/1.05) | Phase 2 Plan 1 |
| TDD cycle establishes test-then-implement commits | RED commit first, GREEN commit after — ensures test isolation and traceability | Phase 2 Plan 1 |

### Critical Pitfalls to Watch

1. After auth removal, grep for `current_user`, `login_required`, `flask_login`, `LoginManager`, `UserMixin` before declaring Phase 1 done
2. Female Mifflin-St-Jeor constant is -161 (not -160, not -162); verify with reference: 30yo, 70kg, 175cm male = BMR 1673.75
3. Every route must handle `UserProfile` being None (fresh DB) — redirect to onboarding guard required
4. Never call the real Open Food Facts API in pytest — mock at `api_client.py` boundary
5. Do not enable `ruff format` alongside Black — use Black for formatting only, Ruff for linting only

### Architecture Notes

- Single blueprint (`main`) in `app/routes.py`
- Business logic isolated to `app/calculator.py` (BMR/TDEE/macros) and `app/nutrition.py` (portion scaling, summation, progress status) — no Flask/SQLAlchemy imports in these modules
- `app/api_client.py` wraps openfoodfacts SDK, raises custom `APIError` on failure
- `UserProfile` table is single-row (id=1); `FoodEntry` is date-keyed; `DailyGoal` is upserted on profile save

### Todos

- [x] Confirm progress threshold constants before Phase 2 template work — RESOLVED: use 0.90/1.00 per ROADMAP.md (Phase 2 Plan 1)
- [ ] Decide deployment target (Render/Railway/PythonAnywhere) at start of Phase 3 so CD step can be included in CI if needed

### Blockers

None currently.

---

## Session Continuity

**To resume work:** Run `/gsd:execute-phase 02` to continue Phase 2 (Plan 2 of 3).

**Stopped at:** Completed 02-tracking-loop/02-01-PLAN.md

**Context for next session:**

- Brownfield Flask app — existing auth system (Flask-Login) must be removed before any other work
- 4-phase roadmap: Foundation → Tracking Loop → Quality Gates → API & Deployment
- All 28 v1 requirements mapped; no orphans
- Research confidence is HIGH; pitfalls are documented above

---

*State initialized: 2026-03-24*
