# Feature Landscape

**Domain:** Nutrition tracking web application (single-user, academic Flask project)
**Researched:** 2026-03-24
**Context:** Brownfield Flask app. Auth system must be removed. MoSCoW priorities defined in project docs.

---

## Table Stakes

Features that any nutrition tracker must have or the product feels broken. These map directly to the Must Have MoSCoW tier.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| User profile (age, height, weight, sex, activity, goal) | Without body data, calorie targets are meaningless — users have no baseline | Low | Single-user app: one profile row, no auth, onboarding flow on first launch |
| BMR calculation (Mifflin-St-Jeor) | Users expect a personalised number, not a hardcoded 2000 kcal default | Low | Pure function: `bmr(weight, height, age, sex)` — highly testable |
| TDEE from BMR + activity factor (PAL) | BMR alone is not actionable; activity multiplier produces the actual daily burn estimate | Low | PAL factors: 1.2 / 1.375 / 1.55 / 1.725 / 1.9 |
| Calorie goal derived from objective (lose/maintain/gain) | Users need a target, not just a burn estimate | Low | -15% / 0% / +10% modifiers — project-defined |
| Macro goals (protein / fat / carbs) | Macros are the second thing every tracker shows after calories | Low | 25% protein / 30% fat / 45% carbs split — project-defined |
| Manual food entry (name, weight/portion, kcal, protein, fat, carbs) | Core logging action — without this, nothing else works | Low-Med | Form with portion scaling (grams entered → per-100g stored) |
| Portion scaling (entered grams → actual nutrient values) | Users enter 150 g of chicken, not "1 serving" | Low | `value = per100g * grams / 100` |
| Daily nutrient summation | The only output that matters on a day-to-day basis | Low | Sum of all food_entries for a given date |
| Dashboard with actual vs. goal (Soll/Ist) | Primary reason to open the app — "how am I doing today?" | Med | Calories + 3 macros, for today's date |
| Colour-coded progress indicator | Visual shorthand: green = on track, orange/red = over | Low | Thresholds: <90% neutral, 90-100% green, >100% orange-red |
| SQLite persistence | App is useless if data disappears on restart | Low | Already in project; SQLAlchemy models need restructuring |

---

## Should Have (Differentiators for This Project)

Features that distinguish a competent implementation from a minimal one. Not expected on day one, but the project spec calls for them in Sprint 4.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Open Food Facts API lookup | Eliminates manual macro lookup for common packaged foods; user types product name, gets pre-filled form | Med | REST GET to `https://world.openfoodfacts.org/cgi/search.pl`; cache results in `foods_cache` table to avoid repeated calls; no API key required |
| Daily history view (by date) | Users need to review past days, not just today | Low-Med | Route `/history/<date>` filtering `food_entries` by `date` column; list of dates with entry counts |
| Edit food entry | Mistakes happen — users need to correct portion sizes or wrong macros | Low | PUT/PATCH route on food_entry; pre-filled form |
| Delete food entry | Accidental entries must be removable | Low | DELETE route; confirm before removing |
| Daily summary (text or numeric) | A small summary block — total kcal consumed, remaining, macro percentages — rounds out the dashboard | Low | Derived from the same summation query; minimal template work |
| Python `logging` module integration | Good engineering practice; required by project spec | Low | Logger per module; log profile saves, food adds, API calls, errors |

---

## Could Have (Nice-to-Have, Low Priority)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| `/health` endpoint | Enables uptime monitoring; trivial to add | Very Low | Returns `{"status": "ok"}` with HTTP 200; useful for deployment checks |
| Automated deployment (Render / Railway / PythonAnywhere) | Demonstrates full SDLC; adds CD section to CI diagram | Med | Optional per project spec; worth doing if time allows |
| Monitoring script (cron/GitHub Action) | Demonstrates operational thinking; hits `/health` on a schedule | Low | Simple Python or `curl` in a GitHub Action |

---

## Anti-Features

Features to explicitly NOT build. These are Won't Have per project spec, but also bad ideas for this context.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Login / registration / sessions | Project spec says Won't Have; adds auth complexity, Flask-Login dependency, password hashing, session management — all overhead with zero benefit in a single-user app | Remove existing auth system; replace with onboarding flow that populates the single profile row |
| Multi-user support | The entire data model (goals, entries) only makes sense per-user when there are multiple users; single-user removes this complexity entirely | Store profile in a `profile` table (single row, no user_id FK needed) |
| Barcode scanner | Requires camera API / mobile browser integration; complex, out of scope, not a web-first feature | Open Food Facts text search covers the same use case adequately |
| Social features (sharing, leaderboards, comments) | Not in scope; significantly increases surface area | No alternative needed |
| AI meal recommendations / meal planning | Modern commercial trackers have this; it's not achievable in a single-developer academic Flask project without an LLM API dependency | Stick to deterministic Mifflin-St-Jeor math |
| Weight logging (separate from profile) | Existing app has a `WeightLog` model; this is feature creep for this project's goals — the profile has `weight_kg` for BMR, that's sufficient | Remove `WeightLog` model and associated routes; simplifies schema |
| Calorie charts / graphs over time | Charting libraries (Chart.js etc.) are tempting but add frontend complexity for marginal academic value; the history view with numbers is sufficient | Colour-coded progress bars in the dashboard cover visual feedback adequately |

