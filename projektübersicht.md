# Projektübersicht - NutriTrack

## Projektstruktur

```
NutriTrack/
├── app/                        # Hauptpaket der Anwendung
│   ├── __init__.py             # Application Factory (create_app)
│   ├── models.py               # OOP-Klassen: User, UserProfile, DailyGoal, FoodEntry
│   ├── forms.py                # OOP-Klassen: LoginForm, RegisterForm, OnboardingForm, ...
│   ├── routes.py               # Blueprint mit allen Routes (URL → Logik)
│   ├── calculator.py           # Reine Funktionen: BMR, TDEE, Makros
│   ├── nutrition.py            # Reine Funktionen: Skalierung, Summierung, Ampel
│   ├── api_client.py           # Open Food Facts API-Anbindung
│   ├── logging_config.py       # Logging-Konfiguration
│   ├── templates/              # Jinja2 HTML-Templates
│   │   ├── base.html           # Basis-Layout (Bootstrap, Navigation)
│   │   ├── login.html          # Login-Seite
│   │   ├── register.html       # Registrierung
│   │   ├── onboarding.html     # Erstmalige Profil-Eingabe
│   │   ├── profile.html        # Profil bearbeiten
│   │   ├── dashboard.html      # Hauptansicht mit Soll/Ist-Vergleich
│   │   └── food_form.html      # Lebensmittel hinzufügen/bearbeiten
│   └── static/
│       └── style.css           # Eigenes CSS
├── tests/                      # Testpaket
│   ├── conftest.py             # Fixtures (app, client, auth_client)
│   ├── test_calculator.py      # 5 Unit Tests für calculator.py
│   ├── test_nutrition.py       # 5 Unit Tests für nutrition.py
│   ├── test_api_client.py      # 5 Unit Tests für api_client.py
│   ├── test_integration.py     # 3 Integrationstests (Profil, Food, Dashboard)
│   └── test_auth.py            # 2 Integrationstests (Register, Login)
├── config.py                   # Config und TestConfig Klassen
├── run.py                      # Einstiegspunkt: python run.py
└── docs/                       # Diagramme (Mermaid)
```

---

## OOP-Konzepte im Projekt

### 1. Model-Klassen (Vererbung + Attribute)

In `app/models.py` liegen die vier zentralen Datenmodell-Klassen. Jede erbt von `db.Model` (SQLAlchemy), wodurch sie automatisch einer Datenbanktabelle zugeordnet wird:

```
db.Model                        ← SQLAlchemy Basisklasse (ORM)
├── User                        ← erbt auch von UserMixin (Flask-Login)
├── UserProfile
├── DailyGoal
└── FoodEntry
```

**`User`** — Repräsentiert einen Benutzer
- **Attribute:** `id`, `username`, `password_hash`
- **Vererbung:** Erbt von `UserMixin` (Flask-Login) → bekommt dadurch Methoden wie `is_authenticated`, `get_id()` geschenkt, ohne sie selbst implementieren zu müssen. Das ist ein klassisches **Mixin-Pattern** (Mehrfachvererbung).

**`UserProfile`** — Das Profil eines Benutzers (1:1 Beziehung zu User)
- **Attribute:** `age`, `height_cm`, `weight_kg`, `gender`, `activity_level`, `goal`
- **Fremdschlüssel:** `user_id → User.id`

**`DailyGoal`** — Berechnete Tagesziele (1:n Beziehung zu User, pro Tag ein Eintrag)
- **Attribute:** `calorie_goal`, `protein_goal`, `fat_goal`, `carb_goal`, `date`
- **Fremdschlüssel:** `user_id → User.id`

**`FoodEntry`** — Ein gegessenes Lebensmittel (n:1 Beziehung zu User)
- **Attribute:** `name`, `amount_g`, `calories_per_100g`, `protein_per_100g`, etc.
- **Fremdschlüssel:** `user_id → User.id`

**OOP-Prinzip:** Jede Klasse kapselt zusammengehörige Daten (**Kapselung**). Die Vererbung von `db.Model` sorgt dafür, dass alle Models automatisch CRUD-Operationen (Create, Read, Update, Delete) über SQLAlchemy bekommen, ohne dass wir SQL schreiben müssen.

---

### 2. Form-Klassen (Vererbung + Validierung)

In `app/forms.py` erben alle Formulare von `FlaskForm`:

```
FlaskForm                       ← Flask-WTF Basisklasse (CSRF + Validierung)
├── LoginForm                   ← username, password
├── RegisterForm                ← username, password, confirm_password
├── OnboardingForm              ← age, height_cm, weight_kg, gender, ...
├── FoodEntryForm               ← name, amount_g, calories_per_100g, ...
└── DeleteForm                  ← leer, nur für CSRF-Token
```

