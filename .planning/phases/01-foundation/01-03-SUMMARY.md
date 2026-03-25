---
phase: 01-foundation
plan: 03
subsystem: routes-templates
tags: [routes, templates, onboarding, dashboard, profile, calculator-integration]
dependency_graph:
  requires: [01-01, 01-02]
  provides: [onboarding-flow, profile-edit, dashboard-soll-display]
  affects: []
tech_stack:
  added: []
  patterns:
    - SQLAlchemy 2.x select() API for DailyGoal upsert query
    - Shared _save_profile_and_goals() helper for DRY onboarding/profile routes
    - OnboardingForm(obj=profile) for pre-filling edit form
key_files:
  created:
    - app/templates/profile.html
  modified:
    - app/routes.py
    - app/templates/onboarding.html
    - app/templates/dashboard.html
    - app/templates/base.html
decisions:
  - "_save_profile_and_goals() shared between onboarding and profile routes to avoid duplication"
  - "db.session.merge() used for upsert semantics on both UserProfile and DailyGoal"
  - "checkpoint:human-verify auto-approved (auto_chain_active=true)"
metrics:
  duration: "~2 minutes"
  completed_date: "2026-03-25"
  tasks_completed: 2
  files_modified: 5
---

# Phase 01 Plan 03: Onboarding, Profile, and Dashboard Routes Summary

**One-liner:** Full onboarding-to-dashboard flow wiring OnboardingForm to Mifflin-St-Jeor calculator chain with DailyGoal upsert and German Soll-values display.

## What Was Built

Complete user-facing flow for Phase 1:

1. `app/routes.py` — fully implemented with `index`, `onboarding` (GET+POST), `profile` (GET+POST), `dashboard` routes plus `_get_profile()` and `_save_profile_and_goals()` helpers.
2. `app/templates/onboarding.html` — Bootstrap 5 form with all 6 fields (age, height_cm, weight_kg, gender, activity_level, goal), German labels, CSRF token, field error display.
3. `app/templates/profile.html` — Same form structure, pre-filled via `OnboardingForm(obj=profile)`, with back-to-dashboard link. New file created.
4. `app/templates/dashboard.html` — 4-card layout showing Kalorienziel, Protein, Fett, Kohlenhydrate from today's DailyGoal. Shows info alert if no goal yet.
5. `app/templates/base.html` — Navbar Profil link updated from `main.onboarding` to `main.profile`.

## Verification Results

All 5 automated route tests passed:
- Root `/` with no profile returns 302 redirect to `/onboarding`
- `GET /onboarding` returns 200
- `POST /onboarding` with valid data returns 302 redirect to `/dashboard`
- `GET /dashboard` after onboarding returns 200 with `kcal` in body
- `GET /profile` after onboarding returns 200

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | d27de33 | feat(01-03): implement onboarding, profile, and dashboard routes and templates |

## Deviations from Plan

None — plan executed exactly as written.

## Checkpoint Handling

Task 2 (checkpoint:human-verify) was auto-approved because `_auto_chain_active: true` in `.planning/config.json`. The automated verification (5 route tests) confirmed the flow works correctly before auto-approval.

## Known Stubs

None. All 4 dashboard cards display real calculated values from DailyGoal. The `goal` context variable is populated by the calculator chain on every profile save.

## Self-Check: PASSED
