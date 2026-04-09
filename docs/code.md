# Code-Erklärung NutriTrack

Jede Datei im Projekt erklärt — was sie macht, warum, und wie sie mit dem Rest zusammenhängt.

---

## config.py

```python
import os

basedir = os.path.abspath(os.path.dirname(__file__))
```
`basedir` speichert den absoluten Pfad zum Projektordner. `__file__` ist der Pfad zu dieser Datei selbst, `dirname` gibt den Ordner zurück, `abspath` macht ihn absolut.

```python
os.makedirs(os.path.join(basedir, "instance"), exist_ok=True)
```
Erstellt den `instance/`-Ordner falls er nicht existiert. Dort liegt die SQLite-Datenbank.

```python
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(basedir, 'instance', 'nutritrack.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```
- `SECRET_KEY` — Wird für die Session-Verschlüsselung und CSRF-Schutz gebraucht. Versucht erst die Umgebungsvariable zu lesen, nimmt sonst einen Default.
- `SQLALCHEMY_DATABASE_URI` — Pfad zur Datenbank. Im Produktionsmodus kommt der Pfad aus der Umgebungsvariable, lokal zeigt er auf `instance/nutritrack.db`.
- `SQLALCHEMY_TRACK_MODIFICATIONS = False` — Schaltet ein Flask-SQLAlchemy-Feature ab, das wir nicht brauchen und Performance kostet.

```python
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
```
Erbt von `Config` und überschreibt nur das, was für Tests anders sein muss:
- `TESTING = True` — Flask weiß, dass es im Testmodus läuft
- `sqlite:///:memory:` — Datenbank nur im RAM, wird nach jedem Test gelöscht
- `WTF_CSRF_ENABLED = False` — CSRF-Token in Tests ausschalten, sonst müssten wir in jedem Test ein Token mitschicken

**Mögliche Rückfrage: "Warum Vererbung bei Config?"**
→ Damit wir den Großteil der Konfiguration nicht doppelt schreiben müssen. `TestConfig` erbt alles von `Config` und ändert nur 3 Werte.

---

## app/__init__.py — Application Factory

```python
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message = "Bitte zuerst einloggen."
login_manager.login_message_category = "warning"
```
- `db` — Das zentrale Datenbank-Objekt. Wird hier erstellt, aber noch nicht mit einer App verbunden.
- `login_manager` — Verwaltet die Login-Logik. `login_view` sagt Flask-Login: "Wenn jemand nicht eingeloggt ist, leite zu dieser Route weiter."

```python
def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)
```
Das ist die **Application Factory**. Statt die App direkt als globale Variable zu erstellen, haben wir eine Funktion, die sie baut. So können wir verschiedene Konfigurationen übergeben (z.B. `TestConfig` in Tests).

- `Flask(__name__)` — Erstellt die Flask-App. `__name__` sagt Flask, wo das Paket liegt.
- `from_object(config_class)` — Lädt die Config-Klasse (alle Großbuchstaben-Attribute werden zu Flask-Config-Werten).
- `init_app()` — Verbindet db und login_manager mit dieser konkreten App-Instanz.

```python
    from app.logging_config import configure_logging
    configure_logging(app)
```
Konfiguriert das Logging (siehe logging_config.py).

```python
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        return db.session.get(User, int(user_id))
```
Flask-Login speichert die User-ID in der Session (Cookie). Bei jedem Request muss es den User aus der DB laden — diese Funktion sagt ihm wie. `db.session.get(User, int(user_id))` ist ein Primary-Key-Lookup.

```python
    from app import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app
```
- `register_blueprint` — Registriert alle Routes bei der App.
- `db.create_all()` — Erstellt alle Tabellen in der DB (falls sie noch nicht existieren). Schaut sich dafür alle Klassen an, die von `db.Model` erben.

**Mögliche Rückfrage: "Warum Application Factory und nicht einfach `app = Flask(__name__)` global?"**
→ Weil wir in Tests eine andere Konfiguration brauchen (In-Memory-DB, CSRF aus). Mit der Factory können wir `create_app(TestConfig)` aufrufen.

---

## app/models.py — Datenmodelle

