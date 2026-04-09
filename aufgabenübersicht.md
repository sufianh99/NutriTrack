# NutriTrack -- Aufgabenübersicht

Zuordnung aller Backlog-Aufgaben zu den konkreten Dateien und Codezeilen im Projekt.

---

## Sprint 1 -- Grundstruktur & Berechnung

| Aufgabe | Datei(en) | Zeilen | Hinweis |
|---------|-----------|--------|---------|
| Projektstruktur anlegen (Flask, SQLite, pytest) | `app/__init__.py` | 14-35 | App-Factory-Pattern mit SQLAlchemy |
| | `config.py` | 8-14 | DB-URI, Secret Key |
| | `run.py` | 1-7 | Dev-Server Einstiegspunkt |
| | `tests/conftest.py` | komplett | Pytest-Fixtures (app, client, auth_client) |
| GitHub-Repository + Branch-Strategie | `.github/workflows/ci.yml` | 1-8 | Trigger auf push/PR zu main |
| Profilformular (Onboarding) | `app/forms.py` | 44-75 | `OnboardingForm` Klasse |
| | `app/routes.py` | 182-190 | `/onboarding` Route (GET/POST) |
| | `app/templates/onboarding.html` | komplett | Formular-Template |
| Grundumsatz berechnen (Mifflin-St-Jeor) | `app/calculator.py` | 25-32 | `calculate_bmr()` -- Formel Mann/Frau |
| Gesamtumsatz mit Aktivitätsfaktor | `app/calculator.py` | 6-12 | `PAL_FACTORS` Dict (1.2 bis 1.9) |
| | `app/calculator.py` | 35-37 | `calculate_tdee()` = BMR * Faktor |
| Kalorienziel aus Ziel ableiten | `app/calculator.py` | 14-18 | `GOAL_MODIFIERS` (lose=0.85, maintain=1.0, gain=1.10) |
| | `app/calculator.py` | 40-42 | `apply_goal_modifier()` |
| Makroverteilung berechnen | `app/calculator.py` | 20-22 | Konstanten: Protein 25%, Fett 30%, KH 45% |
| | `app/calculator.py` | 45-51 | `calculate_macros()` -- gibt protein_g, fat_g, carbs_g |
| Unit Tests Berechnungslogik | `tests/test_calculator.py` | komplett (89 Zeilen) | 10 Tests: BMR, TDEE, Ziel, Makros |
| Klassendiagramm | `docs/klassendiagramm.mmd` | komplett (127 Zeilen) | Mermaid-Diagramm |
| | `docs/klassendiagramm.puml` | komplett | PlantUML-Version |

---

## Sprint 2 -- Tracking & Dashboard

| Aufgabe | Datei(en) | Zeilen | Hinweis |
|---------|-----------|--------|---------|
| Lebensmittel-Modell + DB-Tabellen | `app/models.py` | 40-50 | `FoodEntry` Klasse |
| | `app/models.py` | 17-26 | `UserProfile` Klasse |
| | `app/models.py` | 29-37 | `DailyGoal` Klasse |
| | `app/models.py` | 10-14 | `User` Klasse |
| Lebensmittel manuell hinzufügen | `app/forms.py` | 78-98 | `FoodEntryForm` Klasse |
| | `app/routes.py` | 318-341 | `/add-food` Route (GET/POST) |
| | `app/templates/food_form.html` | komplett | Formular-Template |
| Nährwerte auf Portionsgröße umrechnen | `app/nutrition.py` | 7-32 | `scale_nutrients()` -- Wert * (Menge/100) |
| Tagessumme berechnen | `app/nutrition.py` | 35-49 | `sum_daily_nutrients()` -- summiert alle Einträge |
| | `app/routes.py` | 241-251 | Aufruf im Dashboard |
| Dashboard mit Soll/Ist-Vergleich | `app/routes.py` | 207-315 | `/dashboard` Route |
| | `app/templates/dashboard.html` | komplett | Anzeige: Ziele, Einträge, Summen, Rest, Prozent |
| Farbliche Fortschrittsanzeige | `app/nutrition.py` | 52-74 | `progress_status()` -- "" / "success" / "danger" |
| Integrationstests | `tests/test_integration.py` | komplett (97 Zeilen) | 5 Tests: Profil, Food, Dashboard, Redirect, Health |
| Logging einbauen | `app/logging_config.py` | komplett (25 Zeilen) | Logger "nutritrack" mit StreamHandler |
| | `app/routes.py` | 58, 75, 85 | Login/Logout/Register Events |
| | `app/routes.py` | 160-167 | Profil-Update Details |
| | `app/routes.py` | 338, 362, 379 | Food: Hinzufügen, Bearbeiten, Löschen |
| | `app/api_client.py` | 75, 119 | API-Fehler (ERROR/WARNING) |

