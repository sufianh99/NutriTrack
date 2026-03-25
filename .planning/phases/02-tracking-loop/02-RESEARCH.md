# Phase 2: Tracking Loop — Research

**Researched:** 2026-03-25
**Domain:** Flask CRUD routes, Jinja2 templating, date-keyed food entries, portion scaling, Soll/Ist dashboard
**Confidence:** HIGH

---

## Summary

Phase 2 builds on a fully verified Phase 1 foundation. The `FoodEntry` model with all required columns (`name`, `amount_g`, `calories_per_100g`, `protein_per_100g`, `fat_per_100g`, `carbs_per_100g`, `date`) is already committed and migrated via `db.create_all()`. The `DailyGoal` model stores per-day calorie and macro targets, already upserted on profile save.

The primary new work is: (1) a `FoodEntryForm` for manual food entry, (2) CRUD routes (add, edit, delete) keyed by date, (3) a pure-function `nutrition.py` module for portion scaling and daily summation, and (4) a rewritten `dashboard.html` template that shows Soll/Ist comparison with Bootstrap progress bars and colour coding. Date navigation for history is a URL parameter on the dashboard route.

The outstanding todo in STATE.md flags a threshold discrepancy: the requirements say "green 90-100%, orange/red above 100%" while an earlier ARCHITECTURE.md reference used 0.95/1.05. **The requirements specification wins**: use 0.90 and 1.00 as thresholds, matching the success criteria in ROADMAP.md exactly.

**Primary recommendation:** Add `app/nutrition.py` as a pure-function module (no Flask imports), add `FoodEntryForm` to `app/forms.py`, add CRUD routes to `app/routes.py`, rewrite `dashboard.html` to show Soll/Ist with progress bars, add `food_log.html` for the daily food list, and add a date picker/navigation pattern to the dashboard URL.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FOOD-01 | User can manually add a food entry (name, amount_g, calories, protein, fat, carbs per 100g) | FoodEntry model already exists with all columns; need FoodEntryForm + POST /food/add route |
| FOOD-02 | App scales nutrition values based on portion size (value = per_100g / 100 × amount_g) | Pure-function in nutrition.py — `scale_nutrients(entry)`; no external library needed |
| FOOD-03 | App sums all food entries for a given date into daily totals | Pure-function in nutrition.py — `sum_daily_entries(entries)`; query by FoodEntry.date |
| FOOD-04 | User can edit an existing food entry | GET /food/<id>/edit + POST handler; pre-fill FoodEntryForm with existing row |
| FOOD-05 | User can delete an existing food entry | POST /food/<id>/delete (POST-only, no GET to prevent accidental deletion) |
| FOOD-07 | User can view food entries for past dates (history by date) | Dashboard route accepts `?date=YYYY-MM-DD` query param; date navigation UI in template |
| DASH-01 | Dashboard shows Soll/Ist comparison for calories and all 3 macros | nutrition.py returns totals; route passes totals+goals to template; template renders paired values |
| DASH-02 | Dashboard displays colour-coded progress (neutral <90%, green 90-100%, orange/red >100%) | Bootstrap progress bars with dynamic CSS class from nutrition.py `progress_status()` function |
| DASH-03 | Dashboard shows daily summary (total kcal consumed, remaining, macro percentages) | Computed in nutrition.py or template filter; remaining = goal - actual; percentage = actual/goal×100 |
</phase_requirements>

---

## Project Constraints (from CLAUDE.md)

- Tech stack is locked: Python/Flask, SQLite, Jinja2, pytest — no alternatives
- QA tools: Black, Ruff, Mypy — must remain passing after every plan
- No auth, no multi-user, no Chart.js — colour-coded progress bars are the approved UI pattern
- Flask-Login has been removed; no re-introduction
- Pure-function modules (no Flask/SQLAlchemy imports) required for calculator and nutrition logic — enables unit testing without app context
- SQLAlchemy 2.x `Mapped[]` typed columns required on all models
- `db.session.get()` not deprecated `Model.query` for lookups by primary key
- German language for all user-visible labels and flash messages

---

## Standard Stack