```python
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
```
- `UserMixin` — Mixin von Flask-Login. Gibt der Klasse Methoden wie `is_authenticated` und `get_id()`, ohne dass wir sie selbst schreiben müssen.
- `db.Model` — SQLAlchemy Basisklasse. Macht die Klasse zu einem Datenbank-Model.
- `__tablename__` — Name der Tabelle in der Datenbank.
- `Mapped[int]` — Typ-Annotation für Mypy. Sagt dem Type-Checker: dieses Attribut ist ein int.
- `mapped_column(Integer, primary_key=True)` — Definiert eine Spalte. `primary_key=True` = eindeutiger Identifikator, wird automatisch hochgezählt.
- `unique=True` — Kein zweiter User darf den gleichen Username haben.
- `nullable=False` — Darf nicht leer sein.

```python
class UserProfile(db.Model):
    __tablename__ = "user_profile"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    activity_level: Mapped[str] = mapped_column(String(20), nullable=False)
    goal: Mapped[str] = mapped_column(String(20), nullable=False)
```
- `ForeignKey("user.id")` — Fremdschlüssel. Verweist auf die `id`-Spalte der `user`-Tabelle. So weiß die DB: dieses Profil gehört zu diesem User.

`DailyGoal` und `FoodEntry` folgen dem gleichen Muster. Jede Tabelle hat `user_id` als Fremdschlüssel.

**Mögliche Rückfrage: "Warum speichern wir `password_hash` und nicht das Passwort?"**
→ Sicherheit. Wenn die DB geleakt wird, kann niemand die Passwörter lesen. Der Hash ist eine Einwegfunktion — man kann das Passwort nicht zurückrechnen.

**Mögliche Rückfrage: "Was ist der Unterschied zwischen `Mapped[int]` und `mapped_column(Integer)`?"**
→ `Mapped[int]` ist nur für den Type-Checker (Mypy), `mapped_column(Integer)` ist für SQLAlchemy/die Datenbank. Beides zusammen sorgt dafür, dass sowohl Python als auch die DB wissen, welcher Typ es ist.

---

## app/forms.py — Formulare

```python
class OnboardingForm(FlaskForm):
    age = IntegerField("Alter", validators=[DataRequired(), NumberRange(min=10, max=120)])
    height_cm = FloatField("Größe (cm)", validators=[DataRequired(), NumberRange(min=100, max=250)])
    ...
    submit = SubmitField("Speichern")
```
- `FlaskForm` — Basisklasse von Flask-WTF. Stellt CSRF-Schutz und Validierung bereit.
- Jedes Feld ist ein Objekt (`IntegerField`, `FloatField`, `SelectField`...) mit Validatoren.
- `DataRequired()` — Feld darf nicht leer sein.
- `NumberRange(min=10, max=120)` — Wert muss zwischen 10 und 120 liegen.

```python
class DeleteForm(FlaskForm):
    pass
```
Leeres Formular — existiert nur, um ein CSRF-Token für den Löschen-Button zu generieren. Ohne dieses Token könnte eine bösartige Website den User dazu bringen, ungewollt etwas zu löschen (Cross-Site Request Forgery).

**Mögliche Rückfrage: "Was ist CSRF?"**
→ Cross-Site Request Forgery. Eine Attacke, bei der eine fremde Website einen Request an unsere App schickt, der so aussieht, als käme er vom eingeloggten User. Das CSRF-Token verhindert das, weil es ein geheimes Token ist, das nur unser Formular kennt.

**Mögliche Rückfrage: "Was macht `validate_on_submit()`?"**
→ Prüft ob (1) der Request ein POST war und (2) alle Validatoren bestanden haben. Gibt True oder False zurück.

---

## app/calculator.py — Bedarfsberechnung

```python
PAL_FACTORS: dict[str, float] = {
    "sedentary": 1.200,
    "light": 1.375,
    "moderate": 1.550,
    "active": 1.725,
    "very_active": 1.900,
}
```
PAL = Physical Activity Level. Jedes Aktivitätslevel hat einen Faktor, mit dem der Grundumsatz multipliziert wird.

