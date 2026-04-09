"""Tests für Authentifizierung."""

from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select
from werkzeug.security import generate_password_hash

from app import db
from app.models import User


def test_register_creates_user(client: FlaskClient, app: Flask) -> None:
    """Registrierung erstellt einen neuen User."""
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "password": "secret123",
            "confirm_password": "secret123",
        },
    )
    assert response.status_code == 302

    with app.app_context():
        user = db.session.execute(
            select(User).where(User.username == "newuser")
        ).scalar_one_or_none()
        assert user is not None


def test_login_valid_credentials(client: FlaskClient, app: Flask) -> None:
    """Login mit korrekten Daten leitet weiter."""
    with app.app_context():
        user = User(
            username="loginuser",
            password_hash=generate_password_hash("mypass"),
        )
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/login",
        data={"username": "loginuser", "password": "mypass"},
    )
    assert response.status_code == 302
