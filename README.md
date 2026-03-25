# NutriTrack

NutriTrack ist eine webbasierte Ernährungs-Tracking-Anwendung, die Nutzern hilft, ihren täglichen Energie- und Nährstoffbedarf individuell zu berechnen und ihre Ernährung datenbasiert zu tracken. Die Anwendung besteht aus zwei Kernmodulen: Bedarfsberechnung nach der Mifflin-St-Jeor-Formel und Ernährungstracking mit Soll/Ist-Vergleich und farblicher Ampel. Zielgruppe sind Personen, die Kalorienverbrauch und Makronährstoffzufuhr (Protein, Fett, Kohlenhydrate) kontrollieren möchten.

## Features

- **Profil / Onboarding**: Nutzerprofil anlegen mit Alter, Größe, Gewicht, Geschlecht, Aktivitätslevel und Ziel
- **Grundumsatz (BMR)**: Berechnung nach Mifflin-St-Jeor-Formel
- **Gesamtumsatz (TDEE)**: Multiplikation mit PAL-Faktor (1.2 bis 1.9) je nach Aktivitätslevel
- **Kalorienziel**: Ableitung aus Ziel — Abnehmen (-15%), Halten (0%), Zunehmen (+10%)
- **Makroverteilung**: Automatische Berechnung — Protein 25%, Fett 30%, Kohlenhydrate 45%
- **Lebensmitteleingabe (CRUD)**: Mahlzeiten manuell hinzufügen, bearbeiten und löschen
- **Open Food Facts Suche**: Nährwerte aus der Open Food Facts Datenbank abrufen
- **Dashboard mit Soll/Ist-Vergleich**: Tagesbedarf vs. tatsächliche Zufuhr im Überblick
- **Farbliche Ampel**: Grün (90-100% des Ziels), Rot (>100%) — sofort erkennbarer Status
- **Datumsnavigation / Verlauf**: Vergangene Tage navigieren und Einträge einsehen

## Architecture

### Tech Stack

| Technologie | Version | Zweck |
|-------------|---------|-------|
| Python | 3.9+ | Laufzeitumgebung |
| Flask | 3.1.3 | Web-Framework |
| Flask-SQLAlchemy | 3.1.1 | ORM / DB-Integration |
| SQLite | stdlib | Persistente Datenspeicherung |
| Jinja2 | (via Flask) | Template-Engine |
| Flask-WTF | 1.2.2 | Formulare und CSRF-Schutz |
| gunicorn | 23.0.0 | WSGI-Server für Produktion |

### Project Structure

```
NutriTrack/
├── app/
│   ├── __init__.py          # Flask App Factory (create_app)
│   ├── models.py            # SQLAlchemy-Modelle (UserProfile, DailyGoal, FoodEntry)
│   ├── calculator.py        # BMR, TDEE, Makroberechnung (reines Python)
│   ├── nutrition.py         # Portionsskalierung, Tagessummen, Ampelstatus
│   ├── api_client.py        # Open Food Facts API Wrapper
│   ├── routes.py            # Flask-Routen (Blueprint 'main')
│   ├── forms.py             # WTForms-Klassen (Onboarding, FoodEntry, Delete)
│   ├── logging_config.py    # Strukturiertes Logging
│   ├── static/              # CSS, JavaScript, statische Assets
│   └── templates/           # Jinja2-Templates
├── tests/                   # pytest Test-Suite (Unit + Integration)
├── docs/                    # Diagramme (Klassendiagramm, Sequenzdiagramm)
│   ├── klassendiagramm.mmd  # Mermaid-Klassendiagramm
│   └── sequenzdiagramm-ci.mmd  # Mermaid-Sequenzdiagramm CI/CD
├── .github/workflows/
│   └── ci.yml               # GitHub Actions CI-Pipeline
├── config.py                # App-Konfiguration (Config, TestConfig)
├── run.py                   # Entwicklungsserver
├── wsgi.py                  # WSGI-Einstiegspunkt für gunicorn (Produktion)
├── Procfile                 # Render/Railway Startbefehl
├── .env.example             # Vorlage für Umgebungsvariablen
├── requirements.txt         # Python-Laufzeitabhängigkeiten
└── requirements-dev.txt     # Entwicklungs- und QA-Abhängigkeiten
```

### Two Core Modules

**1. Bedarfsberechnung (`app/calculator.py`)**