### Core (already installed — no new packages needed for Phase 2)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 3.1.3 | Web framework, routing | Already in use |
| Flask-SQLAlchemy | 3.1.1 | ORM, FoodEntry CRUD | Already in use |
| Flask-WTF | 1.2.2 | FoodEntryForm with CSRF | Already in use |
| WTForms | (transitive) | Field types, validators | Already in use |
| SQLite | stdlib | Persistent storage | Already in use |

No new packages are required for Phase 2. All functionality is achievable with the existing installed stack.

**Installation:** No new packages — `requirements.txt` is unchanged for Phase 2.

---

## Architecture Patterns

### Recommended Project Structure After Phase 2

```
app/
├── __init__.py          # app factory (unchanged)
├── calculator.py        # BMR/TDEE/macros — pure functions (unchanged)
├── nutrition.py         # NEW: portion scaling, summation, progress_status
├── models.py            # unchanged — FoodEntry already defined
├── forms.py             # ADD FoodEntryForm
├── routes.py            # ADD food CRUD routes + date-aware dashboard
├── templates/
│   ├── base.html        # unchanged
│   ├── onboarding.html  # unchanged
│   ├── profile.html     # unchanged
│   ├── dashboard.html   # REWRITE: Soll/Ist + progress bars + food log inline
│   └── food_form.html   # NEW: add/edit food entry form
```

### Pattern 1: Pure-Function nutrition.py Module

**What:** Business logic for portion scaling, summation, and progress status lives in `app/nutrition.py` with no Flask or SQLAlchemy imports.
**When to use:** Any calculation that operates on plain data (numbers, dicts, lists) — not DB rows directly.
**Example:**

```python
# app/nutrition.py
# Source: Architecture Notes in STATE.md + CLAUDE.md convention

def scale_nutrients(
    amount_g: float,
    calories_per_100g: float,
    protein_per_100g: float,
    fat_per_100g: float,
    carbs_per_100g: float,
) -> dict[str, float]:
    """Scale per-100g values to the actual portion size."""
    factor = amount_g / 100.0
    return {
        "calories": round(calories_per_100g * factor, 1),
        "protein_g": round(protein_per_100g * factor, 1),
        "fat_g": round(fat_per_100g * factor, 1),
        "carbs_g": round(carbs_per_100g * factor, 1),
    }


def sum_daily_nutrients(entries: list[dict[str, float]]) -> dict[str, float]:
    """Sum scaled nutrients across all entries for a given day."""
    return {
        "calories": round(sum(e["calories"] for e in entries), 1),
        "protein_g": round(sum(e["protein_g"] for e in entries), 1),
        "fat_g": round(sum(e["fat_g"] for e in entries), 1),
        "carbs_g": round(sum(e["carbs_g"] for e in entries), 1),
    }


def progress_status(actual: float, goal: float) -> str:
    """Return Bootstrap colour class based on intake vs goal ratio.

    <90%  → "" (neutral/default)
    90-100% → "success" (green)
    >100%  → "danger" (red/orange)
    """
    if goal <= 0:
        return ""
    ratio = actual / goal
    if ratio < 0.90:
        return ""
    if ratio <= 1.00:
        return "success"
    return "danger"
```

### Pattern 2: Date-Aware Dashboard Route

**What:** The dashboard route accepts an optional `date` query parameter (`?date=YYYY-MM-DD`). If absent, defaults to `date.today()`. This single change enables FOOD-07 (history navigation) without a separate route.
**When to use:** Any feature that views data keyed by date.
**Example:**

