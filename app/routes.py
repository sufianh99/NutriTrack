import logging
from datetime import date, timedelta

from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import select
from werkzeug.wrappers import Response as WerkzeugResponse

from app import db
from app.api_client import search_food
from app.calculator import (
    apply_goal_modifier,
    calculate_bmr,
    calculate_macros,
    calculate_tdee,
)
from app.forms import DeleteForm, FoodEntryForm, OnboardingForm
from app.models import DailyGoal, FoodEntry, UserProfile
from app.nutrition import progress_status, scale_nutrients, sum_daily_nutrients

logger = logging.getLogger("nutritrack")

bp = Blueprint("main", __name__)


@bp.route("/health")
def health() -> tuple[Response, int]:
    """Health check endpoint for monitoring and CI verification."""
    return jsonify({"status": "ok"}), 200


@bp.route("/api/food-search")
def food_search() -> tuple[Response, int]:
    """Search Open Food Facts for foods matching the query string.

    Query param: q (str) — food name to search for.
    Returns JSON array of product dicts, or empty array if q < 2 chars.
    """
    q = request.args.get("q", "")
    if len(q) < 2:
        return jsonify([]), 200
    results = search_food(q)
    return jsonify(results), 200


def _get_profile() -> UserProfile | None:
    """Return the single-user profile (id=1) or None."""
    return db.session.get(UserProfile, 1)


def _save_profile_and_goals(form: OnboardingForm) -> None:
    """Create/update UserProfile and upsert today's DailyGoal."""
    profile = db.session.get(UserProfile, 1) or UserProfile(id=1)
    profile.age = form.age.data
    profile.height_cm = form.height_cm.data
    profile.weight_kg = form.weight_kg.data
    profile.gender = form.gender.data
    profile.activity_level = form.activity_level.data
    profile.goal = form.goal.data
    db.session.merge(profile)

    bmr = calculate_bmr(
        form.weight_kg.data, form.height_cm.data, form.age.data, form.gender.data
    )
    tdee = calculate_tdee(bmr, form.activity_level.data)
    calorie_goal = apply_goal_modifier(tdee, form.goal.data)
    macros = calculate_macros(calorie_goal)

    today = date.today()
    goal_row = db.session.execute(
        select(DailyGoal).where(DailyGoal.date == today)
    ).scalar_one_or_none()
    if goal_row is None:
        goal_row = DailyGoal(date=today)
    goal_row.calorie_goal = round(calorie_goal, 2)
    goal_row.protein_goal = macros["protein_g"]
    goal_row.fat_goal = macros["fat_g"]
    goal_row.carb_goal = macros["carbs_g"]
    db.session.merge(goal_row)
    db.session.commit()
    logger.info(
        "Profile saved: age=%d, weight=%.1f, height=%.1f, goal=%s",
        form.age.data,
        form.weight_kg.data,
        form.height_cm.data,
        form.goal.data,
    )


@bp.route("/")
def index() -> WerkzeugResponse:
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))
    return redirect(url_for("main.dashboard"))


