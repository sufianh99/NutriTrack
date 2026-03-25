# Phase 1: Foundation - Context

**Gathered:** 2026-03-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Remove the existing Flask-Login auth system entirely. Replace current models (User, Meal, WeightLog) with project-spec-compliant schema (UserProfile, DailyGoal, FoodEntry). Implement Mifflin-St-Jeor calculator as pure Python module. Build onboarding form for single-user profile setup. App must boot cleanly on fresh SQLite DB without any login requirement.

</domain>

<decisions>
## Implementation Decisions

### Onboarding Flow
- **D-01:** When no UserProfile exists (fresh DB), all routes redirect to `/onboarding`
- **D-02:** Onboarding form collects: age, height_cm, weight_kg, gender (male/female), activity_level (5 PAL levels), goal (lose/maintain/gain)
- **D-03:** After onboarding submission, app calculates BMR/TDEE/calorie goal/macros, stores results in DailyGoal, and redirects to dashboard

### Profile Editing
- **D-04:** User can re-edit their profile at `/profile` at any time — same fields as onboarding
- **D-05:** Saving profile recalculates and updates DailyGoal automatically

### Results Display
- **D-06:** No separate results page — calculated goals are shown on the dashboard (Soll values)
- **D-07:** Dashboard is the landing page for users who have completed onboarding

### UI Language
- **D-08:** All form labels and UI text in German (consistent with existing app: "Mahlzeit", "Kalorien", etc.)
- **D-09:** Activity levels displayed with German descriptive labels (e.g., "Sitzend (wenig Bewegung)" for sedentary)
- **D-10:** Goals displayed as: "Abnehmen", "Halten", "Zunehmen"

### Auth Removal
- **D-11:** Delete auth blueprint, RegistrationForm, LoginForm, Flask-Login imports entirely
- **D-12:** Remove Flask-Login from requirements.txt, remove email-validator transitive dependency
- **D-13:** Replace `current_user.is_authenticated` navbar logic with profile-exists check
- **D-14:** Remove WeightLog model (weight is a profile attribute for BMR only, per Out of Scope)

### Claude's Discretion
- Form validation ranges (reasonable defaults for age, height, weight)
- Error message wording
- Onboarding page layout within Bootstrap 5 constraints
- Whether to use a single blueprint or keep separate blueprints

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specification
- `.planning/PROJECT.md` — Core value, constraints, key decisions, architecture notes
- `.planning/REQUIREMENTS.md` — RSTC-01 through PROF-06 acceptance criteria for this phase
- `.planning/research/ARCHITECTURE.md` — Data model design, calculator module patterns
- `.planning/research/PITFALLS.md` — Auth removal grep checklist, Mifflin-St-Jeor constant pitfall (-161 for female)

### Existing Code (to be replaced)
- `app/models.py` — Current User/Meal/WeightLog models (must be fully replaced)
- `app/forms.py` — Current forms including auth forms (auth forms deleted, MealForm adapted later)
- `app/__init__.py` — Flask-Login initialization (must be removed)
- `app/routes/auth.py` — Auth blueprint (must be deleted)
- `app/routes/main.py` — Current index route with `current_user` logic (must be rewritten)
- `app/templates/base.html` — Navbar with auth-conditional links (must be rewritten)

### Reference Values
- `CLAUDE.md` §Mifflin-St-Jeor — Formula constants and verification value (30yo, 70kg, 175cm male = BMR 1673.75)
- `CLAUDE.md` §Technology Stack — Pinned versions for requirements.txt

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `config.py` — Config class with SQLite URI and SECRET_KEY — keep as-is
- `app/templates/base.html` — Bootstrap 5 layout shell with navbar, flash messages, footer — adapt (remove auth links)
- `app/static/style.css` — Custom styles — keep
- `run.py` — App entry point — keep as-is
- `app/forms.py:MealForm` — Pattern for Flask-WTF form with validators — reference for onboarding form structure

### Established Patterns
- Flask app factory pattern in `app/__init__.py` with `create_app()`
- Blueprint-based route organization (`main`, `auth`, `tracking`)
- German UI language throughout all templates and form labels
- Bootstrap 5 via CDN for styling
- Flash messages for user feedback

### Integration Points
- `app/__init__.py` — Must remove Flask-Login, update blueprint registration, update context processor
- `app/routes/main.py` — Index route becomes onboarding guard + dashboard redirect
- New files needed: `app/calculator.py` (pure Python, no Flask imports), onboarding form in `app/forms.py`, onboarding template, profile template

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches. Key constraints from project spec:
- Mifflin-St-Jeor formula (not Harris-Benedict)
- PAL factors: 1.2 / 1.375 / 1.55 / 1.725 / 1.9
- Goal modifiers: lose ×0.85, maintain ×1.0, gain ×1.10
- Macro split: protein 25%, fat 30%, carbs 45%
- Single-row UserProfile (id=1), no multi-user support

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-03-25*