```python
# app/routes.py — dashboard route update
from datetime import date, timedelta
from flask import request

@bp.route("/dashboard")
def dashboard():
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))

    # Resolve display date from query param or default to today
    date_str = request.args.get("date")
    try:
        display_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        display_date = date.today()

    today = date.today()
    goal = db.session.execute(
        select(DailyGoal).where(DailyGoal.date == today)
    ).scalar_one_or_none()

    entries = db.session.execute(
        select(FoodEntry).where(FoodEntry.date == display_date).order_by(FoodEntry.id)
    ).scalars().all()

    # Scale each entry and sum totals
    from app.nutrition import scale_nutrients, sum_daily_nutrients, progress_status
    scaled = [scale_nutrients(e.amount_g, e.calories_per_100g, e.protein_per_100g,
                              e.fat_per_100g, e.carbs_per_100g) for e in entries]
    totals = sum_daily_nutrients(scaled)

    # Compute progress statuses
    statuses = {}
    if goal:
        statuses = {
            "calories": progress_status(totals["calories"], goal.calorie_goal),
            "protein": progress_status(totals["protein_g"], goal.protein_goal),
            "fat": progress_status(totals["fat_g"], goal.fat_goal),
            "carbs": progress_status(totals["carbs_g"], goal.carb_goal),
        }

    prev_date = display_date - timedelta(days=1)
    next_date = display_date + timedelta(days=1)

    return render_template(
        "dashboard.html",
        profile=profile,
        goal=goal,
        entries=entries,
        scaled=scaled,
        totals=totals,
        statuses=statuses,
        display_date=display_date,
        today=today,
        prev_date=prev_date,
        next_date=next_date,
    )
```

### Pattern 3: Food Entry CRUD Routes

**What:** Three routes handle food management: POST-only add (from dashboard), GET+POST edit (pre-filled form), POST-only delete (no GET to avoid accidental deletion via link).
**When to use:** Standard Flask CRUD pattern for a date-keyed resource.
**Example:**

```python
# app/routes.py — food CRUD routes

@bp.route("/food/add", methods=["POST"])
def add_food():
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))
    form = FoodEntryForm()
    if form.validate_on_submit():
        entry = FoodEntry(
            date=date.today(),
            name=form.name.data,
            amount_g=form.amount_g.data,
            calories_per_100g=form.calories_per_100g.data,
            protein_per_100g=form.protein_per_100g.data,
            fat_per_100g=form.fat_per_100g.data,
            carbs_per_100g=form.carbs_per_100g.data,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Lebensmittel hinzugefügt.", "success")
    return redirect(url_for("main.dashboard"))


@bp.route("/food/<int:entry_id>/edit", methods=["GET", "POST"])
def edit_food(entry_id: int):
    entry = db.session.get(FoodEntry, entry_id)
    if entry is None:
        flash("Eintrag nicht gefunden.", "warning")
        return redirect(url_for("main.dashboard"))
    form = FoodEntryForm(obj=entry)
    if form.validate_on_submit():
        form.populate_obj(entry)
        db.session.commit()
        flash("Eintrag aktualisiert.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("food_form.html", form=form, entry=entry)


@bp.route("/food/<int:entry_id>/delete", methods=["POST"])
def delete_food(entry_id: int):
    entry = db.session.get(FoodEntry, entry_id)
    if entry:
        db.session.delete(entry)
        db.session.commit()
        flash("Eintrag gelöscht.", "success")
    return redirect(url_for("main.dashboard"))
```

### Pattern 4: FoodEntryForm

**What:** A WTForms `FlaskForm` for manual food entry, covering all `FoodEntry` columns except `date` (which is set to `date.today()` in the route).
**Example:**

```python
# app/forms.py addition

class FoodEntryForm(FlaskForm):
    name = StringField(
        "Lebensmittel", validators=[DataRequired(), Length(min=1, max=200)]
    )
    amount_g = FloatField(
        "Menge (g)", validators=[DataRequired(), NumberRange(min=0.1, max=5000)]
    )
    calories_per_100g = FloatField(
        "Kalorien pro 100g", validators=[DataRequired(), NumberRange(min=0, max=2000)]
    )
    protein_per_100g = FloatField(
        "Protein pro 100g (g)", validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    fat_per_100g = FloatField(
        "Fett pro 100g (g)", validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    carbs_per_100g = FloatField(
        "Kohlenhydrate pro 100g (g)", validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    submit = SubmitField("Speichern")
```

Note: `StringField` and `Length` validator must be imported — add `StringField` from `wtforms` and `Length` from `wtforms.validators` to the existing imports in `app/forms.py`.

### Pattern 5: Bootstrap Progress Bar with Dynamic Colour

**What:** Jinja2 template renders a Bootstrap progress bar whose `bg-*` class is computed from `progress_status()`.
**Example:**