@bp.route("/onboarding", methods=["GET", "POST"])
def onboarding() -> WerkzeugResponse | str:
    form = OnboardingForm()
    if form.validate_on_submit():
        _save_profile_and_goals(form)
        flash("Profil gespeichert! Deine Ziele wurden berechnet.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("onboarding.html", form=form)


@bp.route("/profile", methods=["GET", "POST"])
def profile() -> WerkzeugResponse | str:
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))
    form = OnboardingForm(obj=profile)
    if form.validate_on_submit():
        _save_profile_and_goals(form)
        flash("Profil aktualisiert! Ziele neu berechnet.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("profile.html", form=form, profile=profile)


@bp.route("/dashboard")
def dashboard() -> WerkzeugResponse | str:
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))

    # Resolve display date from ?date= query param or default to today
    date_str = request.args.get("date")
    try:
        display_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        display_date = date.today()

    today = date.today()

    # Always use today's goal for Soll values (goals don't retroactively change)
    goal = db.session.execute(
        select(DailyGoal).where(DailyGoal.date == today)
    ).scalar_one_or_none()

    # Fetch food entries for the displayed date
    entries = (
        db.session.execute(
            select(FoodEntry)
            .where(FoodEntry.date == display_date)
            .order_by(FoodEntry.id)
        )
        .scalars()
        .all()
    )

    # Scale each entry and compute daily totals
    scaled = [
        scale_nutrients(
            e.amount_g,
            e.calories_per_100g,
            e.protein_per_100g,
            e.fat_per_100g,
            e.carbs_per_100g,
        )
        for e in entries
    ]
    totals = sum_daily_nutrients(scaled)

    # Build merged entry_rows for template (avoids zip in Jinja2)
    entry_rows = [{"entry": e, "scaled": s} for e, s in zip(entries, scaled)]

    # Compute progress statuses for colour coding
    statuses: dict[str, str] = {}
    if goal:
        statuses = {
            "calories": progress_status(totals["calories"], goal.calorie_goal),
            "protein": progress_status(totals["protein_g"], goal.protein_goal),
            "fat": progress_status(totals["fat_g"], goal.fat_goal),
            "carbs": progress_status(totals["carbs_g"], goal.carb_goal),
        }

    # Compute remaining and percentages for DASH-03
    remaining: dict[str, float] = {}
    percentages: dict[str, float] = {}
    if goal:
        remaining = {
            "calories": round(goal.calorie_goal - totals["calories"], 1),
            "protein_g": round(goal.protein_goal - totals["protein_g"], 1),
            "fat_g": round(goal.fat_goal - totals["fat_g"], 1),
            "carbs_g": round(goal.carb_goal - totals["carbs_g"], 1),
        }
        percentages = {
            "calories": (
                round(totals["calories"] / goal.calorie_goal * 100, 1)
                if goal.calorie_goal > 0
                else 0.0
            ),
            "protein": (
                round(totals["protein_g"] / goal.protein_goal * 100, 1)
                if goal.protein_goal > 0
                else 0.0
            ),
            "fat": (
                round(totals["fat_g"] / goal.fat_goal * 100, 1)
                if goal.fat_goal > 0
                else 0.0
            ),
            "carbs": (
                round(totals["carbs_g"] / goal.carb_goal * 100, 1)
                if goal.carb_goal > 0
                else 0.0
            ),
        }

    prev_date = display_date - timedelta(days=1)
    next_date = display_date + timedelta(days=1)

    delete_form = DeleteForm()

    return render_template(
        "dashboard.html",
        profile=profile,
        goal=goal,
        entry_rows=entry_rows,
        totals=totals,
        statuses=statuses,
        remaining=remaining,
        percentages=percentages,
        display_date=display_date,
        today=today,
        prev_date=prev_date,
        next_date=next_date,
        delete_form=delete_form,
    )


@bp.route("/food/add", methods=["GET", "POST"])
def add_food() -> WerkzeugResponse | str:
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
        logger.info("Food entry added: %s, %.1fg", form.name.data, form.amount_g.data)
        flash("Lebensmittel hinzugefuegt.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("food_form.html", form=form, edit=False)


@bp.route("/food/<int:entry_id>/edit", methods=["GET", "POST"])
def edit_food(entry_id: int) -> WerkzeugResponse | str:
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))
    entry = db.session.get(FoodEntry, entry_id)
    if entry is None:
        flash("Eintrag nicht gefunden.", "warning")
        return redirect(url_for("main.dashboard"))
    form = FoodEntryForm(obj=entry)
    if form.validate_on_submit():
        form.populate_obj(entry)
        db.session.commit()
        logger.info("Food entry updated: id=%d, %s", entry_id, form.name.data)
        flash("Eintrag aktualisiert.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("food_form.html", form=form, edit=True, entry=entry)


@bp.route("/food/<int:entry_id>/delete", methods=["POST"])
def delete_food(entry_id: int) -> WerkzeugResponse:
    entry = db.session.get(FoodEntry, entry_id)
    if entry is not None:
        db.session.delete(entry)
        db.session.commit()
        logger.info("Food entry deleted: id=%d", entry_id)
        flash("Eintrag geloescht.", "success")
    return redirect(url_for("main.dashboard"))
