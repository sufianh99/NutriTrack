from flask import Blueprint, render_template, redirect, url_for, flash, request
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required

from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Dieser Benutzername ist bereits vergeben.", "danger")
            return render_template("auth/register.html", form=form)
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Registrierung fehlgeschlagen: Datenbank-Schema ist veraltet. Bitte DB neu erstellen (siehe README) oder Migration ausführen.", "danger")
            return render_template("auth/register.html", form=form)
        flash("Registrierung erfolgreich! Du kannst dich jetzt anmelden.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))
        flash("Ungültiger Benutzername oder Passwort.", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Erfolgreich abgemeldet.", "info")
    return redirect(url_for("main.index"))
