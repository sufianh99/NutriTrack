# Phase 1: Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-25
**Phase:** 01-foundation
**Areas discussed:** Onboarding flow, Profile editing, Results display, Activity level labels
**Mode:** --auto (all decisions auto-selected)

---

## Onboarding Flow

| Option | Description | Selected |
|--------|-------------|----------|
| Redirect to /onboarding | When no profile exists, redirect all routes to onboarding form; after submit redirect to dashboard | * |
| Inline setup on index | Show onboarding fields directly on the landing page | |
| Modal overlay | Show onboarding as a modal on first visit | |

**User's choice:** [auto] Redirect to /onboarding (recommended default)
**Notes:** Standard pattern for single-user apps with required profile setup. Clean separation of concerns.

---

## Profile Editing

| Option | Description | Selected |
|--------|-------------|----------|
| Editable at /profile | User can re-edit all profile fields anytime, triggers recalculation | * |
| One-time onboarding only | Profile is set once during onboarding, no editing | |

**User's choice:** [auto] Editable at /profile (recommended default)
**Notes:** Users need to update weight/activity as they progress. Recalculation on save keeps goals current.

---

## Results Display

| Option | Description | Selected |
|--------|-------------|----------|
| Dashboard shows goals | Calculated goals shown as Soll values on dashboard — no separate results page | * |
| Separate results page | Dedicated page showing calculation breakdown after onboarding | |

**User's choice:** [auto] Dashboard shows goals (recommended default)
**Notes:** Dashboard is the natural home for Soll/Ist comparison (Phase 2). Showing goals there from Phase 1 establishes the pattern.

---

## Activity Level Labels

| Option | Description | Selected |
|--------|-------------|----------|
| German labels | All UI in German, matching existing app language | * |
| English labels | Switch to English for international accessibility | |
| Bilingual | German primary with English tooltips | |

**User's choice:** [auto] German labels (recommended default)
**Notes:** Existing app is fully German (forms, flash messages, footer). Consistency matters.

---

## Claude's Discretion

- Form validation ranges
- Error message wording
- Onboarding page layout
- Blueprint structure decisions

## Deferred Ideas

None