```python
def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
    return base + 5.0 if gender == "male" else base - 161.0
```
Die **Mifflin-St-Jeor-Formel** für den Grundumsatz (BMR = Basal Metabolic Rate).
- Männer: `(10 × Gewicht) + (6.25 × Größe) - (5 × Alter) + 5`
- Frauen: gleiche Formel, aber `-161` statt `+5`

```python
def calculate_tdee(bmr: float, activity_level: str) -> float:
    return bmr * PAL_FACTORS[activity_level]
```
TDEE = Total Daily Energy Expenditure. Grundumsatz × Aktivitätsfaktor = tatsächlicher Kalorienverbrauch pro Tag.

```python
def apply_goal_modifier(tdee: float, goal: str) -> float:
    return tdee * GOAL_MODIFIERS[goal]
```
Je nach Ziel wird der TDEE angepasst: Abnehmen = -15%, Halten = 0%, Zunehmen = +10%.

```python
def calculate_macros(calorie_goal: float) -> dict[str, float]:
    return {
        "protein_g": round((calorie_goal * 0.25) / KCAL_PER_GRAM_PROTEIN, 1),
        "fat_g": round((calorie_goal * 0.30) / KCAL_PER_GRAM_FAT, 1),
        "carbs_g": round((calorie_goal * 0.45) / KCAL_PER_GRAM_CARBS, 1),
    }
```
Verteilt die Kalorien auf Makronährstoffe: 25% Protein, 30% Fett, 45% Kohlenhydrate. Teilt durch den Brennwert pro Gramm (Protein=4, Fett=9, Kohlenhydrate=4) um Gramm zu bekommen.

**Wichtig:** Dieses Modul hat **keine Flask-Imports**. Es ist reines Python. Das macht es einfach zu testen — kein App-Kontext nötig.

**Mögliche Rückfrage: "Warum sind das reine Funktionen und keine Klasse?"**
→ Die Funktionen haben keinen Zustand. Sie bekommen Werte rein und geben Ergebnisse zurück. Eine Klasse wäre hier Overengineering — es gibt nichts, was man als Objekt kapseln müsste.

---

## app/nutrition.py — Nährwertlogik

```python
def scale_nutrients(amount_g, calories_per_100g, protein_per_100g, fat_per_100g, carbs_per_100g):
    factor = amount_g / 100.0
    return {
        "calories": round(calories_per_100g * factor, 1),
        ...
    }
```
Wenn wir 150g Haferflocken essen und die Nährwerte pro 100g kennen, multiplizieren wir mit `150/100 = 1.5`. Einfacher Dreisatz.

```python
def sum_daily_nutrients(entries: list[dict[str, float]]) -> dict[str, float]:
    return {
        "calories": round(sum(e["calories"] for e in entries), 1),
        ...
    }
```
Summiert alle Einträge eines Tages auf. `sum(e["calories"] for e in entries)` ist ein Generator-Ausdruck — geht durch alle Einträge und summiert die Kalorien.

```python
def progress_status(actual: float, goal: float) -> str:
    if goal <= 0:
        return ""
    ratio = actual / goal
    if ratio < 0.90:
        return ""          # Unter 90% → kein Farbcode
    if ratio <= 1.00:
        return "success"   # 90-100% → grün
    return "danger"         # Über 100% → rot
```
Bestimmt die Ampelfarbe für die Fortschrittsbalken im Dashboard. Gibt Bootstrap-CSS-Klassen zurück (`success` = grün, `danger` = rot).

**Mögliche Rückfrage: "Was passiert wenn goal 0 ist?"**
→ Division durch 0 vermeiden. Wenn kein Ziel gesetzt ist, geben wir einen leeren String zurück (kein Farbcode).

---

## app/api_client.py — Open Food Facts API

```python
_SEARCH_URLS = [
    "https://search.openfoodfacts.org/search",
    "https://world.openfoodfacts.org/api/v2/search",
]
```
Zwei URLs. Wenn die erste nicht geht (z.B. Server down), wird die zweite probiert.

