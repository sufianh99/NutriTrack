# Bewertungs-Checkliste NutriTrack

## Must Have

| Kriterium                                                     | Gewichtung | Status   | Nachweis                                                                                                                                                                                                                                     |
| ------------------------------------------------------------- | ---------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Commits werden automatisiert in CI gebracht                   | 3          | Erfuellt | `.github/workflows/ci.yml` — Trigger auf `push` (Zeile 4-5) und `pull_request` (Zeile 6-7). Quality-Job fuehrt Black, Ruff, Mypy, Pytest aus (Zeile 10-36).                                                                                  |
| Mindestens ein Unit-Test wird in CI automatisiert ausgefuehrt | 3          | Erfuellt | `ci.yml` Zeile 35-36: `pytest` wird ausgefuehrt. 43 Tests in 5 Dateien: `tests/test_calculator.py` (10), `tests/test_nutrition.py` (12), `tests/test_api_client.py` (9), `tests/test_auth.py` (7), `tests/test_integration.py` (5).          |
| UML- oder DIN-Diagramm umgesetzt                              | 2          | Erfuellt | `docs/klassendiagramm.mmd` — Mermaid-Klassendiagramm mit 4 DB-Modellen, 3 Logik-Modulen, 4 Formklassen und Beziehungen. `docs/sequenzdiagramm-ci.mmd` — Sequenzdiagramm der CI/CD-Pipeline. `docs/klassendiagramm.puml` — PlantUML-Version.  |
| Daten aus mindestens einer Datenquelle erfasst                | 3          | Erfuellt | **Nutzereingabe:** Formulare in `app/forms.py` (OnboardingForm, FoodEntryForm). **Externe API:** Open Food Facts via `app/api_client.py` (Zeile 1-126), Endpunkt `/api/food-search` in `app/routes.py` (Zeile 103-111).                      |
| Daten werden verarbeitet und interpretiert                    | 3          | Erfuellt | `app/calculator.py` — BMR (Mifflin-St-Jeor), TDEE, Makroverteilung. `app/nutrition.py` — Naehrstoffskalierung, Tagessummen, Ampel-Status (`progress_status()` mit Schwellenwerten <90%, 90-100%, >100%). Dashboard zeigt Soll/Ist-Vergleich. |
| Daten werden in Datenbank gespeichert (AE)                    | 3          | Erfuellt | SQLite via Flask-SQLAlchemy. Konfiguration in `config.py` (Zeile 12): `instance/nutritrack.db`. 4 Modelle in `app/models.py`: `User`, `UserProfile`, `DailyGoal`, `FoodEntry`.                                                               |
| Lesbar und verstaendlich (aussagekraeftige Namen)             | 3          | Erfuellt | Funktionen: `calculate_bmr()`, `calculate_tdee()`, `scale_nutrients()`, `progress_status()`, `search_food()`. Variablen: `calories_per_100g`, `protein_per_100g`, `activity_level`, `calorie_goal`. Durchgehend Type Hints und Docstrings.   |

## Should Have

| Kriterium                                           | Gewichtung | Status   | Nachweis                                                                                                                                                                                                                                                                                                                                                      |
| --------------------------------------------------- | ---------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Automatisiertes Linting in Pipeline                 | 1          | Erfuellt | `ci.yml` Zeile 26-33: `black --check .`, `ruff check .`, `mypy app/`. Konfiguration in `pyproject.toml`, Dev-Dependencies in `requirements-dev.txt`.                                                                                                                                                                                                          |
| Mind. 3 Unit-Tests + 1 Integrationstest             | 1          | Erfuellt | 38 Unit-Tests (test_calculator, test_nutrition, test_api_client, test_auth) + 5 Integrationstests (`tests/test_integration.py` — Profil-Speicherung, Food-Entry, Dashboard-Workflow).                                                                                                                                                                         |
| Daten ueber GUI/Website visualisiert                | 1          | Erfuellt | 7 Templates in `app/templates/`: `dashboard.html` (Fortschrittsbalken, Ampel-Farben), `food_form.html`, `login.html`, `register.html`, `onboarding.html`, `profile.html`, `base.html`. Bootstrap-Styling.                                                                                                                                                     |
| OOP-Aufbau, sinnvoll in Module/Klassen strukturiert | 1          | Erfuellt | **Klassen:** `User`, `UserProfile`, `DailyGoal`, `FoodEntry` (models.py), `LoginForm`, `RegisterForm`, `OnboardingForm`, `FoodEntryForm` (forms.py), `APIError` (api_client.py). **Module:** calculator.py, nutrition.py, api_client.py (reine Logik ohne Flask-Abhaengigkeit), routes.py (Blueprint). **Pattern:** Application Factory in `app/__init__.py`. |

## Could Have

| Kriterium                                     | Gewichtung | Status   | Nachweis                                                                                                                                                                               |
| --------------------------------------------- | ---------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Continuous Deployment in Produktivumgebung    | 2          | Erfuellt | `ci.yml` Zeile 38-48: Deploy-Job nach Quality-Check, POST an Render Deploy Hook. `Procfile`: `web: gunicorn wsgi:app`. `scripts/monitor.py`: Health-Check nach Deployment (3 Retries). |
| Daten ueber weitere Medien (API, E-Mail, ...) | 2          | Erfuellt | REST-API: `/api/food-search` (routes.py Zeile 103-111) liefert JSON. `/health` Endpunkt (routes.py Zeile 94-97) fuer Monitoring.                                                       |

## Fachgespraech

| Kriterium                                       | Gewichtung | Status       | Nachweis                                                                                                                                                                   |
| ----------------------------------------------- | ---------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Alle sind am Gespraech beteiligt                | 3          | Vorbereitung | Vorbereitung erforderlich — kein technischer Nachweis moeglich.                                                                                                            |
| Alle koennen auf Fragen zum Quellcode antworten | 3          | Vorbereitung | Kernmodule verstehen: `calculator.py` (Mifflin-St-Jeor), `nutrition.py` (Skalierung/Ampel), `api_client.py` (OFF-API), `models.py` (Datenmodell), `routes.py` (Endpunkte). |
| Fragen im Kontext OOP beantwortet               | —          | Vorbereitung | Relevante Konzepte: Klassen (SQLAlchemy-Modelle, WTForms), Vererbung (`db.Model`, `FlaskForm`), Kapselung (Module), Factory Pattern (`create_app()`).                      |

---

**Ergebnis:** Alle technischen Kriterien (Must Have, Should Have, Could Have) sind erfuellt. Fuer das Fachgespraech ist Vorbereitung noetig.
