from datetime import datetime, timezone, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Meal, WeightLog
from app.forms import MealForm, WeightForm, ProfileForm

bp = Blueprint("tracking", __name__, url_prefix="/tracking")


@bp.route("/meal/add", methods=["GET", "POST"])
@login_required
def add_meal():
    form = MealForm()
    if form.validate_on_submit():
        meal = Meal(
            user_id=current_user.id,
            name=form.name.data,
            calories=form.calories.data,
            protein_g=form.protein_g.data or 0,
            carbs_g=form.carbs_g.data or 0,
            fat_g=form.fat_g.data or 0,
            meal_type=form.meal_type.data,
        )
        db.session.add(meal)
        db.session.commit()
        flash("Mahlzeit gespeichert!", "success")
        return redirect(url_for("main.index"))
    return render_template("tracking/add_meal.html", form=form)


@bp.route("/weight/add", methods=["GET", "POST"])
@login_required
def add_weight():
    form = WeightForm()
    if form.validate_on_submit():
        log = WeightLog(user_id=current_user.id, weight_kg=form.weight_kg.data)
        db.session.add(log)
        db.session.commit()
        flash("Gewicht gespeichert!", "success")
        return redirect(url_for("main.index"))
    return render_template("tracking/add_weight.html", form=form)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.height_cm = form.height_cm.data
        current_user.target_weight_kg = form.target_weight_kg.data
        current_user.daily_calorie_goal = form.daily_calorie_goal.data
        db.session.commit()
        flash("Profil aktualisiert!", "success")
        return redirect(url_for("main.index"))
    return render_template("tracking/profile.html", form=form)


@bp.route("/history")
@login_required
def history():
    meals = current_user.meals.order_by(Meal.logged_at.desc()).limit(50).all()
    weights = current_user.weight_logs.order_by(WeightLog.logged_at.desc()).limit(30).all()
    return render_template("tracking/history.html", meals=meals, weights=weights)
