# Roadmap: NutriTrack

**Milestone:** v1
**Granularity:** Coarse
**Requirements:** 28 v1 requirements
**Coverage:** 28/28 mapped

---

## Phases

- [ ] **Phase 1: Foundation** - Remove auth, rewrite models, implement calculator, onboarding form
- [ ] **Phase 2: Tracking Loop** - Food entry CRUD, portion scaling, dashboard with Soll/Ist comparison
- [ ] **Phase 3: Quality Gates** - CI pipeline, test suite, diagrams, health endpoint, logging
- [ ] **Phase 4: API Integration & Deployment** - Open Food Facts search, deployment, README

---

## Phase Details

### Phase 1: Foundation
**Goal**: The app boots cleanly as a single-user tool, user can set up their profile, and all calorie/macro calculations produce correct values
**Depends on**: Nothing (first phase)
**Requirements**: RSTC-01, RSTC-02, RSTC-03, PROF-01, PROF-02, PROF-03, PROF-04, PROF-05, PROF-06
**Success Criteria** (what must be TRUE):
  1. App starts on a fresh SQLite database without any login page, session errors, or Flask-Login import errors
  2. User is redirected to onboarding on first run and can submit age, height, weight, gender, activity level, and goal
  3. After submitting the onboarding form, user can view their calculated daily calorie goal and macro targets (protein/fat/carbs in grams)
  4. A 30-year-old, 70 kg, 175 cm male with sedentary activity and maintain goal produces BMR = 1673.75 kcal and calorie goal = 1673.75 kcal (verified reference value)
**Plans:** 3 plans

Plans:
- [ ] 01-01-PLAN.md — Auth removal, model rewrite, forms, dependencies, pyproject.toml
- [ ] 01-02-PLAN.md — Calculator module (BMR/TDEE/macros) with TDD unit tests
- [ ] 01-03-PLAN.md — Onboarding/profile routes, templates, dashboard display

**UI hint**: yes

### Phase 2: Tracking Loop
**Goal**: User can log food for today, see scaled nutrition values sum up, and compare their intake against goals with colour-coded feedback
**Depends on**: Phase 1
**Requirements**: FOOD-01, FOOD-02, FOOD-03, FOOD-04, FOOD-05, FOOD-07, DASH-01, DASH-02, DASH-03
**Success Criteria** (what must be TRUE):
  1. User can add a food entry with name, portion size in grams, and per-100g nutrition values, and the app displays the scaled values for their portion
  2. User can edit or delete any food entry on the current day's log
  3. Dashboard shows today's total calories and macros alongside the goal values (Soll/Ist), with progress bars that turn green at 90-100% and orange/red above 100%
  4. Dashboard daily summary shows remaining calories and macro percentages consumed
  5. User can navigate to a past date and view the food entries and totals for that day
**Plans**: TBD
**UI hint**: yes

### Phase 3: Quality Gates
**Goal**: The project meets all academic QA requirements — a green CI pipeline, a complete test suite, mandatory diagrams, structured logging, and a health endpoint
**Depends on**: Phase 2
**Requirements**: QUAL-01, QUAL-02, QUAL-03, QUAL-04, QUAL-05, QUAL-06, QUAL-07
**Success Criteria** (what must be TRUE):
  1. Pushing a commit triggers GitHub Actions and the pipeline runs Black, Ruff, Mypy, and pytest sequentially, with a passing green badge
  2. The test suite contains at minimum 5 unit tests covering BMR, TDEE, calorie goal, macro calculation, and portion scaling, plus integration tests for profile save, food entry add, and dashboard response
  3. A Klassendiagramm of the application models and a Sequenzdiagramm of the CI/CD pipeline exist as committed artefacts
  4. GET /health returns {"status": "ok"} with HTTP 200
  5. Application startup, profile saves, and food entry events are written to application logs via the Python logging module
**Plans**: TBD

### Phase 4: API Integration & Deployment
**Goal**: User can search the Open Food Facts database to auto-fill food entries, the app is deployable to a live host, and the project is documented for submission
**Depends on**: Phase 3
**Requirements**: FOOD-06, DEPL-01, DEPL-02
**Success Criteria** (what must be TRUE):
  1. User can type a food name in the food entry form and select from Open Food Facts search results, which auto-populate the nutrition fields
  2. The app can be deployed to Render, Railway, or PythonAnywhere from the repository with no manual configuration beyond environment variables
  3. The README contains setup instructions, an architecture overview, and a usage guide sufficient for a grader to run the app locally
**Plans**: TBD

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/3 | Planning complete | - |
| 2. Tracking Loop | 0/? | Not started | - |
| 3. Quality Gates | 0/? | Not started | - |
| 4. API Integration & Deployment | 0/? | Not started | - |

---

*Roadmap created: 2026-03-24*
*Last updated: 2026-03-25 after Phase 1 planning*
