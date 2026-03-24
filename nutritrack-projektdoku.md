# NutriTrack – Projektdokumentation

---

## 1. Produktvision

> „NutriTrack soll Nutzern helfen, ihren täglichen Energie- und Nährstoffbedarf individuell zu berechnen und ihre Ernährung einfach, übersichtlich und datenbasiert zu tracken."

Die Anwendung richtet sich an Personen, die ihren Kalorienverbrauch und ihre Makronährstoffzufuhr kontrollieren möchten – egal ob zur Gewichtsreduktion, zum Gewichtserhalt oder zur gezielten Gewichtszunahme.

---

## 2. Projektziel

Entwicklung einer webbasierten Anwendung mit zwei Kernmodulen:

- **Modul 1 – Bedarfsberechnung:** Individuellen Tagesbedarf auf Basis persönlicher Körperdaten berechnen.
- **Modul 2 – Ernährungstracking:** Lebensmittel erfassen, Nährwerte summieren und Soll/Ist-Vergleich visualisieren.

---

## 3. Tech-Stack

| Schicht | Technologie |
|---|---|
| Backend | Python, Flask |
| Datenbank | SQLite + SQLAlchemy |
| Frontend | HTML/CSS/Jinja2 oder leichtes JS |
| Tests | pytest |
| Linting | Ruff / Flake8 |
| Formatting | Black |
| Type Checking | Mypy |
| CI/CD | GitHub Actions |
| Deployment (optional) | Render / Railway / PythonAnywhere |

---

## 4. MoSCoW-Priorisierung

### Must Have
- Nutzerprofil anlegen (Alter, Größe, Gewicht, Geschlecht, Aktivität, Ziel)
- Grundumsatz + Gesamtumsatz berechnen
- Tägliches Kalorienziel + Makroziele anzeigen
- Lebensmittel manuell hinzufügen
- Nährwerte (kcal, Protein, Fett, KH) aufaddieren
- Soll/Ist-Vergleich im Dashboard anzeigen
- Farbliche Fortschrittsanzeige (normal / grün / orange-rot)
- Daten in SQLite speichern
- Mindestens 5 Unit Tests + Integrationstests
- GitHub Actions CI-Pipeline
- Sequenzdiagramm der Pipeline
- Klassendiagramm

### Should Have
- Externe Lebensmittel-API (z. B. Open Food Facts)
- Tagesverlauf pro Datum anzeigen
- Einträge bearbeiten und löschen
- Tageszusammenfassung
- Logging (Python `logging`-Modul)

### Could Have
- Automatisches Deployment via CD
- `/health`-Endpunkt für Monitoring
- Monitoring-Skript (Cronjob oder GitHub Action)
- Deployment auf Render / Railway

### Won't Have
- Benutzer-Login / Registrierung
- Mobile App
- Barcode-Scanner
- Social Features / Chatbot

---

## 5. User Stories

| ID | Als … | möchte ich … | damit … |
|---|---|---|---|
| US-01 | Nutzer | meine Körperdaten eingeben | mein täglicher Bedarf berechnet wird |
| US-02 | Nutzer | meinen Kalorienbedarf sehen | ich weiß, wie viel ich essen darf |
| US-03 | Nutzer | Lebensmittel hinzufügen | mein Tagesverbrauch aktualisiert wird |
| US-04 | Nutzer | meinen Fortschritt sehen | ich mein Essverhalten anpassen kann |
| US-05 | Nutzer | Lebensmittel suchen | ich nicht alles manuell eingeben muss |
| US-06 | Nutzer | vergangene Tage einsehen | ich meinen Verlauf nachvollziehen kann |
| US-07 | Nutzer | Einträge bearbeiten/löschen | ich Fehler korrigieren kann |

---

## 6. Backlog

### Sprint 1 – Grundstruktur & Berechnung
- [ ] Projektstruktur anlegen (Flask, SQLite, pytest)
- [ ] GitHub-Repository + Branch-Strategie einrichten
- [ ] Profilformular (Onboarding) implementieren
- [ ] Grundumsatz berechnen (Mifflin-St-Jeor-Formel)
- [ ] Gesamtumsatz mit Aktivitätsfaktor berechnen
- [ ] Kalorienziel aus Ziel (abnehmen/halten/zunehmen) ableiten
- [ ] Makroverteilung berechnen
- [ ] Unit Tests für Berechnungslogik schreiben
- [ ] Klassendiagramm erstellen