```python
def search_food(query: str, max_results: int = 10) -> list[dict]:
    try:
        products = _fetch_products(query, max_results * 3)
        # ... filtern, normalisieren, deduplizieren
        return results
    except Exception:
        return []
```
Die Hauptfunktion. Holt Produkte von der API, filtert leere raus, entfernt Duplikate, normalisiert die Feldnamen. **Gibt niemals einen Fehler weiter** — bei jedem Problem kommt eine leere Liste zurück.

```python
def _fetch_products(query: str, max_results: int) -> list[dict]:
    for url in _SEARCH_URLS:
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            return data.get("products", [])
        except Exception:
            continue
```
Versucht jede URL der Reihe nach. `requests.get()` macht den HTTP-Aufruf. `raise_for_status()` wirft einen Fehler wenn der Statuscode nicht 200 ist (z.B. 503). `timeout=8` bricht nach 8 Sekunden ab.

**Mögliche Rückfrage: "Warum `max_results * 3`?"**
→ Wir holen mehr Produkte als nötig, weil einige nach dem Filtern (leere Nährwerte, Duplikate) wegfallen. So haben wir am Ende trotzdem genug Ergebnisse.

**Mögliche Rückfrage: "Warum gibt die Funktion bei Fehler eine leere Liste zurück statt einen Fehler zu werfen?"**
→ Die App soll auch ohne Internetverbindung funktionieren. Der User kann Nährwerte immer noch manuell eintippen.

---

## app/routes.py — Alle Routes

### Authentifizierung

```python
@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        existing = db.session.execute(
            select(User).where(User.username == form.username.data)
        ).scalar_one_or_none()
        if existing:
            flash("Benutzername bereits vergeben.", "danger")
            return render_template("register.html", form=form)
        user = User(
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data),
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("main.onboarding"))
    return render_template("register.html", form=form)
```
Schritt für Schritt:
1. Ist der User schon eingeloggt? → Redirect zur Startseite
2. Formular erstellen
3. Wurde das Formular abgeschickt UND ist es gültig? (`validate_on_submit`)
4. Gibt es den Username schon? → Fehlermeldung
5. Neuen User erstellen, Passwort hashen, in DB speichern
6. User direkt einloggen und zum Onboarding weiterleiten
7. Bei GET-Request oder ungültigem Formular: Template anzeigen

### Login

```python
@bp.route("/login", methods=["GET", "POST"])
def login():
    ...
    user = db.session.execute(
        select(User).where(User.username == form.username.data)
    ).scalar_one_or_none()
    if user and check_password_hash(user.password_hash, form.password.data):
        login_user(user)
        ...
```
- `select(User).where(...)` — SQL: `SELECT * FROM user WHERE username = '...'`
- `scalar_one_or_none()` — Gibt entweder den einen User zurück oder `None`
- `check_password_hash` — Vergleicht das eingegebene Passwort mit dem gespeicherten Hash

### Hilfsfunktionen

```python
def _get_profile() -> UserProfile | None:
    return db.session.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    ).scalar_one_or_none()
```
Holt das Profil des aktuell eingeloggten Users. Wird in mehreren Routes verwendet.

```python
def _save_profile_and_goals(form: OnboardingForm) -> None:
```
Speichert das Profil und berechnet gleichzeitig die Tagesziele:
1. Profil aus Formular in DB speichern
2. BMR berechnen → TDEE berechnen → Ziel-Modifier anwenden → Makros berechnen
3. DailyGoal für heute erstellen/aktualisieren

Hier sieht man, wie `calculator.py` verwendet wird:
```python
    bmr = calculate_bmr(form.weight_kg.data, form.height_cm.data, form.age.data, form.gender.data)
    tdee = calculate_tdee(bmr, form.activity_level.data)
    calorie_goal = apply_goal_modifier(tdee, form.goal.data)
    macros = calculate_macros(calorie_goal)
```

### Dashboard

```python
@bp.route("/dashboard")
@login_required
def dashboard():
```
`@login_required` — Decorator von Flask-Login. Wenn der User nicht eingeloggt ist, wird er automatisch zu `/login` weitergeleitet.