```html
{# dashboard.html — one macro bar block (repeat for protein, fat, carbs) #}
{% set pct = (totals.calories / goal.calorie_goal * 100) | round(1) if goal and goal.calorie_goal > 0 else 0 %}
{% set status = statuses.get('calories', '') %}
<div class="mb-3">
  <div class="d-flex justify-content-between">
    <span>Kalorien</span>
    <span>{{ totals.calories }} / {{ "%.0f"|format(goal.calorie_goal) }} kcal</span>
  </div>
  <div class="progress">
    <div class="progress-bar {% if status %}bg-{{ status }}{% endif %}"
         role="progressbar"
         style="width: {{ [pct, 100] | min }}%"
         aria-valuenow="{{ pct }}"
         aria-valuemin="0"
         aria-valuemax="100">
    </div>
  </div>
</div>
```

When `status` is `""` (below 90%), the progress bar renders in Bootstrap's default blue. When `"success"`, it turns green. When `"danger"`, it turns red.

### Anti-Patterns to Avoid

- **Scaling in the template:** Never do `entry.calories_per_100g / 100 * entry.amount_g` inside Jinja2. Scaling must happen in `nutrition.py` and be passed to the template as pre-computed values.
- **Business logic in the route:** The route calls `nutrition.py` functions; it does not contain the arithmetic directly. This keeps functions unit-testable without app context.
- **GET route for delete:** Deleting via a `<a href>` exposes entries to accidental deletion (browser prefetching, link crawlers). Use `<form method="POST">` with a CSRF token.
- **Hardcoding today's date in food add:** The add route always assigns `date.today()` — users add food only for today. History viewing (FOOD-07) is read-only; no UI for adding food to past dates.
- **`Model.query` style:** Always use `db.session.execute(select(...))` — the legacy `Model.query` attribute is deprecated in SQLAlchemy 2.x.
- **Passing raw SQLAlchemy row objects to nutrition functions:** Convert to plain Python values before calling `scale_nutrients`; do not pass ORM objects into pure-function modules.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSRF protection on food forms | Custom token logic | Flask-WTF `FlaskForm` with `form.hidden_tag()` | Flask-WTF already integrated; omitting it creates XSS/XSRF exposure |
| Form validation (number ranges, required fields) | Manual `if not request.form.get(...)` checks | WTForms `DataRequired()`, `NumberRange()` | Edge cases: empty string, None, out-of-range; WTForms handles all cleanly |
| Progress percentage capping at 100% in template | `{% if pct > 100 %}100{% else %}{{ pct }}{% endif %}` | `[pct, 100] | min` Jinja2 filter | One-liner; Bootstrap progress bar overflows visually if `width > 100%` |
| Date parsing from query string | `datetime.strptime(...)` with manual try/except | `date.fromisoformat(date_str)` wrapped in try/except ValueError | ISO 8601 date strings (`YYYY-MM-DD`) parse cleanly; fromisoformat is stdlib |

**Key insight:** The stack already contains everything needed. Phase 2 is purely about wiring existing pieces together — no new dependencies, no custom infrastructure.

---

## Common Pitfalls

### Pitfall 1: Progress Threshold Ambiguity

**What goes wrong:** STATE.md todo flags a discrepancy between `<0.95/0.95-1.05/>1.05` (from an earlier ARCHITECTURE.md) and `<90%/90-100%/>100%` (from ROADMAP.md success criteria).
**Why it happens:** Two documents were written at different times with different thresholds.
**How to avoid:** The ROADMAP.md success criteria are the authoritative specification. Use `0.90` and `1.00` as thresholds in `progress_status()`. The earlier ARCHITECTURE.md reference is superseded.
**Resolution:** `ratio < 0.90` → neutral, `0.90 <= ratio <= 1.00` → green (success), `ratio > 1.00` → red (danger).

### Pitfall 2: DailyGoal Missing for the Displayed Date

**What goes wrong:** The `DailyGoal` row is only created when the user saves their profile. If a user navigates to a past date that predates their profile setup, `goal` will be `None`. The template must handle this gracefully.
**Why it happens:** `DailyGoal` is upserted on `_save_profile_and_goals()` — only called on profile save events, not retroactively.
**How to avoid:** Always wrap goal-dependent template blocks in `{% if goal %}`. For the dashboard, always use today's `DailyGoal` for the Soll values regardless of the displayed date — goals don't change by historical date. The route should query `DailyGoal` for `date.today()` even when displaying a past date's food entries.