### Sprint 2 – Tracking & Dashboard
- [ ] Lebensmittel-Modell + Datenbank-Tabellen anlegen
- [ ] Lebensmittel manuell hinzufügen (Formular)
- [ ] Nährwerte auf Portionsgröße umrechnen
- [ ] Tagessumme berechnen + speichern
- [ ] Dashboard mit Soll/Ist-Vergleich implementieren
- [ ] Farbliche Fortschrittsanzeige implementieren
- [ ] Integrationstests schreiben (Profil speichern, Food hinzufügen)
- [ ] Logging einbauen

### Sprint 3 – CI/CD & Qualitätssicherung
- [ ] GitHub Actions Workflow erstellen (`.github/workflows/ci.yml`)
- [ ] Black, Ruff, Mypy in Pipeline integrieren
- [ ] Alle Tests automatisch in CI laufen lassen
- [ ] Sequenzdiagramm der CI/CD-Pipeline erstellen
- [ ] README schreiben

### Sprint 4 – Erweiterungen (Should/Could Have)
- [ ] Externe API anbinden (Open Food Facts)
- [ ] Tagesverlauf implementieren
- [ ] Bearbeiten/Löschen von Einträgen
- [ ] `/health`-Endpunkt
- [ ] Deployment (optional)
- [ ] Monitoring-Skript (optional)

---

## 7. Architekturübersicht

```
nutritrack/
│
├── app/
│   ├── __init__.py          # Flask App Factory
│   ├── models.py            # SQLAlchemy-Modelle
│   ├── routes.py            # URL-Routen
│   ├── calculator.py        # Berechnungslogik (Grundumsatz, Makros)
│   ├── nutrition.py         # Nährwertberechnung + Summierung
│   ├── api_client.py        # Anbindung externe API (optional)
│   └── templates/
│       ├── onboarding.html
│       ├── dashboard.html
│       ├── add_food.html
│       └── history.html
│
├── tests/
│   ├── test_calculator.py   # Unit Tests Berechnungslogik
│   ├── test_nutrition.py    # Unit Tests Nährwerte
│   ├── test_status.py       # Unit Tests Fortschrittsstatus
│   └── test_integration.py  # Integrationstests
│
├── .github/
│   └── workflows/
│       └── ci.yml           # CI-Pipeline
│
├── requirements.txt
├── README.md
└── run.py
```

---

## 8. Datenbankmodell

### Tabellen

**users**
| Feld | Typ | Beschreibung |
|---|---|---|
| id | INTEGER PK | Eindeutige ID |
| name | TEXT | Nutzername |
| age | INTEGER | Alter |
| height_cm | FLOAT | Größe in cm |
| weight_kg | FLOAT | Gewicht in kg |
| gender | TEXT | Geschlecht |
| activity_level | TEXT | Aktivitätsfaktor (sedentary / light / moderate / active / very_active) |
| goal | TEXT | Ziel (lose / maintain / gain) |

**daily_goals**
| Feld | Typ | Beschreibung |
|---|---|---|
| id | INTEGER PK | Eindeutige ID |
| user_id | INTEGER FK | Referenz auf users |
| date | DATE | Datum |
| calorie_goal | FLOAT | Kalorienziel in kcal |
| protein_goal | FLOAT | Proteinziel in g |
| fat_goal | FLOAT | Fettziel in g |
| carb_goal | FLOAT | KH-Ziel in g |

**food_entries**
| Feld | Typ | Beschreibung |
|---|---|---|
| id | INTEGER PK | Eindeutige ID |
| user_id | INTEGER FK | Referenz auf users |
| date | DATE | Datum |
| food_name | TEXT | Lebensmittelname |
| amount_g | FLOAT | Menge in g |
| calories | FLOAT | Kalorien |
| protein | FLOAT | Protein in g |
| fat | FLOAT | Fett in g |
| carbs | FLOAT | KH in g |

