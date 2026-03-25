---
phase: 02-tracking-loop
plan: 03
subsystem: dashboard
tags: [dashboard, soll-ist, progress-bars, date-navigation, nutrition-calculations]
dependency_graph:
  requires: [02-01]
  provides: [DASH-01, DASH-02, DASH-03, FOOD-07]
  affects: [app/routes.py, app/templates/dashboard.html, app/forms.py]
tech_stack:
  added: []
  patterns:
    - entry_rows merged list pattern to avoid zip in Jinja2
    - date.fromisoformat() with try/except for safe query param parsing
    - DailyGoal always queried for today (not display_date) for consistent Soll values
    - Progress bar width capped at 100% with [pct, 100] | min Jinja2 filter
    - bg-{status} Bootstrap class only applied when status is non-empty (neutral = default blue)
key_files:
  created: []
  modified:
    - app/routes.py
    - app/templates/dashboard.html
    - app/forms.py
decisions:
  - "Dashboard always uses today's DailyGoal for Soll values regardless of display_date — retroactive goal changes are not meaningful"
  - "entry_rows is a pre-merged list of {entry, scaled} dicts to avoid needing zip filter in Jinja2"
  - "Edit/delete actions only shown when display_date == today — past entries are intentionally read-only"
  - "DeleteForm added to forms.py to provide CSRF tokens for delete buttons in the dashboard"
metrics:
  duration: "~8 minutes"
  completed_date: "2026-03-25"
  tasks_completed: 2
  files_modified: 3
---

# Phase 02 Plan 03: Dashboard Soll/Ist View Summary

**One-liner:** Date-aware dashboard with colour-coded Soll/Ist progress bars, daily food log with scaled nutrition values, and prev/next date navigation.

## What Was Built

The dashboard route was completely rewritten to support:
1. **Date navigation** (`?date=YYYY-MM-DD`) — parse via `date.fromisoformat()` with fallback
2. **Soll/Ist progress bars** for calories, protein, fat, and carbs using `scale_nutrients()`, `sum_daily_nutrients()`, and `progress_status()` from `app/nutrition.py`
3. **Daily summary section** (DASH-03) showing consumed kcal, remaining kcal, and macro percentages
4. **Food log table** iterating `entry_rows` (pre-merged list of entry+scaled dicts)
5. **Past-date read-only guard** — edit/delete actions only rendered when `display_date == today`

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Rewrite dashboard route with date awareness | 8827697 | app/routes.py, app/forms.py |
| 2 | Rewrite dashboard.html with Soll/Ist, progress bars, food log, date nav | 0563f55 | app/templates/dashboard.html |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical Functionality] Added DeleteForm to forms.py**
- **Found during:** Task 1
- **Issue:** `DeleteForm` was listed in the plan context as coming from Plan 02-02 (parallel wave). Since both plans run simultaneously, neither could rely on the other's changes. The dashboard route requires `DeleteForm` for CSRF tokens on delete buttons.
- **Fix:** Added `DeleteForm(FlaskForm)` class to `app/forms.py` with a docstring explaining its purpose. Also added `StringField` to the wtforms import (for future use by Plan 02-02's `FoodEntryForm`).
- **Files modified:** app/forms.py
- **Commit:** 8827697

### Notes on Parallel Execution

Plan 02-03 runs in parallel with Plan 02-02 (food CRUD routes). The dashboard template references `url_for('main.add_food')`, `url_for('main.edit_food')`, and `url_for('main.delete_food')` inside `{% if display_date == today %}` guards. These will raise `BuildError` until Plan 02-02's routes are registered. Verification was performed against past dates to avoid this issue. The orchestrator merge will resolve this.

## Known Stubs

None. All template variables are computed from real DB data via nutrition.py functions.

## Self-Check

### Files Exist
- [x] C:/Repos/NutriTrack/app/routes.py — modified
- [x] C:/Repos/NutriTrack/app/templates/dashboard.html — modified
- [x] C:/Repos/NutriTrack/app/forms.py — modified

### Commits Exist
- [x] 8827697 — Task 1 (route + forms)
- [x] 0563f55 — Task 2 (template)

## Self-Check: PASSED