---

## Sprint 3 -- CI/CD & Qualitätssicherung

| Aufgabe | Datei(en) | Zeilen | Hinweis |
|---------|-----------|--------|---------|
| GitHub Actions Workflow erstellen | `.github/workflows/ci.yml` | komplett (73 Zeilen) | 3 Jobs: quality, deploy, monitor |
| Black, Ruff, Mypy in Pipeline | `.github/workflows/ci.yml` | 27, 30, 33 | `black --check .`, `ruff check .`, `mypy app/` |
| | `pyproject.toml` | komplett | Konfiguration aller drei Tools |
| Tests automatisch in CI | `.github/workflows/ci.yml` | 35-36 | `pytest tests/ -v --tb=short` |
| Sequenzdiagramm CI/CD | `docs/sequenzdiagramm-ci.mmd` | komplett (50 Zeilen) | Mermaid: Dev -> GitHub -> Runner -> Deploy -> Monitor |
| README schreiben | `README.md` | komplett | Vision, Features, Architektur, Setup-Anleitung |

---

## Sprint 4 -- Erweiterungen (Should/Could Have)

| Aufgabe | Datei(en) | Zeilen | Hinweis |
|---------|-----------|--------|---------|
| Externe API (Open Food Facts) | `app/api_client.py` | komplett (124 Zeilen) | `search_food()` mit Fallback-URL |
| | `app/routes.py` | 103-111 | `/api/food-search` Endpunkt |
| Tagesverlauf pro Datum | `app/routes.py` | 214-218 | `?date=YYYY-MM-DD` Query-Parameter |
| | `app/routes.py` | 296-297 | Vor-/Zurück-Navigation (prev_date/next_date) |
| Bearbeiten/Löschen von Einträgen | `app/routes.py` | 344-365 | `/edit-food/<id>` Route |
| | `app/routes.py` | 368-381 | `/delete-food/<id>` Route (POST) |
| /health-Endpunkt | `app/routes.py` | 94-97 | `GET /health` -> `{"status": "ok"}` |
| Deployment | `Procfile` | 1 | `web: gunicorn wsgi:app` |
| | `wsgi.py` | komplett | WSGI-Einstiegspunkt für Gunicorn |
| | `.github/workflows/ci.yml` | 38-48 | Deploy-Job: Render Webhook |
| Monitoring-Skript | `scripts/monitor.py` | komplett (22 Zeilen) | Prüft /health, Exit 0 oder 1 |
| | `.github/workflows/ci.yml` | 50-72 | Monitor-Job nach Deploy |

---

## Unit Tests (UT-01 bis UT-10)

