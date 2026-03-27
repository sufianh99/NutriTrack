from datetime import date

from flask_login import UserMixin
from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app import db


class User(UserMixin, db.Model):  # type: ignore[name-defined]
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)


class UserProfile(db.Model):  # type: ignore[name-defined]
    __tablename__ = "user_profile"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    activity_level: Mapped[str] = mapped_column(String(20), nullable=False)
    goal: Mapped[str] = mapped_column(String(20), nullable=False)


class DailyGoal(db.Model):  # type: ignore[name-defined]
    __tablename__ = "daily_goal"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    calorie_goal: Mapped[float] = mapped_column(Float, nullable=False)
    protein_goal: Mapped[float] = mapped_column(Float, nullable=False)
    fat_goal: Mapped[float] = mapped_column(Float, nullable=False)
    carb_goal: Mapped[float] = mapped_column(Float, nullable=False)


class FoodEntry(db.Model):  # type: ignore[name-defined]
    __tablename__ = "food_entry"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount_g: Mapped[float] = mapped_column(Float, nullable=False)
    calories_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    protein_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