**OOP-Prinzip:** Durch Vererbung von `FlaskForm` bekommt jedes Formular:
- Automatischen **CSRF-Schutz**
- Eine `validate_on_submit()`-Methode
- Eine `populate_obj()`-Methode um Model-Objekte zu befüllen

Jedes Feld (z.B. `StringField`, `FloatField`) ist selbst ein Objekt mit Validatoren wie `DataRequired()`, `NumberRange(min=10, max=120)`. Das ist **Komposition** — die Form-Klasse besteht aus Field-Objekten.

---

### 3. Config-Klassen (Vererbung)

In `config.py`:

```
Config                          ← Basis-Konfiguration (SECRET_KEY, DB-Pfad)
└── TestConfig                  ← Erbt von Config, überschreibt DB → In-Memory SQLite
```

**OOP-Prinzip:** `TestConfig` überschreibt nur das, was für Tests anders sein muss (`TESTING = True`, SQLite in-memory). Alles andere wird von `Config` geerbt. Das ist klassische **Vererbung mit Überschreibung**.

---

### 4. Application Factory Pattern

In `app/__init__.py` wird `create_app()` als Factory-Funktion genutzt:

```python
def create_app(config_class=Config):
    app = Flask(__name__)          # Flask-Objekt erstellen
    db.init_app(app)               # Datenbank-Objekt anbinden
    login_manager.init_app(app)    # Login-Manager anbinden
    app.register_blueprint(bp)     # Routes registrieren
    return app
```

Das ist das **Factory Pattern** — eine Funktion erstellt und konfiguriert ein komplexes Objekt. Der Vorteil: Man kann verschiedene Konfigurationen übergeben (z.B. `TestConfig` für Tests).

---

### 5. Blueprint (Modularisierung)

In `routes.py` werden alle Routes in einem `Blueprint`-Objekt gruppiert:

```python
bp = Blueprint("main", __name__)
```

Ein Blueprint ist ein Objekt, das Routes sammelt und später bei der App registriert wird. Das ermöglicht Modularität — man könnte theoretisch mehrere Blueprints für verschiedene App-Bereiche haben.

---

## Wie alles zusammenhängt

```
User öffnet Browser
        │
        ▼
    routes.py          ← Empfängt HTTP-Request, prüft Login
        │
        ├──► models.py         ← Liest/schreibt Daten (User, FoodEntry, ...)
        │       │
        │       ▼
        │    SQLite DB          ← Persistente Speicherung
        │
        ├──► calculator.py     ← Berechnet BMR → TDEE → Kalorienziel → Makros
        │
        ├──► nutrition.py      ← Skaliert Portionen, summiert Tageswerte, Ampel
        │
        ├──► api_client.py     ← Sucht Lebensmittel über Open Food Facts API
        │
        ├──► forms.py          ← Validiert Eingaben (Formulare)
        │
        ▼
    templates/*.html   ← Rendert HTML mit Daten → zurück an Browser
```

**Ablauf-Beispiel "Lebensmittel hinzufügen":**
1. User klickt "Hinzufügen" → `GET /food/add` → `routes.py` rendert `food_form.html` mit leerem `FoodEntryForm`
2. User tippt Suchbegriff → JavaScript ruft `GET /api/food-search?q=Haferflocken` → `api_client.py` fragt Open Food Facts API → Ergebnisse als JSON zurück → JS füllt Formularfelder
3. User klickt "Speichern" → `POST /food/add` → `FoodEntryForm.validate_on_submit()` prüft Eingaben → neues `FoodEntry`-Objekt erstellt → `db.session.add()` + `commit()` → Redirect zu Dashboard
4. Dashboard: `routes.py` lädt alle `FoodEntry`-Objekte des Tages → `nutrition.py` skaliert und summiert → `progress_status()` berechnet Ampelfarben → `dashboard.html` zeigt Soll/Ist-Balken

---

## Zusammenfassung OOP-Konzepte

| Konzept | Wo im Projekt | Beispiel |
|---------|--------------|----------|
| **Klassen & Objekte** | models.py, forms.py, config.py | `User`, `FoodEntry`, `OnboardingForm` |
| **Vererbung** | Überall | `User(UserMixin, db.Model)`, `TestConfig(Config)` |
| **Mehrfachvererbung (Mixin)** | models.py | `User` erbt von `UserMixin` UND `db.Model` |
| **Kapselung** | models.py | Jede Klasse bündelt zusammengehörige Attribute |
| **Komposition** | forms.py | Forms bestehen aus Field-Objekten mit Validatoren |
| **Factory Pattern** | `__init__.py` | `create_app()` erstellt konfigurierte App-Instanz |
| **Überschreibung** | config.py | `TestConfig` überschreibt DB-URI von `Config` |
