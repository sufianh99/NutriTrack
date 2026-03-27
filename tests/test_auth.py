"""Tests for authentication: register, login, logout, access control, data isolation."""

from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select
from werkzeug.security import generate_password_hash

from app import db
from app.models import FoodEntry, User, UserProfile


def test_register_creates_user(client: FlaskClient, app: Flask) -> None:
    """POST /register creates a new user and redirects to onboarding."""
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "password": "secret123",
            "confirm_password": "secret123",
        },
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/onboarding")

    with app.app_context():
        user = db.session.execute(
            select(User).where(User.username == "newuser")
        ).scalar_one_or_none()
        assert user is not None


def test_register_duplicate_username(client: FlaskClient, app: Flask) -> None:
    """POST /register with existing username shows error."""
    with app.app_context():
        user = User(
            username="taken",
            password_hash=generate_password_hash("pass123"),
        )
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/register",
        data={
            "username": "taken",
            "password": "secret123",
            "confirm_password": "secret123",
        },
    )
    assert response.status_code == 200
    assert "bereits vergeben" in response.data.decode()


def test_login_valid_credentials(client: FlaskClient, app: Flask) -> None:
    """POST /login with valid credentials redirects to index."""
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
    assert response.headers["Location"].endswith("/")


def test_login_invalid_credentials(client: FlaskClient, app: Flask) -> None:
    """POST /login with wrong password shows error."""
    with app.app_context():
        user = User(
            username="loginuser",
            password_hash=generate_password_hash("mypass"),
        )
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/login",
        data={"username": "loginuser", "password": "wrongpass"},
    )
    assert response.status_code == 200
    assert "falsch" in response.data.decode()


def test_logout(auth_client: tuple) -> None:
    """GET /logout redirects to login."""
    client, _ = auth_client
    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_protected_route_redirects_anonymous(client: FlaskClient) -> None:
    """Unauthenticated access to /dashboard redirects to /login."""
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_data_isolation(app: Flask) -> None:
    """User A cannot see User B's food entries."""
    client = app.test_client()

    with app.app_context():
        user_a = User(
            username="alice",
            password_hash=generate_password_hash("pass_a"),
        )
        user_b = User(
            username="bob",
            password_hash=generate_password_hash("pass_b"),
        )
        db.session.add_all([user_a, user_b])
        db.session.commit()

        # Create profiles for both
        from datetime import date

        profile_a = UserProfile(
            user_id=user_a.id,
            age=25,
            height_cm=170.0,
            weight_kg=65.0,
            gender="female",
            activity_level="moderate",
            goal="maintain",
        )
        profile_b = UserProfile(
            user_id=user_b.id,
            age=30,
            height_cm=180.0,
            weight_kg=80.0,
            gender="male",
            activity_level="sedentary",
            goal="lose",
        )
        db.session.add_all([profile_a, profile_b])

        # Bob adds a food entry
        entry_b = FoodEntry(
            user_id=user_b.id,
            date=date.today(),
            name="Bobs Geheimrezept",
            amount_g=200.0,
            calories_per_100g=300.0,
            protein_per_100g=20.0,
            fat_per_100g=10.0,
            carbs_per_100g=40.0,
        )
        db.session.add(entry_b)
        db.session.commit()

        a_id = user_a.id

    # Login as Alice
    with client.session_transaction() as sess:
        sess["_user_id"] = str(a_id)

    # Alice's dashboard should NOT show Bob's entry
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Bobs Geheimrezept" not in response.data
