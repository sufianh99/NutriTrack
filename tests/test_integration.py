from datetime import date

from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select

from app import db
from app.models import DailyGoal, FoodEntry, UserProfile

VALID_PROFILE = {
    "age": "30",
    "height_cm": "175.0",
    "weight_kg": "70.0",
    "gender": "male",
    "activity_level": "sedentary",
    "goal": "maintain",
}

VALID_FOOD = {
    "name": "Banane",
    "amount_g": "120.0",
    "calories_per_100g": "89.0",
    "protein_per_100g": "1.1",
    "fat_per_100g": "0.3",
    "carbs_per_100g": "22.8",
}


def test_profile_save(client: FlaskClient, app: Flask) -> None:
    """POST /onboarding saves UserProfile and creates a DailyGoal for today."""
    response = client.post("/onboarding", data=VALID_PROFILE)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")

    with app.app_context():
        profile = db.session.get(UserProfile, 1)
        assert profile is not None
        assert profile.age == 30
        assert profile.weight_kg == 70.0
        assert profile.gender == "male"

        today = date.today()
        goal = db.session.execute(
            select(DailyGoal).where(DailyGoal.date == today)
        ).scalar_one_or_none()
        assert goal is not None


def test_food_entry_add(client: FlaskClient, app: Flask) -> None:
    """POST /food/add adds a FoodEntry row to the database."""
    # Setup profile first so the food route doesn't redirect to onboarding
    client.post("/onboarding", data=VALID_PROFILE)

    response = client.post("/food/add", data=VALID_FOOD)
    assert response.status_code == 302

    with app.app_context():
        entries = db.session.execute(select(FoodEntry)).scalars().all()
        assert len(entries) == 1
        assert entries[0].name == "Banane"
        assert entries[0].amount_g == 120.0


def test_dashboard_response(client: FlaskClient, app: Flask) -> None:
    """GET /dashboard returns 200 with calorie and protein information."""
    client.post("/onboarding", data=VALID_PROFILE)

    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Kalorien" in response.data
    assert b"Protein" in response.data


def test_dashboard_redirects_without_profile(client: FlaskClient) -> None:
    """GET /dashboard without a profile redirects to /onboarding."""
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/onboarding")


def test_health_endpoint(client: FlaskClient) -> None:
    """GET /health returns 200 with JSON status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
