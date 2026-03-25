from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class DeleteForm(FlaskForm):
    """Empty form used solely for CSRF token on delete actions."""

    pass


class OnboardingForm(FlaskForm):
    age = IntegerField(
        "Alter", validators=[DataRequired(), NumberRange(min=10, max=120)]
    )
    height_cm = FloatField(
        "Größe (cm)", validators=[DataRequired(), NumberRange(min=100, max=250)]
    )
    weight_kg = FloatField(
        "Gewicht (kg)", validators=[DataRequired(), NumberRange(min=20, max=300)]
    )
    gender = SelectField(
        "Geschlecht",
        choices=[("male", "Männlich"), ("female", "Weiblich")],
        validators=[DataRequired()],
    )
    activity_level = SelectField(
        "Aktivitätslevel",
        choices=[
            ("sedentary", "Sitzend (wenig Bewegung)"),
            ("light", "Leicht aktiv (1-3x/Woche Sport)"),
            ("moderate", "Mäßig aktiv (3-5x/Woche Sport)"),
            ("active", "Sehr aktiv (6-7x/Woche Sport)"),
            ("very_active", "Extrem aktiv (körperliche Arbeit)"),
        ],
        validators=[DataRequired()],
    )
    goal = SelectField(
        "Ziel",
        choices=[("lose", "Abnehmen"), ("maintain", "Halten"), ("gain", "Zunehmen")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Speichern")


class FoodEntryForm(FlaskForm):
    name = StringField(
        "Lebensmittel", validators=[DataRequired(), Length(min=1, max=200)]
    )
    amount_g = FloatField(
        "Menge (g)", validators=[DataRequired(), NumberRange(min=0.1, max=5000)]
    )
    calories_per_100g = FloatField(
        "Kalorien pro 100g", validators=[DataRequired(), NumberRange(min=0, max=2000)]
    )
    protein_per_100g = FloatField(
        "Protein pro 100g (g)", validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    fat_per_100g = FloatField(
        "Fett pro 100g (g)", validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    carbs_per_100g = FloatField(
        "Kohlenhydrate pro 100g (g)",
        validators=[DataRequired(), NumberRange(min=0, max=100)],
    )
    submit = SubmitField("Speichern")