### Pitfall 3: Scaled Values Not Passed as Parallel List

**What goes wrong:** The template iterates `entries` (ORM objects) and tries to access scaled values. Since scaling is done in Python, the template needs a way to access `scaled[i]` alongside `entries[i]`.
**Why it happens:** Jinja2 doesn't support calling Python functions; can't call `scale_nutrients()` in the template.
**How to avoid:** Either: (a) use `zip(entries, scaled)` in the template (`{% for entry, s in zip(entries, scaled) %}`), or (b) pre-build a list of dicts that merges entry data and scaled data in the route. Option (b) is cleaner for template readability. Pass `entry_rows = [{"entry": e, "scaled": s} for e, s in zip(entries, scaled)]` to the template.

Note: Jinja2 does not have a built-in `zip` filter. To use `zip` in a template, either register it as a global (`app.jinja_env.globals["zip"] = zip` in `create_app`) or merge the data in the route. Merging in the route is simpler and more explicit.

### Pitfall 4: Delete Form Redirect Loses the Display Date

**What goes wrong:** After deleting an entry while viewing a past date (`?date=2026-03-20`), the redirect goes to `url_for("main.dashboard")` — which defaults to today — losing the historical context.
**Why it happens:** The delete route doesn't know what date the user was viewing.
**How to avoid:** Include a hidden `date` field in the delete form, or pass a `next` parameter. Simplest approach: include the date in the form action URL: `action="{{ url_for('main.delete_food', entry_id=entry.id) }}"` and add a hidden `<input name="date" value="{{ display_date }}">`, then redirect to `url_for("main.dashboard", date=request.form.get("date"))` in the delete handler. For Phase 2, only current-day deletion is a hard requirement — past date deletion is a read-only view. Acceptable to redirect to today after delete.

### Pitfall 5: `form.populate_obj()` on FoodEntry Sets `date` from Form

**What goes wrong:** If `FoodEntryForm` includes a date field (it should not), `populate_obj(entry)` would overwrite the entry's date.
**Why it happens:** WTForms `populate_obj()` sets all form fields onto the object.
**How to avoid:** `FoodEntryForm` must NOT include a `date` field. The date is set once at creation (`date.today()`) and never changed via the edit form.

### Pitfall 6: Mypy Errors on `scaled` List

**What goes wrong:** If the route builds `scaled` as a list comprehension without type annotations, Mypy may infer `list[Unknown]` and flag downstream usage.
**Why it happens:** `scale_nutrients()` returns `dict[str, float]` but Mypy needs the function to be annotated.
**How to avoid:** Annotate `nutrition.py` functions with full return types (`-> dict[str, float]`). The list comprehension type will infer correctly.

---

## Code Examples

### Portion Scaling Formula (FOOD-02)

```python
# app/nutrition.py — verified formula from REQUIREMENTS.md
# value = per_100g / 100 × amount_g
factor = amount_g / 100.0
calories = round(calories_per_100g * factor, 1)
```

### Jinja2 Min Filter for Progress Bar Cap

```html
{# Caps progress bar width at 100% visually #}
style="width: {{ [pct, 100] | min }}%"
```

### Delete Button with POST Form (FOOD-05)

```html
{# Using POST form prevents accidental GET deletion #}
<form method="POST" action="{{ url_for('main.delete_food', entry_id=entry.id) }}"
      class="d-inline">
  {{ form.hidden_tag() }}
  <button type="submit" class="btn btn-sm btn-outline-danger"
          onclick="return confirm('Eintrag löschen?')">
    Löschen
  </button>
</form>
```

Note: The delete form needs its own CSRF token. Options: (a) render a minimal `FlaskForm` with just `hidden_tag()` and pass it to the template, or (b) use `generate_csrf()` from flask_wtf.csrf directly. Option (a) is standard practice — add a `DeleteForm(FlaskForm): pass` class to `forms.py`.

### Date Navigation Links

