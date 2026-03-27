# NutriTrack — Umsetzungsanleitung

Schritt-fuer-Schritt-Anleitung, um NutriTrack in Minimalform selbst zu erstellen.

---

## Voraussetzungen

- Python 3.12+
- pip
- Git
- GitHub-Account (fuer CI/CD)

---

## Schritt 1: Projektstruktur anlegen

```
nutritrack/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── calculator.py
│   ├── nutrition.py
│   ├── api_client.py
│   ├── logging_config.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── onboarding.html
│   │   ├── profile.html
│   │   ├── food_form.html
│   │   └── dashboard.html
│   └── static/
│       └── style.css
├── tests/
│   ├── conftest.py
│   ├── test_calculator.py
│   ├── test_nutrition.py
│   ├── test_api_client.py
│   ├── test_integration.py
│   └── test_auth.py
├── instance/            (wird automatisch erstellt)
├── config.py
├── run.py
├── wsgi.py
├── Procfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── .github/workflows/ci.yml
```

```bash
mkdir -p app/templates app/static tests instance .github/workflows
touch app/__init__.py app/models.py app/routes.py app/forms.py
touch app/calculator.py app/nutrition.py app/api_client.py app/logging_config.py
touch config.py run.py wsgi.py Procfile
touch requirements.txt requirements-dev.txt pyproject.toml
```

---

## Schritt 2: Dependencies installieren

**requirements.txt:**
```
Flask==3.1.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2
python-dotenv==1.2.2
gunicorn==23.0.0
requests==2.32.5
```

**requirements-dev.txt:**
```
-r requirements.txt
pytest==9.0.2
pytest-flask==1.3.0
black==26.3.1
ruff==0.15.7
mypy==1.19.1
```

```bash
pip install -r requirements-dev.txt
```

---

## Schritt 3: Konfiguration (`config.py`)

Zwei Klassen: `Config` (Produktion) und `TestConfig` (Tests).

- `SECRET_KEY` aus Umgebungsvariable oder Fallback
- `SQLALCHEMY_DATABASE_URI` = SQLite-Datei unter `instance/nutritrack.db`
- `TestConfig`: In-Memory-SQLite (`sqlite:///:memory:`), CSRF deaktiviert

---

## Schritt 4: App Factory (`app/__init__.py`)

1. `db = SQLAlchemy()` initialisieren
2. `login_manager = LoginManager()` initialisieren, `login_view = "main.login"` setzen
3. `create_app(config_class)` Funktion:
   - Flask-App erstellen, Config laden
   - `db.init_app(app)` und `login_manager.init_app(app)`
   - Logging konfigurieren
   - `@login_manager.user_loader` registrieren (laedt User per ID aus DB)
   - Blueprint importieren und registrieren
   - `db.create_all()` im App-Context
   - App zurueckgeben

---

## Schritt 5: Datenmodelle (`app/models.py`)

4 Modelle mit SQLAlchemy 2.0 `Mapped[]` Syntax:

### User
| Spalte | Typ | Hinweis |
|--------|-----|---------|
| id | Integer, PK | |
| username | String(80), unique | |
| password_hash | String(256) | Werkzeug-Hash |

Erbt von `UserMixin` (Flask-Login).

### UserProfile
| Spalte | Typ | Hinweis |
|--------|-----|---------|
| id | Integer, PK | |
| user_id | Integer, FK(user.id) | |
| age | Integer | |
| height_cm | Float | |
| weight_kg | Float | |
| gender | String(10) | "male" / "female" |
| activity_level | String(20) | sedentary/light/moderate/active/very_active |
| goal | String(20) | lose/maintain/gain |

### DailyGoal
| Spalte | Typ | Hinweis |
|--------|-----|---------|
| id | Integer, PK | |
| user_id | Integer, FK(user.id) | |
| date | Date | Ein Goal pro User pro Tag |
| calorie_goal | Float | |
| protein_goal | Float | Gramm |
| fat_goal | Float | Gramm |
| carb_goal | Float | Gramm |

### FoodEntry
| Spalte | Typ | Hinweis |
|--------|-----|---------|
| id | Integer, PK | |
| user_id | Integer, FK(user.id) | |
| date | Date | |
| name | String(200) | |
| amount_g | Float | Portionsgroesse |
| calories_per_100g | Float | |
| protein_per_100g | Float | |
| fat_per_100g | Float | |
| carbs_per_100g | Float | |

---

## Schritt 6: Berechnungslogik (`app/calculator.py`)

Reine Funktionen, kein Flask/DB-Import noetig.

### Mifflin-St-Jeor Formel (BMR)
```
Maennlich: (10 x Gewicht_kg) + (6.25 x Groesse_cm) - (5 x Alter) + 5
Weiblich:  (10 x Gewicht_kg) + (6.25 x Groesse_cm) - (5 x Alter) - 161
```

### TDEE = BMR x Aktivitaetsfaktor
| Level | Faktor |
|-------|--------|
| sedentary | 1.2 |
| light | 1.375 |
| moderate | 1.55 |
| active | 1.725 |
| very_active | 1.9 |

