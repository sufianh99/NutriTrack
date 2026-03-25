from flask import Blueprint, redirect, render_template, url_for

from app import db
from app.models import UserProfile

bp = Blueprint("main", __name__)


def _get_profile():
    return db.session.get(UserProfile, 1)


@bp.route("/")
def index():
    profile = _get_profile()
    if profile is None:
        return redirect(url_for("main.onboarding"))
    return redirect(url_for("main.dashboard"))


@bp.route("/onboarding")
def onboarding():
    return render_template("onboarding.html")


@bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