---

## Feature Dependencies

```
Profile (age, height, weight, sex, activity, goal)
  → BMR calculation
      → TDEE calculation
          → Calorie goal (+ goal modifier)
              → Macro goals
                  → Dashboard Soll/Ist display

Manual food entry (name, grams, per-100g macros)
  → Portion scaling
      → Daily nutrient summation
          → Dashboard Soll/Ist display
          → Daily summary block
          → History view (requires date on entry)

Edit / Delete food entry
  → Requires food_entries to exist (Manual food entry)

Open Food Facts API lookup
  → Pre-fills manual food entry form (optional path, not blocking)
  → foods_cache table (optional, reduces API calls)

Colour-coded progress indicator
  → Requires daily summation + calorie/macro goals
```

---

## MVP Recommendation

Given the sprint structure and academic deadline, build in this order:

**Sprint 1 (Foundation):** Profile + BMR/TDEE/macro calculation. This unlocks all goal display and is fully unit-testable — satisfies the "5 unit tests" requirement early.

**Sprint 2 (Core Loop):** Manual food entry + portion scaling + daily summation + dashboard with colour-coded progress. This is the product. Everything else is polish.

**Sprint 3 (CI/CD):** GitHub Actions pipeline with Black, Ruff, Mypy, pytest. Diagrams. README. These are hard academic requirements, not optional.

**Sprint 4 (Should Have):** Open Food Facts API, history view, edit/delete entries, daily summary, logging. These differentiate a good submission from a minimal one.

Defer until "if time allows":
- `/health` endpoint: 10 lines of code, do it at the end of Sprint 3 or Sprint 4 if time permits
- Automated deployment: do it only if the CI diagram needs to show a CD step for marks
- Monitoring script: lowest priority

---

## Existing Code Inventory (Brownfield Context)

The current app has these features that need **removal or replacement**:

| Existing Feature | Action Required | Reason |
|-----------------|-----------------|--------|
| `User` model with password hash, email, username | Remove auth fields; replace with single `Profile` model | Won't Have: no login |
| `flask_login`, `werkzeug.security` dependencies | Remove from `__init__.py`, `models.py`, routes | No auth = no need for these |
| `WeightLog` model | Remove | Out of scope; weight is a profile attribute only |
| Auth routes (`auth.py`) | Delete entire file | No login/register |
| `@login_required` decorators on all tracking routes | Remove | Single-user app, all routes are public |
| `MealForm`, `WeightForm` in `forms.py` | Replace `MealForm` with `FoodEntryForm`; remove `WeightForm` | Rename to match new domain model |
| Calorie goal hardcoded to `default=2000` | Replace with calculated TDEE value from profile | Must Have: BMR/TDEE calculation |

The `Meal` model is structurally close to what's needed (`name`, `calories`, `protein_g`, `carbs_g`, `fat_g`, `meal_type`, `logged_at`) — it can be renamed to `FoodEntry` and `user_id` FK replaced with a direct profile reference or dropped if single-profile design is used.

---

## Sources

- Project documentation: `/c/Repos/NutriTrack/nutritrack-projektdoku.md` (MoSCoW priorities, sprint plan, user stories)
- Project context: `/c/Repos/NutriTrack/.planning/PROJECT.md`
- [Open Food Facts API documentation](https://openfoodfacts.github.io/openfoodfacts-server/api/) — confirmed: no API key required, v2 stable, v3 in development (use v2)
- [Diet and Nutrition Apps Statistics 2026](https://media.market.us/diet-and-nutrition-apps-statistics/) — market context for table stakes features
- [Top Nutrition APIs for App Developers 2026](https://www.spikeapi.com/blog/top-nutrition-apis-for-developers-2026) — confirmed Open Food Facts as the dominant free option
- [User Perspectives of Diet-Tracking Apps (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8103297/) — academic study on what users actually need from trackers

**Confidence:** HIGH for Must Have features (directly from project spec + existing code audit). MEDIUM for Should Have ordering rationale (based on complexity estimates and dependency analysis). LOW for market "table stakes" claims (consumer app market differs significantly from an academic single-user tool).