**foods_cache** *(optional, für API-Suche)*
| Feld | Typ | Beschreibung |
|---|---|---|
| id | INTEGER PK | Eindeutige ID |
| name | TEXT | Lebensmittelname |
| kcal_per_100g | FLOAT | kcal pro 100g |
| protein_per_100g | FLOAT | Protein pro 100g |
| fat_per_100g | FLOAT | Fett pro 100g |
| carbs_per_100g | FLOAT | KH pro 100g |

---

## 9. Fachliche Berechnungslogik

### Grundumsatz (Mifflin-St-Jeor)
```
Männer: (10 × Gewicht) + (6.25 × Größe) − (5 × Alter) + 5
Frauen: (10 × Gewicht) + (6.25 × Größe) − (5 × Alter) − 161
```

### Aktivitätsfaktoren (PAL)
| Level | Faktor |
|---|---|
| sedentary (kaum Bewegung) | 1.2 |
| light (leichte Aktivität, 1–3×/Woche) | 1.375 |
| moderate (moderate Aktivität, 3–5×/Woche) | 1.55 |
| active (intensive Aktivität, 6–7×/Woche) | 1.725 |
| very_active (sehr intensiv / körperliche Arbeit) | 1.9 |

### Kalorienziel aus Ziel
```
abnehmen:  Gesamtumsatz × 0.85  (−15%)
halten:    Gesamtumsatz × 1.00
zunehmen:  Gesamtumsatz × 1.10  (+10%)
```

### Makroverteilung (Standardwerte)
```
Protein:       25% der Gesamtkalorien → ÷ 4 = g
Fett:          30% der Gesamtkalorien → ÷ 9 = g
Kohlenhydrate: 45% der Gesamtkalorien → ÷ 4 = g
```

### Nährwertumrechnung auf Portionsgröße
```
Nährwert = (Wert_pro_100g / 100) × Menge_in_g
```

---

## 10. Testkonzept

### Teststrategie

NutriTrack nutzt zwei Testebenen: **Unit Tests** für isolierte Berechnungslogik und **Integrationstests** für End-to-End-Abläufe im Backend.

### Unit Tests (`tests/test_calculator.py`, `tests/test_nutrition.py`, `tests/test_status.py`)

| Test-ID | Beschreibung | Erwartet |
|---|---|---|
| UT-01 | Grundumsatz Mann korrekt | Mifflin-Formel stimmt |
| UT-02 | Grundumsatz Frau korrekt | Mifflin-Formel stimmt |
| UT-03 | Gesamtumsatz mit Faktor `moderate` | Grundumsatz × 1.55 |
| UT-04 | Kalorienziel `lose` | Gesamtumsatz × 0.85 |
| UT-05 | Makroberechnung aus Kalorienziel | Protein/Fett/KH korrekt |
| UT-06 | Nährwerte auf Portionsgröße umrechnen | Werte × (Menge/100) |
| UT-07 | Summierung mehrerer Lebensmittel | Summe korrekt |
| UT-08 | Fortschrittsstatus `under` (< 100%) | Rückgabe: "normal" |
| UT-09 | Fortschrittsstatus `reached` (≥ 100%) | Rückgabe: "green" |
| UT-10 | Fortschrittsstatus `exceeded` (> 110%) | Rückgabe: "red" |

### Integrationstests (`tests/test_integration.py`)

| Test-ID | Beschreibung | Erwartet |
|---|---|---|
| IT-01 | Profilformular absenden → Datensatz gespeichert | Nutzer in DB vorhanden |
| IT-02 | Lebensmittel hinzufügen → Tagessumme aktualisiert | Summenwert korrekt |
| IT-03 | Request an `/dashboard` → korrekte Soll/Ist-Werte | HTTP 200, Werte stimmen |
| IT-04 | API-Antwort verarbeiten → Nährwerte im Dashboard | Daten korrekt übernommen |

### Werkzeuge
- `pytest` für alle Tests
- `Flask Test Client` für Integrationstests
- SQLite In-Memory-Datenbank für Tests (kein Schreiben auf Disk)

---