Der Dashboard-Code macht folgendes:
1. Profil prüfen — kein Profil → Redirect zu Onboarding
2. Datum bestimmen — aus URL-Parameter oder heute
3. Tagesziele laden (`DailyGoal` für heute)
4. Alle Lebensmitteleinträge für das Datum laden
5. Nährwerte skalieren (Portion × Werte pro 100g)
6. Tagessumme berechnen
7. Ampelfarben berechnen (progress_status)
8. Prozentwerte und Restwerte berechnen
9. Alles an das Template übergeben

```python
    scaled = [scale_nutrients(e.amount_g, e.calories_per_100g, ...) for e in entries]
    totals = sum_daily_nutrients(scaled)
```
List Comprehension: Für jeden Eintrag die Nährwerte skalieren, dann alles summieren.

### Food CRUD

```python
@bp.route("/food/add", methods=["GET", "POST"])
@login_required
def add_food():
    ...
    entry = FoodEntry(
        user_id=current_user.id,
        date=date.today(),
        name=form.name.data,
        ...
    )
    db.session.add(entry)
    db.session.commit()
```
Neues FoodEntry-Objekt erstellen, mit den Formulardaten befüllen, in die DB schreiben.

```python
@bp.route("/food/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_food(entry_id: int):
    entry = db.session.execute(
        select(FoodEntry).where(
            FoodEntry.id == entry_id, FoodEntry.user_id == current_user.id
        )
    ).scalar_one_or_none()
```
`<int:entry_id>` — Flask URL-Parameter. `/food/5/edit` → `entry_id = 5`. Die Query prüft sowohl die ID als auch die User-ID → ein User kann nur seine eigenen Einträge bearbeiten.

```python
    form = FoodEntryForm(obj=entry)
    if form.validate_on_submit():
        form.populate_obj(entry)
        db.session.commit()
```
- `FoodEntryForm(obj=entry)` — Füllt das Formular mit den existierenden Werten vor.
- `populate_obj(entry)` — Übernimmt die neuen Formulardaten zurück ins Objekt. SQLAlchemy trackt die Änderungen automatisch, daher reicht ein `commit()`.

```python
@bp.route("/food/<int:entry_id>/delete", methods=["POST"])
```
Nur POST, kein GET. Man kann nicht durch einfaches Aufrufen einer URL etwas löschen. Der Löschen-Button im Template schickt ein POST-Formular mit CSRF-Token.

### API-Route

```python
@bp.route("/api/food-search")
@login_required
def food_search():
    q = request.args.get("q", "")
    if len(q) < 2:
        return jsonify([]), 200
    results = search_food(q)
    return jsonify(results), 200
```
Wird vom JavaScript aufgerufen. `request.args.get("q")` liest den URL-Parameter (`?q=Haferflocken`). Gibt JSON zurück statt HTML.

**Mögliche Rückfrage: "Was ist ein Blueprint?"**
→ Ein Blueprint gruppiert zusammengehörige Routes. Man kann ihn wie ein Sub-Modul bei der App registrieren. In unserem Fall haben wir nur einen (`main`), aber bei größeren Apps könnte man z.B. einen `auth`-Blueprint und einen `tracking`-Blueprint haben.

---

## app/logging_config.py

```python
def configure_logging(app: Flask) -> None:
    logger = logging.getLogger("nutritrack")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
```
Erstellt einen Logger namens "nutritrack". `StreamHandler` schreibt auf die Konsole. Das `if not logger.handlers` verhindert, dass bei Tests mehrere Handler angehängt werden (jeder Test erstellt eine neue App).

In `routes.py` wird der Logger so verwendet:
```python
logger.info("Food entry added: %s, %.1fg", form.name.data, form.amount_g.data)
```

---

## Templates

### base.html — Basistemplate

```html
{% block content %}{% endblock %}
```
Definiert einen Block, den Kindtemplates überschreiben. Das ist **Template-Vererbung** — wie Klassen-Vererbung, aber für HTML.

```html
{% if current_user.is_authenticated %}
    <a href="/dashboard">Dashboard</a>
{% else %}
    <a href="/login">Einloggen</a>
{% endif %}
```
Jinja2-Bedingung. Zeigt unterschiedliche Navigation je nachdem ob der User eingeloggt ist.