Reine Python-Funktionen ohne Flask- oder SQLAlchemy-Importe — ermöglicht isoliertes Unit-Testing und Mypy-Kompatibilität.

- `calculate_bmr(weight_kg, height_cm, age, gender)` — Mifflin-St-Jeor BMR
  - Male: `(10 * weight) + (6.25 * height) - (5 * age) + 5`
  - Female: `(10 * weight) + (6.25 * height) - (5 * age) - 161`
- `calculate_tdee(bmr, activity_level)` — TDEE = BMR * PAL-Faktor
- `apply_goal_modifier(tdee, goal)` — Zielanpassung (0.85 / 1.0 / 1.10)
- `calculate_macros(calorie_goal)` — Makrosplit: Protein 25%, Fett 30%, KH 45%

**2. Ernährungstracking (`app/nutrition.py` + `app/routes.py`)**

- `scale_nutrients(amount_g, ...)` — Nährwerte von 100g auf Portionsgröße skalieren
- `sum_daily_nutrients(entries)` — Tageseinträge aufsummieren
- `progress_status(actual, goal)` — Ampelstatus: `""` (unter 90%), `"success"` (90-100%), `"danger"` (über 100%)
- CRUD-Routen für Lebensmitteleinträge mit CSRF-Schutz via Flask-WTF

### Data Model

| Tabelle | Beschreibung |
|---------|-------------|
| `user_profile` | Einzelnes Nutzerprofil (id=1); Alter, Größe, Gewicht, Geschlecht, Aktivitätslevel, Ziel |
| `daily_goal` | Ein Eintrag pro Datum; berechnete Tagesziele für Kalorien und Makros |
| `food_entry` | Mehrere Einträge pro Datum; Lebensmittelname, Menge (g), Nährwerte pro 100g |

## Setup (Lokale Installation)

### Voraussetzungen

- Python 3.9 oder neuer
- Git

### Schritt-für-Schritt

**1. Repository klonen**

```bash
git clone https://github.com/your-username/NutriTrack.git
cd NutriTrack
```

**2. Virtuelle Umgebung erstellen und aktivieren**

```bash
# Linux / macOS
python -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# Windows (CMD)
python -m venv venv
venv\Scripts\activate.bat
```

**3. Abhängigkeiten installieren**

```bash
pip install -r requirements.txt
```

**4. Umgebungsvariablen konfigurieren**

```bash
cp .env.example .env
```

Die `.env`-Datei öffnen und `SECRET_KEY` auf einen zufälligen Wert setzen:

```
SECRET_KEY=mein-zufaelliger-geheimer-schluessel-hier
DATABASE_URL=sqlite:///instance/nutritrack.db
```

**5. Anwendung starten**

```bash
python run.py
```

Die Anwendung ist unter http://127.0.0.1:5000 erreichbar.

**6. Onboarding**

Beim ersten Aufruf wird automatisch auf das Onboarding-Formular weitergeleitet, wo Profildaten eingegeben werden.

## Usage (Bedienungsanleitung)

### 1. Onboarding

Beim ersten Start wird das Profil-Formular angezeigt. Folgende Angaben sind erforderlich:

- **Alter** (Jahre)
- **Größe** (cm)
- **Gewicht** (kg)
- **Geschlecht** (Männlich / Weiblich)
- **Aktivitätslevel**:
  - Sitzend (wenig Bewegung) — PAL 1.2
  - Leicht aktiv (1-3x/Woche Sport) — PAL 1.375
  - Mäßig aktiv (3-5x/Woche Sport) — PAL 1.55
  - Sehr aktiv (6-7x/Woche Sport) — PAL 1.725
  - Extrem aktiv (körperliche Arbeit) — PAL 1.9
- **Ziel**: Abnehmen / Halten / Zunehmen

Nach dem Speichern werden Grundumsatz, Gesamtumsatz und Tagesziele automatisch berechnet.

### 2. Dashboard

Das Dashboard zeigt für den aktuellen Tag:

- Berechnete Soll-Werte (Kalorien, Protein, Fett, Kohlenhydrate)
- Tatsächliche Ist-Werte aus eingetragenen Mahlzeiten
- Fortschrittsbalken mit Ampelfarben:
  - Grau: Unter 90% des Ziels
  - Grün: 90-100% des Ziels (Zielbereich)
  - Rot: Über 100% (Ziel überschritten)
- Liste aller Mahlzeiten des Tages mit Edit- und Lösch-Schaltflächen

### 3. Lebensmittel eintragen

