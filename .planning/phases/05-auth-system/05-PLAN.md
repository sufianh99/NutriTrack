# Phase 5: Authentication System

## Goal

Die App wird Multi-User-fähig: Nutzer können sich registrieren und einloggen, jeder sieht nur seine eigenen Daten (Profil, Goals, Food Entries).

## Requirements

- AUTH-01: Registrierung mit Username + Passwort
- AUTH-02: Login / Logout
- AUTH-03: Geschützte Routen (alle außer Login/Register)
- AUTH-04: Daten-Isolation — jeder User sieht nur seine eigenen Einträge
- AUTH-05: Bestehende Tests weiterhin grün

## Success Criteria

1. Ein neuer Nutzer kann sich mit Username und Passwort registrieren
2. Login/Logout funktioniert, Session bleibt über Requests bestehen
3. Ohne Login wird man auf die Login-Seite umgeleitet
4. Jeder User hat eigenes Profil, eigene DailyGoals und eigene FoodEntries
5. Alle bestehenden Tests + neue Auth-Tests sind grün
6. CI-Pipeline bleibt grün (Black, Ruff, Mypy, pytest)

## Dependencies

- Flask-Login (neu hinzufügen)
- Werkzeug (bereits vorhanden — für `generate_password_hash` / `check_password_hash`)

## Impact Analysis

### Models (`app/models.py`)
- **Neu:** `User` Model mit `id`, `username`, `password_hash` + `UserMixin`
- **Ändern:** `UserProfile` — FK `user_id` hinzufügen
- **Ändern:** `DailyGoal` — FK `user_id` hinzufügen
- **Ändern:** `FoodEntry` — FK `user_id` hinzufügen

### Forms (`app/forms.py`)
- **Neu:** `LoginForm` (username, password)
- **Neu:** `RegisterForm` (username, password, confirm_password)

### Routes (`app/routes.py`)
- **Neu:** `/login` (GET/POST)
- **Neu:** `/register` (GET/POST)
- **Neu:** `/logout`
- **Ändern:** Alle bestehenden Routen — `@login_required` + Queries filtern auf `current_user.id`
- **Ändern:** `_get_profile()` — filtert auf `current_user.id`
- **Ändern:** `_save_profile_and_goals()` — setzt `user_id`
- **Ändern:** `add_food()`, `edit_food()`, `delete_food()` — setzt/prüft `user_id`
- **Ändern:** `dashboard()` — filtert Goals und Entries auf `current_user.id`

### App Init (`app/__init__.py`)
- **Ändern:** `LoginManager` initialisieren, `login_view` setzen, `user_loader` registrieren

### Templates
- **Neu:** `login.html`, `register.html`
- **Ändern:** `base.html` — Nav-Links für Login/Logout/Register
- **Entfernen:** Onboarding-Redirect auf `/` — stattdessen Login-Redirect

### DB-Migration
- SQLite: `db.create_all()` erstellt neue Spalten nicht auf bestehenden Tabellen
- Strategie: DB löschen und neu erstellen (Dev-Umgebung), oder Alembic für Migration

### Tests
- Bestehende Test-Fixtures brauchen einen eingeloggten User
- Neue Tests: Register, Login, Logout, Zugriffschutz, Daten-Isolation

---

## Plan: 3 Schritte

### Plan 05-01: User Model + Flask-Login Setup
**Dateien:** `requirements.txt`, `app/models.py`, `app/__init__.py`

Tasks:
1. `Flask-Login==0.6.3` zu `requirements.txt` hinzufügen
2. `User` Model erstellen (id, username, password_hash) mit `UserMixin`
3. FKs `user_id` zu `UserProfile`, `DailyGoal`, `FoodEntry` hinzufügen (nullable=True für Migration)
4. `LoginManager` in `app/__init__.py` konfigurieren + `user_loader`
5. DB neu erstellen (instance/nutritrack.db löschen)

### Plan 05-02: Auth Routes + Templates
**Dateien:** `app/forms.py`, `app/routes.py`, `app/templates/login.html`, `app/templates/register.html`, `app/templates/base.html`

Tasks:
1. `LoginForm` und `RegisterForm` erstellen
2. `/register` Route — User anlegen, Passwort hashen, einloggen, redirect zu Onboarding
3. `/login` Route — Credentials prüfen, `login_user()`, redirect zu Dashboard
4. `/logout` Route — `logout_user()`, redirect zu Login
5. `login.html` und `register.html` Templates erstellen
6. `base.html` — Nav anpassen (Login/Register wenn anonym, Logout wenn eingeloggt)
7. `@login_required` auf alle geschützten Routen
8. Index-Route: anonym → Login, eingeloggt ohne Profil → Onboarding, sonst → Dashboard

### Plan 05-03: Daten-Isolation + Tests
**Dateien:** `app/routes.py`, `app/models.py`, `tests/conftest.py`, `tests/test_auth.py`

Tasks:
1. Alle DB-Queries in Routes auf `current_user.id` filtern
2. `_get_profile()` → `WHERE user_id = current_user.id`
3. `_save_profile_and_goals()` → setzt `user_id = current_user.id`
4. `add_food()`, `edit_food()`, `delete_food()` → setzt/prüft `user_id`
5. Dashboard-Query → filtert auf `current_user.id`
6. Test-Fixtures aktualisieren: User erstellen + einloggen
7. Neue Tests: Register, Login, Logout, Redirect wenn nicht eingeloggt, Daten-Isolation (User A sieht nicht User B's Einträge)
8. Alle bestehenden Tests grün halten
9. CI-Check: Black, Ruff, Mypy, pytest

---

## Risiken

| Risiko | Mitigation |
|--------|------------|
| Bestehende DB bricht durch Schema-Änderung | Dev-DB löschen und neu erstellen |
| Bestehende Tests brechen ohne Login-Context | Fixtures mit authentifiziertem Client |
| Mypy-Fehler durch Flask-Login types | `type: ignore` wo nötig, Flask-Login stubs |

---

*Erstellt: 2026-03-27*