| Test-ID | Beschreibung | Datei | Zeilen | Funktion |
|---------|-------------|-------|--------|----------|
| UT-01 | Grundumsatz Mann | `tests/test_calculator.py` | 11-20 | `test_bmr_male_reference_value()` |
| UT-02 | Grundumsatz Frau | `tests/test_calculator.py` | 33-40 | `test_bmr_female_direct()` |
| UT-03 | Gesamtumsatz moderate | `tests/test_calculator.py` | 48-60 | `test_tdee_all_activity_levels()` |
| UT-04 | Kalorienziel lose | `tests/test_calculator.py` | 63-64 | `test_goal_modifier_lose()` |
| UT-05 | Makroberechnung | `tests/test_calculator.py` | 75-79 | `test_macros_standard_split()` |
| UT-06 | Portionsgröße umrechnen | `tests/test_nutrition.py` | 5-13 | `test_150g_portion()` |
| UT-07 | Summierung Lebensmittel | `tests/test_nutrition.py` | 37-49 | `test_two_entries()` |
| UT-08 | Status under (<90%) | `tests/test_nutrition.py` | 63-65 | `test_below_90_percent()` |
| UT-09 | Status reached (90-100%) | `tests/test_nutrition.py` | 71-77 | `test_exactly_90()`, `test_exactly_100()` |
| UT-10 | Status exceeded (>100%) | `tests/test_nutrition.py` | 79-85 | `test_just_above_100()`, `test_well_above_100()` |

---

## Integrationstests (IT-01 bis IT-04)

| Test-ID | Beschreibung | Datei | Zeilen | Funktion |
|---------|-------------|-------|--------|----------|
| IT-01 | Profil speichern -> DB | `tests/test_integration.py` | 29-51 | `test_profile_save()` |
| IT-02 | Food hinzufügen -> Summe | `tests/test_integration.py` | 54-71 | `test_food_entry_add()` |
| IT-03 | Dashboard Soll/Ist | `tests/test_integration.py` | 73-82 | `test_dashboard_response()` |
| IT-04 | Dashboard ohne Profil -> Redirect | `tests/test_integration.py` | 84-89 | `test_dashboard_redirects_without_profile()` |

---

## Qualitätssicherung (QS-01 bis QS-03)

| QS-ID | Maßnahme | CI-Step | Konfiguration | Prüfbefehl |
|-------|----------|---------|---------------|------------|
| QS-01 | Black (Formatting) | `.github/workflows/ci.yml` Zeile 27 | `pyproject.toml` | `black --check .` |
| QS-02 | Ruff (Linting) | `.github/workflows/ci.yml` Zeile 30 | `pyproject.toml` | `ruff check .` |
| QS-03 | Mypy (Type Checking) | `.github/workflows/ci.yml` Zeile 33 | `pyproject.toml` | `mypy app/` |

---

## Nachweis-Checkliste (Pflicht)

| Nachweis | Datei / Ort | Status |
|----------|-------------|--------|
| Laufende App | `run.py`, `wsgi.py` | Implementiert |
| Git-Repository mit Historie | `.git/` | Vorhanden |
| CI-Pipeline | `.github/workflows/ci.yml` | Implementiert (73 Zeilen) |
| Testdateien | `tests/` (6 Dateien) | test_calculator, test_nutrition, test_integration, test_api_client, test_auth, conftest |
| Pipeline-Nachweis | GitHub Actions Runs | Konfiguriert |
| Klassendiagramm | `docs/klassendiagramm.mmd` | Implementiert (127 Zeilen) |
| Sequenzdiagramm CI/CD | `docs/sequenzdiagramm-ci.mmd` | Implementiert (50 Zeilen) |
| Testkonzept | `nutritrack-projektdoku.md` Abschnitt 10 | Dokumentiert |
| SDLC-Beschreibung | `nutritrack-projektdoku.md` Abschnitt 13 | Dokumentiert |
| README | `README.md` | Implementiert |

## Nachweis-Checkliste (Optional)

| Nachweis | Datei / Ort | Status |
|----------|-------------|--------|
| Deployment-URL | `.github/workflows/ci.yml` Zeilen 38-48 | Render-Hook konfiguriert |
| Monitoring-Log | `scripts/monitor.py`, CI Monitor-Job | Implementiert |
| Deployment-Beschreibung | `nutritrack-projektdoku.md` Abschnitt 14 | Dokumentiert |