```html
{# Previous/Next day navigation in dashboard.html #}
<div class="d-flex justify-content-between align-items-center mb-3">
  <a href="{{ url_for('main.dashboard', date=prev_date) }}"
     class="btn btn-outline-secondary btn-sm">&laquo; Vorheriger Tag</a>
  <h5 class="mb-0">
    {% if display_date == today %}Heute{% else %}{{ display_date.strftime('%d.%m.%Y') }}{% endif %}
  </h5>
  <a href="{{ url_for('main.dashboard', date=next_date) }}"
     class="btn btn-outline-secondary btn-sm {% if display_date >= today %}disabled{% endif %}">
    Nächster Tag &raquo;
  </a>
</div>
```

The "next day" button is disabled when already on today — prevents navigating into the future where no data exists.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `Model.query.filter_by(...)` | `db.session.execute(select(Model).where(...))` | SQLAlchemy 2.0 | Required — `Model.query` is deprecated |
| `Model.query.get(id)` | `db.session.get(Model, id)` | SQLAlchemy 2.0 | Required — already used in Phase 1 routes |
| Jinja2 `loop.index0` for parallel iteration | Pre-zip in route, pass merged list | N/A — best practice | Cleaner templates, easier to test route logic |

---

## Open Questions

1. **Delete CSRF: dedicated DeleteForm or flask_wtf.csrf.generate_csrf()?**
   - What we know: Both are valid; Flask-WTF supports both patterns.
   - What's unclear: Whether a `DeleteForm(FlaskForm): pass` stub class is idiomatic.
   - Recommendation: Use `class DeleteForm(FlaskForm): pass` — it's the most explicit and keeps all form handling through Flask-WTF's standard path. One small class in `forms.py`.

2. **Dashboard: inline food log or separate `/log` page?**
   - What we know: Success criteria say "Dashboard shows today's total calories and macros" and separately "User can navigate to a past date". Both can live on the dashboard route with `?date=` param.
   - What's unclear: Whether the food entry form should be inline on the dashboard or on a separate `/food/add` page.
   - Recommendation: Inline form on the dashboard for today's view (fastest workflow). Separate `food_form.html` only for the edit flow (GET /food/<id>/edit). This minimises page transitions.

3. **Progress bar colour: orange vs red for >100%?**
   - What we know: Success criteria say "orange/red above 100%". Bootstrap 5 has `bg-danger` (red) and `bg-warning` (yellow/orange).
   - What's unclear: Which Bootstrap class to use.
   - Recommendation: Use `bg-danger` (red). The success criteria list "orange/red" as a combined option. Bootstrap's `bg-warning` is more yellow than orange and has low contrast on white. `bg-danger` is unambiguous and requires no custom CSS.

---

## Environment Availability

Step 2.6: SKIPPED (no external dependencies identified — Phase 2 uses only already-installed Python packages and stdlib).

---

## Sources

### Primary (HIGH confidence)

- Phase 1 VERIFICATION.md — confirmed what models, routes, and modules exist
- `app/models.py` (read directly) — FoodEntry schema verified
- `app/routes.py` (read directly) — existing route patterns
- `app/calculator.py` (read directly) — pure-function module pattern to replicate in nutrition.py
- `app/forms.py` (read directly) — FoodEntryForm base pattern
- REQUIREMENTS.md — FOOD-01..07, DASH-01..03 specifications
- ROADMAP.md — Phase 2 success criteria (authoritative threshold spec)
- STATE.md — threshold discrepancy todo, architecture notes, critical pitfalls

### Secondary (MEDIUM confidence)

- Flask official docs — testing: https://flask.palletsprojects.com/en/stable/testing/
- Flask-WTF docs — CSRF and form patterns: https://flask-wtf.readthedocs.io/
- SQLAlchemy 2.x migration guide — `select()` API, `db.session.get()`: https://docs.sqlalchemy.org/en/20/

### Tertiary (LOW confidence)

- None — all findings are based on the existing codebase and authoritative documentation.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new packages; everything verified in Phase 1
- Architecture: HIGH — patterns derived from existing working code
- Pitfalls: HIGH — threshold discrepancy documented in STATE.md; CSRF/populate_obj patterns are well-known Flask-WTF behaviours
- Code examples: HIGH — formulas from REQUIREMENTS.md; patterns from existing routes.py

**Research date:** 2026-03-25
**Valid until:** 2026-04-25 (stable stack; Flask 3.x and SQLAlchemy 2.x have no pending breaking changes)
