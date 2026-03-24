# Project State: NutriTrack

**Last updated:** 2026-03-24
**Updated by:** roadmapper (initial creation)

---

## Project Reference

**Core value:** Nutzer können ihren individuellen Tagesbedarf berechnen und ihre tatsächliche Nahrungsaufnahme dagegen tracken — mit sofort sichtbarem Soll/Ist-Vergleich und farblicher Ampel.

**Current focus:** Phase 1 — Foundation (auth removal, model rewrite, calculator, onboarding)

---

## Current Position

**Phase:** 1 - Foundation
**Plan:** None started
**Status:** Not started

**Progress:**
```
[Phase 1: Foundation       ] [ ] Not started
[Phase 2: Tracking Loop    ] [ ] Not started
[Phase 3: Quality Gates    ] [ ] Not started
[Phase 4: API & Deployment ] [ ] Not started
```

Overall: 0/4 phases complete

---

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

- [ ] Confirm progress threshold constants before Phase 2 template work (project spec vs ARCHITECTURE.md discrepancy: <0.95/0.95-1.05/>1.05 vs <90%/90-100%/>100%)
- [ ] Decide deployment target (Render/Railway/PythonAnywhere) at start of Phase 3 so CD step can be included in CI if needed

### Blockers

None currently.

---

## Session Continuity

**To resume work:** Run `/gsd:plan-phase 1` to begin planning Phase 1.

**Context for next session:**
- Brownfield Flask app — existing auth system (Flask-Login) must be removed before any other work
- 4-phase roadmap: Foundation → Tracking Loop → Quality Gates → API & Deployment
- All 28 v1 requirements mapped; no orphans
- Research confidence is HIGH; pitfalls are documented above

---

*State initialized: 2026-03-24*
