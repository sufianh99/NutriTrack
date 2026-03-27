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
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.wrappers import Response as WerkzeugResponse

from app import db
from app.api_client import search_food
from app.calculator import (
    apply_goal_modifier,
    calculate_bmr,
    calculate_macros,
    calculate_tdee,
)
from app.forms import DeleteForm, FoodEntryForm, LoginForm, OnboardingForm, RegisterForm
from app.models import DailyGoal, FoodEntry, User, UserProfile
from app.nutrition import progress_status, scale_nutrients, sum_daily_nutrients

logger = logging.getLogger("nutritrack")

bp = Blueprint("main", __name__)


# --- Auth Routes ---


@bp.route("/register", methods=["GET", "POST"])
def register() -> WerkzeugResponse | str:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        existing = db.session.execute(
            select(User).where(User.username == form.username.data)
        ).scalar_one_or_none()
        if existing:
            flash("Benutzername bereits vergeben.", "danger")
            return render_template("register.html", form=form)
        user = User(
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data),
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        logger.info("User registered: %s", user.username)
        flash("Registrierung erfolgreich! Bitte Profil ausfuellen.", "success")
        return redirect(url_for("main.onboarding"))
    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login() -> WerkzeugResponse | str:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(
            select(User).where(User.username == form.username.data)
        ).scalar_one_or_none()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            logger.info("User logged in: %s", user.username)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))
        flash("Benutzername oder Passwort falsch.", "danger")
    return render_template("login.html", form=form)


@bp.route("/logout")
@login_required
def logout() -> WerkzeugResponse:
    logger.info("User logged out: %s", current_user.username)
    logout_user()
    flash("Erfolgreich abgemeldet.", "success")
    return redirect(url_for("main.login"))


# --- Health ---


@bp.route("/health")
def health() -> tuple[Response, int]:
    """Health check endpoint for monitoring and CI verification."""
    return jsonify({"status": "ok"}), 200


# --- API ---


@bp.route("/api/food-search")
@login_required
def food_search() -> tuple[Response, int]:
    """Search Open Food Facts for foods matching the query string."""
    q = request.args.get("q", "")
    if len(q) < 2:
        return jsonify([]), 200
    results = search_food(q)
    return jsonify(results), 200


# --- Helpers ---


def _get_profile() -> UserProfile | None:
    """Return the current user's profile or None."""
    return db.session.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    ).scalar_one_or_none()


def _save_profile_and_goals(form: OnboardingForm) -> None:
    """Create/update UserProfile and upsert today's DailyGoal for current user."""
    profile = db.session.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    ).scalar_one_or_none()
    if profile is None:
        profile = UserProfile(user_id=current_user.id)
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
        select(DailyGoal).where(
            DailyGoal.user_id == current_user.id, DailyGoal.date == today
        )
    ).scalar_one_or_none()
    if goal_row is None:
        goal_row = DailyGoal(date=today, user_id=current_user.id)
    goal_row.calorie_goal = round(calorie_goal, 2)
    goal_row.protein_goal = macros["protein_g"]
    goal_row.fat_goal = macros["fat_g"]
    goal_row.carb_goal = macros["carbs_g"]
    db.session.merge(goal_row)
    db.session.commit()
    logger.info(
        "Profile saved: user=%s, age=%d, weight=%.1f, height=%.1f, goal=%s",
        current_user.username,
        form.age.data,
        form.weight_kg.data,
        form.height_cm.data,
        form.goal.data,
    )


# --- App Routes ---


@bp.route("/")
@login_required
def index() -> WerkzeugResponse:
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))
    return redirect(url_for("main.dashboard"))


@bp.route("/onboarding", methods=["GET", "POST"])
@login_required
def onboarding() -> WerkzeugResponse | str:
    form = OnboardingForm()
    if form.validate_on_submit():
        _save_profile_and_goals(form)
        flash("Profil gespeichert! Deine Ziele wurden berechnet.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("onboarding.html", form=form)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
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
@login_required
def dashboard() -> WerkzeugResponse | str:
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))

    date_str = request.args.get("date")
    try:
        display_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        display_date = date.today()

    today = date.today()

    goal = db.session.execute(
        select(DailyGoal).where(
            DailyGoal.user_id == current_user.id, DailyGoal.date == today
        )
    ).scalar_one_or_none()

    entries = (
        db.session.execute(
            select(FoodEntry)
            .where(
                FoodEntry.user_id == current_user.id,
                FoodEntry.date == display_date,
            )
            .order_by(FoodEntry.id)
        )
        .scalars()
        .all()
    )

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

    entry_rows = [{"entry": e, "scaled": s} for e, s in zip(entries, scaled)]

    statuses: dict[str, str] = {}
    if goal:
        statuses = {
            "calories": progress_status(totals["calories"], goal.calorie_goal),
            "protein": progress_status(totals["protein_g"], goal.protein_goal),
            "fat": progress_status(totals["fat_g"], goal.fat_goal),
            "carbs": progress_status(totals["carbs_g"], goal.carb_goal),
        }

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
@login_required
def add_food() -> WerkzeugResponse | str:
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))
    form = FoodEntryForm()
    if form.validate_on_submit():
        entry = FoodEntry(
            user_id=current_user.id,
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
@login_required
def edit_food(entry_id: int) -> WerkzeugResponse | str:
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))
    entry = db.session.execute(
        select(FoodEntry).where(
            FoodEntry.id == entry_id, FoodEntry.user_id == current_user.id
        )
    ).scalar_one_or_none()
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
@login_required
def delete_food(entry_id: int) -> WerkzeugResponse:
    entry = db.session.execute(
        select(FoodEntry).where(
            FoodEntry.id == entry_id, FoodEntry.user_id == current_user.id
        )
    ).scalar_one_or_none()
    if entry is not None:
        db.session.delete(entry)
        db.session.commit()
        logger.info("Food entry deleted: id=%d", entry_id)
        flash("Eintrag geloescht.", "success")
    return redirect(url_for("main.dashboard"))