1. Auf "Hinzufügen" klicken
2. Optional: Open Food Facts Suche nutzen — Produktname eingeben und in der Ergebnisliste auswählen (Nährwerte werden automatisch übernommen)
3. Formular ausfüllen: Name, Menge (g), Kalorien/100g, Protein/100g, Fett/100g, KH/100g
4. "Speichern" klicken — Eintrag erscheint sofort im Dashboard

### 4. Einträge bearbeiten und löschen

- **Bearbeiten**: Stift-Symbol beim Eintrag klicken, Werte anpassen, speichern
- **Löschen**: Papierkorb-Symbol klicken (CSRF-geschützt, POST-Request)

### 5. Datumsnavigation / Verlauf

- Pfeiltasten im Dashboard-Header verwenden, um zwischen Tagen zu navigieren
- Vergangene Einträge sind lesbar; neue Einträge können für beliebige Daten erfasst werden

## Testing

### Abhängigkeiten installieren

```bash
pip install -r requirements-dev.txt
```

### Tests ausführen

```bash
# Alle Tests mit Details
python -m pytest tests/ -v

# Nur Unit-Tests
python -m pytest tests/test_calculator.py tests/test_nutrition.py -v

# Integrationstests
python -m pytest tests/test_integration.py -v
```

### Codequalität prüfen

```bash
# Formatierung (Black)
python -m black --check .

# Linting (Ruff)
python -m ruff check .

# Typ-Prüfung (Mypy)
python -m mypy app/ --ignore-missing-imports --disallow-untyped-defs
```

Die Test-Suite umfasst:
- 10 Unit-Tests für `calculator.py` (BMR, TDEE, Makros)
- 12 Unit-Tests für `nutrition.py` (Portionsskalierung, Summierung, Ampelstatus)
- 5 Integrationstests (Onboarding, Dashboard, CRUD-Operationen, /health-Endpoint)

## CI/CD

GitHub Actions Pipeline (`.github/workflows/ci.yml`) läuft bei jedem Push und Pull Request auf `main`:

1. **Black** — Formatierungsprüfung (`black --check .`)
2. **Ruff** — Linting (`ruff check .`)
3. **Mypy** — Statische Typprüfung (`mypy app/`)
4. **pytest** — Test-Suite (`pytest tests/ -v --tb=short`)

Alle vier Schritte müssen grün sein, bevor ein Merge möglich ist.

## Deployment

### Render

1. Neues "Web Service" erstellen und GitHub-Repository verbinden
2. Build Command: `pip install -r requirements.txt`
3. Start Command wird automatisch aus `Procfile` übernommen: `gunicorn wsgi:app`
4. Unter "Environment" folgende Variable setzen:
   - `SECRET_KEY` → zufälliger, sicherer Wert
5. Deploy auslösen — SQLite-Datenbank wird automatisch angelegt

### Railway

1. Repository verbinden — Railway erkennt das `Procfile` automatisch
2. Unter "Variables" eintragen:
   - `SECRET_KEY` → zufälliger, sicherer Wert
3. Deploy starten

### PythonAnywhere

1. Code via Git hochladen oder ZIP-Upload
2. Virtuelle Umgebung erstellen und `pip install -r requirements.txt` ausführen
3. WSGI-Konfigurationsdatei unter "Web" → "Code" auf `wsgi.py` zeigen lassen
4. `SECRET_KEY` in der WSGI-Datei als Umgebungsvariable setzen
5. Web-App neu laden

### Umgebungsvariablen

| Variable | Beschreibung | Pflicht |
|----------|-------------|---------|
| `SECRET_KEY` | Zufälliger Schlüssel für CSRF-Token und Sessions | Ja |
| `DATABASE_URL` | SQLite-Pfad oder externe DB-URL | Nein (Standard: `sqlite:///instance/nutritrack.db`) |

## Diagramme

Die Pflicht-Diagramme befinden sich im Verzeichnis `docs/`:

- **`docs/klassendiagramm.mmd`** — Mermaid-Klassendiagramm der Datenmodelle und Module
- **`docs/sequenzdiagramm-ci.mmd`** — Mermaid-Sequenzdiagramm der CI/CD-Pipeline

Die `.mmd`-Dateien können mit [Mermaid Live Editor](https://mermaid.live/) oder GitHub (direkte Vorschau) gerendert werden.

## Lizenz

Akademisches Projekt — nicht zur Weiterverbreitung lizenziert. Alle Rechte vorbehalten.