```html
{% for category, message in get_flashed_messages(with_categories=true) %}
    <div class="alert alert-{{ category }}">{{ message }}</div>
{% endfor %}
```
Flash-Messages anzeigen. `flash("Gespeichert!", "success")` aus routes.py wird hier als grüne Box gerendert.

### dashboard.html — Fortschrittsbalken

```html
{% set pct_cal = percentages.get('calories', 0) %}
<div class="progress-bar {% if st_cal %}bg-{{ st_cal }}{% endif %}"
     style="width: {{ [pct_cal, 100] | min }}%">
```
- `{% set %}` — Jinja2-Variable setzen
- `bg-{{ st_cal }}` — Wird zu `bg-success` (grün) oder `bg-danger` (rot) je nach Ampelstatus
- `[pct_cal, 100] | min` — Begrenzt die Breite auf maximal 100% (sonst würde der Balken überlaufen)

### food_form.html — API-Suche mit JavaScript

```javascript
fetch('/api/food-search?q=' + encodeURIComponent(query))
    .then(function (resp) { return resp.json(); })
    .then(function (items) {
        items.forEach(function (item) {
            btn.addEventListener('click', function () {
                document.getElementById('name').value = item.name;
                document.getElementById('calories_per_100g').value = item.calories_per_100g;
                ...
            });
        });
    });
```
1. `fetch()` — Schickt einen HTTP-GET an unsere API-Route
2. `.then(resp => resp.json())` — Wandelt die Antwort von JSON-Text in ein JavaScript-Objekt
3. Für jedes Ergebnis wird ein Button erstellt
4. Beim Klick werden die Formularfelder mit den Nährwerten befüllt

**Mögliche Rückfrage: "Warum `encodeURIComponent`?"**
→ Sonderzeichen im Suchbegriff (z.B. Leerzeichen, Umlaute) müssen für URLs kodiert werden. Aus "Müsli Bar" wird "M%C3%BCsli%20Bar".

---

## tests/conftest.py — Test-Fixtures

```python
@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()
```
- `@pytest.fixture` — Markiert die Funktion als wiederverwendbaren Baustein für Tests
- `create_app(TestConfig)` — App mit In-Memory-DB erstellen
- `yield` — Gibt die App an den Test zurück. Alles nach `yield` ist Aufräum-Code.
- `_db.drop_all()` — Löscht alle Tabellen nach dem Test

```python
@pytest.fixture
def auth_client(app, client):
    user = User(username="testuser", password_hash=generate_password_hash("testpass123"))
    _db.session.add(user)
    _db.session.commit()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
    return client, user
```
Erstellt einen eingeloggten Test-User. `session_transaction()` manipuliert die Flask-Session direkt — so simulieren wir ein Login ohne die Login-Route aufrufen zu müssen.

**Mögliche Rückfrage: "Was ist `yield` und warum nicht `return`?"**
→ `yield` gibt den Wert zurück, aber die Funktion läuft danach weiter. So können wir nach dem Test aufräumen (`drop_all`). Mit `return` wäre die Funktion sofort beendet.

---

## run.py — Einstiegspunkt

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```
- `create_app()` — Erstellt die App mit der Standard-Config
- `if __name__ == "__main__"` — Nur ausführen wenn die Datei direkt gestartet wird (nicht beim Import)
- `debug=True` — Auto-Reload bei Code-Änderungen, detaillierte Fehlermeldungen

---

## Gesamtfluss: Vom Request zur Antwort

```
1. User ruft /dashboard auf
2. Flask findet die passende Route in routes.py
3. @login_required prüft: User eingeloggt?
   → Nein: Redirect zu /login
   → Ja: Weiter
4. Route-Funktion läuft:
   a. Profil aus DB laden (models.py)
   b. Einträge aus DB laden (models.py)
   c. Nährwerte skalieren (nutrition.py)
   d. Tagessumme berechnen (nutrition.py)
   e. Ampelfarben berechnen (nutrition.py)
5. render_template("dashboard.html", ...) → Jinja2 rendert HTML
6. HTML geht zurück an den Browser
```