## 11. Qualitätssicherungsmaßnahmen

Zusätzlich zu automatisierten Tests werden folgende drei QS-Maßnahmen eingesetzt:

| Nr. | Maßnahme | Werkzeug | Zweck |
|---|---|---|---|
| QS-01 | Code Formatting | `black` | Einheitlicher Codestil |
| QS-02 | Linting | `ruff` | Stilprüfung + Fehlererkennung |
| QS-03 | Type Checking | `mypy` | Typfehler frühzeitig erkennen |

Ergänzend im Entwicklungsprozess:
- **Pull Requests / Vier-Augen-Prinzip** – kein direkter Push auf `main`
- **Definition of Done** – Feature gilt als fertig, wenn: implementiert, getestet, reviewt, dokumentiert

---

## 12. CI/CD-Pipeline

### Branch-Strategie
```
main        → stabile Version (nur per Merge)
develop     → aktuelle Entwicklung
feature/*   → einzelne Features (z. B. feature/calculator)
```

### GitHub Actions Workflow (`.github/workflows/ci.yml`)

```yaml
name: NutriTrack CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Python setup
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Abhängigkeiten installieren
        run: pip install -r requirements.txt

      - name: Black (Formatierung prüfen)
        run: black --check .

      - name: Ruff (Linting)
        run: ruff check .

      - name: Mypy (Type Checking)
        run: mypy app/

      - name: Unit Tests
        run: pytest tests/test_calculator.py tests/test_nutrition.py tests/test_status.py -v

      - name: Integrationstests
        run: pytest tests/test_integration.py -v
```

---

## 13. SDLC – Software Development Life Cycle

| Phase | Inhalt |
|---|---|
| **1. Planung** | Produktvision, Anforderungen, MoSCoW, User Stories, Backlog, Sprints |
| **2. Analyse & Design** | Architektur, Datenmodell, Klassendiagramm, UI-Skizze, Pipeline planen |
| **3. Implementierung** | Backend, Frontend, Datenbank, API-Anbindung, Logging |
| **4. Qualitätssicherung** | Unit Tests, Integrationstests, Linting, Formatting, Type Checking |
| **5. Auslieferung** | CI-Pipeline automatisiert, optional: Deployment auf Render/Railway |
| **6. Betrieb / Monitoring** | `/health`-Endpunkt, Monitoring-Skript, Logs auswerten |

---

## 14. Optionales Deployment & Monitoring

### Deployment (Could Have)
- Zielumgebung: **Render** oder **Railway** (kostenlose Tier)
- CD-Trigger: erfolgreicher Merge auf `main` → automatisches Deployment
- Alternativ: Docker-Container lokal als simulierte Produktivumgebung

### Monitoring-Skript (Beispiel)
```python
import requests, time, logging

URL = "https://nutritrack.onrender.com/health"

def check():
    try:
        r = requests.get(URL, timeout=5)
        if r.status_code == 200:
            logging.info(f"OK – {r.elapsed.total_seconds()*1000:.0f}ms")
        else:
            logging.warning(f"Status {r.status_code}")
    except Exception as e:
        logging.error(f"Nicht erreichbar: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    while True:
        check()
        time.sleep(60)
```

### Health-Check-Endpunkt
```python
@app.route("/health")
def health():
    return {"status": "ok"}, 200
```

---

## 15. Nachweis-Checkliste für die Abgabe

### Pflicht
- [ ] Laufende NutriTrack-App
- [ ] Git-Repository mit Commit-Historie
- [ ] `.github/workflows/ci.yml`
- [ ] Testdateien in `tests/`
- [ ] Nachweis erfolgreicher Pipeline-Läufe (Screenshot / Log)
- [ ] Klassendiagramm
- [ ] Sequenzdiagramm der CI/CD-Pipeline
- [ ] Testkonzept (→ Abschnitt 10)
- [ ] SDLC-Beschreibung (→ Abschnitt 13)
- [ ] README mit Setup-Anleitung

### Optional (für volle Punktzahl)
- [ ] Deployment-URL oder Screenshot Produktivumgebung
- [ ] Monitoring-Log
- [ ] Beschreibung des Deployment-Prozesses
