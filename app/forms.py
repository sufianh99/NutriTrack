from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, FloatField, IntegerField, SelectField, SubmitField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class RegistrationForm(FlaskForm):
    username = StringField("Benutzername", validators=[DataRequired(), Length(3, 64)])
    password = PasswordField("Passwort", validators=[DataRequired(), Length(6, 128)])
    password2 = PasswordField("Passwort bestätigen", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Registrieren")


class LoginForm(FlaskForm):
    username = StringField("Benutzername", validators=[DataRequired(), Length(3, 64)])
    password = PasswordField("Passwort", validators=[DataRequired()])
    submit = SubmitField("Anmelden")


class MealForm(FlaskForm):
    name = StringField("Mahlzeit", validators=[DataRequired(), Length(1, 200)])
    calories = IntegerField("Kalorien (kcal)", validators=[DataRequired(), NumberRange(min=0)])
    protein_g = FloatField("Protein (g)", validators=[Optional(), NumberRange(min=0)])
    carbs_g = FloatField("Kohlenhydrate (g)", validators=[Optional(), NumberRange(min=0)])
    fat_g = FloatField("Fett (g)", validators=[Optional(), NumberRange(min=0)])
    meal_type = SelectField(
        "Mahlzeittyp",
        choices=[
            ("breakfast", "Frühstück"),
            ("lunch", "Mittagessen"),
            ("dinner", "Abendessen"),
            ("snack", "Snack"),
        ],
    )
    submit = SubmitField("Speichern")


class WeightForm(FlaskForm):
    weight_kg = FloatField("Gewicht (kg)", validators=[DataRequired(), NumberRange(min=20, max=500)])
    submit = SubmitField("Speichern")


class ProfileForm(FlaskForm):
    height_cm = FloatField("Größe (cm)", validators=[Optional(), NumberRange(min=50, max=300)])
    target_weight_kg = FloatField("Zielgewicht (kg)", validators=[Optional(), NumberRange(min=20, max=500)])
    daily_calorie_goal = IntegerField("Tagesziel Kalorien", validators=[Optional(), NumberRange(min=500, max=10000)])
    submit = SubmitField("Speichern")