### Kalorienziel = TDEE x Ziel-Modifikator
| Ziel | Modifikator |
|------|-------------|
| lose | 0.85 (-15%) |
| maintain | 1.0 |
| gain | 1.10 (+10%) |

### Makroverteilung
| Makro | Anteil | kcal/g |
|-------|--------|--------|
| Protein | 25% | 4.0 |
| Fett | 30% | 9.0 |
| Kohlenhydrate | 45% | 4.0 |

Formel: `gramm = (kalorienziel x anteil) / kcal_pro_gramm`

4 Funktionen implementieren:
1. `calculate_bmr(weight_kg, height_cm, age, gender) -> float`
2. `calculate_tdee(bmr, activity_level) -> float`
3. `apply_goal_modifier(tdee, goal) -> float`
4. `calculate_macros(calorie_goal) -> dict` (gibt protein_g, fat_g, carbs_g zurueck)

---

## Schritt 7: Naehrwert-Helfer (`app/nutrition.py`)

Reine Funktionen:

1. **`scale_nutrients(amount_g, cal, prot, fat, carbs) -> dict`**
   - Skaliert pro-100g-Werte auf Portionsgroesse: `wert * (amount_g / 100)`
   - Gibt dict mit keys: calories, protein_g, fat_g, carbs_g

2. **`sum_daily_nutrients(entries: list[dict]) -> dict`**
   - Summiert Liste von skalierten Eintraegen
   - Leere Liste = alles 0

3. **`progress_status(actual, goal) -> str`**
   - `""` wenn < 90%
   - `"success"` wenn 90-100% (gruen)
   - `"danger"` wenn > 100% (rot)

---

## Schritt 8: Open Food Facts API (`app/api_client.py`)

1. **`search_food(query, max_results=10) -> list[dict]`**
   - HTTP GET an `https://search.openfoodfacts.org/search`
   - Parameter: `q`, `page_size`, `fields`
   - Antwort-Key: `hits` (Liste von Produkten)
   - Jedes Produkt hat `nutriments` dict mit:
     - `energy-kcal_100g`, `proteins_100g`, `fat_100g`, `carbohydrates_100g`
   - Filtern: Produkte ohne kcal UND ohne Protein entfernen
   - Deduplizieren: Gleiche Namen (case-insensitive) nur einmal
   - Brand an Namen anhaengen: "Haferflocken (Alnatura)"
   - Alle Werte auf 1 Dezimalstelle runden
   - Fallback-URL: `https://world.openfoodfacts.org/api/v2/search` (nutzt `search_terms` statt `q`, Key `products` statt `hits`)
   - User-Agent Header setzen: `NutriTrack/1.0`
   - Alle Exceptions fangen, bei Fehler leere Liste zurueckgeben

---

## Schritt 9: Formulare (`app/forms.py`)

Flask-WTF Formulare mit Validierung:

| Form | Felder | Validierung |
|------|--------|-------------|
| DeleteForm | (leer) | Nur CSRF-Token |
| LoginForm | username, password | Required, username 3-80 Zeichen |
| RegisterForm | username, password, confirm_password | Required, password 6-128 Zeichen, confirm muss matchen |
| OnboardingForm | age, height_cm, weight_kg, gender, activity_level, goal | NumberRange, DataRequired, SelectField |
| FoodEntryForm | name, amount_g, calories_per_100g, protein_per_100g, fat_per_100g, carbs_per_100g | NumberRange, DataRequired |

---

## Schritt 10: Routes (`app/routes.py`)

Ein Blueprint `main` mit 12 Endpunkten:

### Auth (ohne @login_required)
| Route | Methode | Was passiert |
|-------|---------|--------------|
| `/register` | GET/POST | User anlegen, Passwort hashen (Werkzeug), einloggen, redirect zu /onboarding |
| `/login` | GET/POST | Credentials pruefen, `login_user()`, redirect zu / oder `?next=` |
| `/logout` | GET | `logout_user()`, redirect zu /login |
| `/health` | GET | JSON `{"status": "ok"}` |

### Geschuetzt (@login_required)
| Route | Methode | Was passiert |
|-------|---------|--------------|
| `/` | GET | Profil vorhanden? -> /dashboard, sonst -> /onboarding |
| `/onboarding` | GET/POST | Profilformular, bei Submit: BMR/TDEE/Makros berechnen, Profil+DailyGoal speichern |
| `/profile` | GET/POST | Wie Onboarding, aber fuer bestehendes Profil |
| `/dashboard` | GET | Tagesansicht mit Soll/Ist-Vergleich, optional `?date=YYYY-MM-DD` |
| `/food/add` | GET/POST | Lebensmittel hinzufuegen (heute) |
| `/food/<id>/edit` | GET/POST | Eintrag bearbeiten (Ownership pruefen!) |
| `/food/<id>/delete` | POST | Eintrag loeschen (Ownership pruefen!) |
| `/api/food-search` | GET | JSON-API fuer OFF-Suche, Parameter `?q=` |

### Wichtig bei allen geschuetzten Routes:
- Alle DB-Queries filtern auf `current_user.id`
- Edit/Delete pruefen `user_id == current_user.id`
- Ohne Profil -> Redirect zu /onboarding

