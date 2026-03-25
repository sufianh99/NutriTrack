# Requirements: NutriTrack

**Defined:** 2026-03-24
**Core Value:** Nutzer können ihren individuellen Tagesbedarf berechnen und ihre tatsächliche Nahrungsaufnahme dagegen tracken — mit sofort sichtbarem Soll/Ist-Vergleich und farblicher Ampel.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Restructuring

- [x] **RSTC-01**: Existing auth system (Flask-Login, login/register routes, password hashing) is completely removed
- [x] **RSTC-02**: Existing models are replaced with project-spec-compliant schema (users, daily_goals, food_entries, foods_cache)
- [x] **RSTC-03**: App runs as single-user without any login requirement

### Profile & Calculation

- [x] **PROF-01**: User can enter body data via onboarding form (age, height_cm, weight_kg, gender, activity_level, goal)
- [x] **PROF-02**: App calculates BMR using Mifflin-St-Jeor formula (male: 10×weight + 6.25×height - 5×age + 5, female: ... - 161)
- [x] **PROF-03**: App calculates TDEE by multiplying BMR with PAL factor (1.2 / 1.375 / 1.55 / 1.725 / 1.9)
- [x] **PROF-04**: App derives calorie goal from TDEE and user goal (lose: ×0.85, maintain: ×1.0, gain: ×1.10)
- [x] **PROF-05**: App calculates macro goals (protein 25% ÷4, fat 30% ÷9, carbs 45% ÷4)
- [x] **PROF-06**: User can view their calculated daily calorie and macro goals

### Food Tracking

- [x] **FOOD-01**: User can manually add a food entry (name, amount_g, calories, protein, fat, carbs per 100g)
- [x] **FOOD-02**: App scales nutrition values based on portion size (value = per_100g / 100 × amount_g)
- [x] **FOOD-03**: App sums all food entries for a given date into daily totals
- [x] **FOOD-04**: User can edit an existing food entry
- [x] **FOOD-05**: User can delete an existing food entry
- [x] **FOOD-06**: User can search food via Open Food Facts API and auto-fill nutrition values
- [x] **FOOD-07**: User can view food entries for past dates (history by date)

### Dashboard

- [x] **DASH-01**: Dashboard shows actual vs. goal comparison (Soll/Ist) for calories and all 3 macros
- [x] **DASH-02**: Dashboard displays colour-coded progress (neutral <90%, green 90-100%, orange/red >100%)
- [x] **DASH-03**: Dashboard shows daily summary (total kcal consumed, remaining, macro percentages)

### Quality Assurance

- [x] **QUAL-01**: Minimum 5 unit tests for calculation logic (BMR, TDEE, calorie goal, macros, portion scaling)
- [x] **QUAL-02**: Integration tests for profile save, food entry add, dashboard response
- [x] **QUAL-03**: GitHub Actions CI pipeline runs Black, Ruff, Mypy, and pytest on push/PR
- [x] **QUAL-04**: Klassendiagramm of the application models
- [x] **QUAL-05**: Sequenzdiagramm of the CI/CD pipeline
- [x] **QUAL-06**: Python logging module integrated across app modules
- [x] **QUAL-07**: /health endpoint returns {"status": "ok"} with HTTP 200

### Deployment

- [x] **DEPL-01**: App is deployable to Render / Railway / PythonAnywhere
- [x] **DEPL-02**: README with setup instructions, architecture overview, and usage guide

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Monitoring

- **MNTR-01**: Monitoring script that checks /health endpoint periodically
- **MNTR-02**: GitHub Action for automated health checks

### Extended Tracking

- **EXTD-01**: Meal type categorization (breakfast, lunch, dinner, snack)
- **EXTD-02**: Weekly/monthly summary reports

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Login / Registration / Sessions | Won't Have per project spec — single-user app |
| Mobile App | Won't Have — web-only |
| Barcode Scanner | Won't Have — requires camera API, too complex |
| Social Features / Chatbot | Won't Have — not in project scope |
| Weight Logging (separate from profile) | Weight is a profile attribute for BMR only |
| Charts / Graphs (Chart.js etc.) | Colour-coded progress bars are sufficient; avoids frontend complexity |
| Multi-user support | Single-user by design — no user_id FKs needed |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| RSTC-01 | Phase 1 | Complete |
| RSTC-02 | Phase 1 | Complete |
| RSTC-03 | Phase 1 | Complete |
| PROF-01 | Phase 1 | Complete |
| PROF-02 | Phase 1 | Complete |
| PROF-03 | Phase 1 | Complete |
| PROF-04 | Phase 1 | Complete |
| PROF-05 | Phase 1 | Complete |
| PROF-06 | Phase 1 | Complete |
| FOOD-01 | Phase 2 | Complete |
| FOOD-02 | Phase 2 | Complete |
| FOOD-03 | Phase 2 | Complete |
| FOOD-04 | Phase 2 | Complete |
| FOOD-05 | Phase 2 | Complete |
| FOOD-06 | Phase 4 | Complete |
| FOOD-07 | Phase 2 | Complete |
| DASH-01 | Phase 2 | Complete |
| DASH-02 | Phase 2 | Complete |
| DASH-03 | Phase 2 | Complete |
| QUAL-01 | Phase 3 | Complete |
| QUAL-02 | Phase 3 | Complete |
| QUAL-03 | Phase 3 | Complete |
| QUAL-04 | Phase 3 | Complete |
| QUAL-05 | Phase 3 | Complete |
| QUAL-06 | Phase 3 | Complete |
| QUAL-07 | Phase 3 | Complete |
| DEPL-01 | Phase 4 | Complete |
| DEPL-02 | Phase 4 | Complete |

**Coverage:**
- v1 requirements: 28 total
- Mapped to phases: 28
- Unmapped: 0

---
*Requirements defined: 2026-03-24*
*Last updated: 2026-03-24 after roadmap creation — traceability complete*
