from datetime import date

from flask import Blueprint, flash, redirect, render_template, url_for
from sqlalchemy import select

from app import db
from app.calculator import (
    apply_goal_modifier,
    calculate_bmr,
    calculate_macros,
    calculate_tdee,
)
from app.forms import OnboardingForm
from app.models import DailyGoal, UserProfile

bp = Blueprint("main", __name__)


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


@bp.route("/")
def index():
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))
    return redirect(url_for("main.dashboard"))


@bp.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    form = OnboardingForm()
    if form.validate_on_submit():
        _save_profile_and_goals(form)
        flash("Profil gespeichert! Deine Ziele wurden berechnet.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("onboarding.html", form=form)


@bp.route("/profile", methods=["GET", "POST"])
def profile():
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
def dashboard():
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))
    today = date.today()
    goal = db.session.execute(
        select(DailyGoal).where(DailyGoal.date == today)
    ).scalar_one_or_none()
    return render_template("dashboard.html", profile=profile, goal=goal)
