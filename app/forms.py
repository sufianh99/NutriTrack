from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class OnboardingForm(FlaskForm):
    age = IntegerField("Alter", validators=[DataRequired(), NumberRange(min=10, max=120)])
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
