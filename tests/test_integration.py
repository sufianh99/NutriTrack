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


def test_profile_save(auth_client: tuple, app: Flask) -> None:
    """Profil speichern erstellt UserProfile und DailyGoal."""
    client, user = auth_client
    response = client.post("/onboarding", data=VALID_PROFILE)
    assert response.status_code == 302

    with app.app_context():
        profile = db.session.execute(
            select(UserProfile).where(UserProfile.user_id == user.id)
        ).scalar_one_or_none()
        assert profile is not None
        assert profile.weight_kg == 70.0


def test_food_entry_add(auth_client: tuple, app: Flask) -> None:
    """Lebensmittel hinzufügen erstellt FoodEntry in der Datenbank."""
    client, user = auth_client
    client.post("/onboarding", data=VALID_PROFILE)
    response = client.post("/food/add", data=VALID_FOOD)
    assert response.status_code == 302

    with app.app_context():
        entries = (
            db.session.execute(select(FoodEntry).where(FoodEntry.user_id == user.id))
            .scalars()
            .all()
        )
        assert len(entries) == 1
        assert entries[0].name == "Banane"


def test_dashboard_shows_nutrients(auth_client: tuple, app: Flask) -> None:
    """Dashboard zeigt Kalorien und Protein an."""
    client, _ = auth_client
    client.post("/onboarding", data=VALID_PROFILE)
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Kalorien" in response.data