---

## Schritt 11: Templates

### base.html
- Bootstrap 5.3.3 CDN einbinden
- Navbar: Brand "NutriTrack", Links abhaengig von Login-Status
- Flash-Messages als Bootstrap-Alerts
- Footer, Script-Block

### login.html / register.html
- Einfache Formulare mit Bootstrap-Klassen
- Links zwischen Login und Register

### onboarding.html / profile.html
- Alle Profilfelder als Bootstrap-Form
- SelectFields fuer Geschlecht, Aktivitaet, Ziel

### food_form.html
- Oben: OFF-Suchfeld mit JavaScript
  - `fetch('/api/food-search?q=...')` aufrufen
  - Ergebnisse als klickbare Liste anzeigen
  - Klick fuellt Formularfelder automatisch aus
- Unten: Formular fuer manuelle Eingabe

### dashboard.html
- Datumsnavigation (vor/zurueck)
- 4 Fortschrittsbalken (Kalorien, Protein, Fett, KH) mit Farb-Ampel
- Zusammenfassung (verbleibend, Prozent)
- Tabelle aller Eintraege mit Edit/Delete-Buttons (nur fuer heute)
- "Lebensmittel hinzufuegen" Button (nur fuer heute)

---

## Schritt 12: Tests

### conftest.py
- `app` Fixture: App mit TestConfig (In-Memory-DB) erstellen
- `client` Fixture: Test-Client
- `auth_client` Fixture: Test-User erstellen und einloggen

### Mindest-Tests (5 Unit + Integration):
1. **test_calculator.py**: BMR maennlich, BMR weiblich, TDEE, Ziel-Modifikator, Makro-Split
2. **test_nutrition.py**: Portionsskalierung, Tagessumme, Fortschrittsstatus
3. **test_integration.py**: Profil speichern, Food hinzufuegen, Dashboard-Response, Health-Endpoint
4. **test_auth.py**: Register, Login, Logout, Zugriffschutz, Daten-Isolation
5. **test_api_client.py**: Normalisierung, Fehlerbehandlung, Deduplizierung (alles gemockt)

---

## Schritt 13: QA-Tools konfigurieren (`pyproject.toml`)

```toml
[tool.black]
line-length = 88

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "W"]

[tool.mypy]
ignore_missing_imports = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Lokal ausfuehren:
```bash
black .
ruff check .
mypy app/
pytest tests/ -v
```

---

## Schritt 14: CI/CD Pipeline (`.github/workflows/ci.yml`)

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-dev.txt
      - run: black --check .
      - run: ruff check .
      - run: mypy app/
      - run: pytest tests/ -v --tb=short
```

---

## Schritt 15: Deployment

**run.py** (Entwicklung):
```python
from app import create_app
app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
```

**wsgi.py** (Produktion):
```python
from app import create_app
app = create_app()
```

**Procfile**:
```
web: gunicorn wsgi:app
```

---

## Schritt 16: Diagramme (Pflicht-Nachweis)

### Klassendiagramm
Zeigt die 4 Modelle (User, UserProfile, DailyGoal, FoodEntry) mit Attributen und Beziehungen (user_id FKs).

### Sequenzdiagramm CI/CD
Zeigt den Ablauf: Push -> GitHub Actions -> Black -> Ruff -> Mypy -> Pytest -> Ergebnis.

Beide als Mermaid-Diagramme in einer `.md`-Datei erstellen.

---

## Reihenfolge der Umsetzung (empfohlen)

| # | Was | Abhaengigkeit |
|---|-----|---------------|
| 1 | Projektstruktur + Dependencies + Config | - |
| 2 | App Factory + Logging | Schritt 1 |
| 3 | Models (alle 4) | Schritt 2 |
| 4 | Calculator (BMR/TDEE/Makros) + Tests | - (reine Funktionen) |
| 5 | Nutrition (Skalierung/Summe/Status) + Tests | - (reine Funktionen) |
| 6 | Forms (alle 5) | Schritt 3 |
| 7 | Auth-Routes (Register/Login/Logout) + Templates | Schritt 3, 6 |
| 8 | Onboarding/Profil-Routes + Templates | Schritt 4, 6, 7 |
| 9 | Dashboard-Route + Template | Schritt 5, 8 |
| 10 | Food CRUD-Routes + Template | Schritt 5, 9 |
| 11 | OFF API-Client + Suchfeld im Food-Template | Schritt 10 |
| 12 | Integration-Tests + Auth-Tests | Schritt 7-11 |
| 13 | pyproject.toml + QA lokal laufen lassen | Schritt 1-12 |
| 14 | GitHub Actions CI-Pipeline | Schritt 13 |
| 15 | Deployment-Konfiguration (wsgi, Procfile) | Schritt 2 |
| 16 | Diagramme | Schritt 3, 14 |

---

*Tipp: Schritte 4 und 5 (Calculator + Nutrition) koennen parallel zu Schritt 3 gemacht werden, da sie keine Flask-Abhaengigkeit haben. TDD-Ansatz: Tests zuerst schreiben, dann Logik implementieren.*
