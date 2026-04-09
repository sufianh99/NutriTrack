# Testing

## Überblick

Wir verwenden **pytest** als Test-Framework. Unsere Tests sind aufgeteilt in:

| Kategorie | Datei | Anzahl | Was wird getestet |
|-----------|-------|--------|-------------------|
| Unit Test | `test_calculator.py` | 5 | BMR, TDEE, Ziel-Modifier, Makros |
| Unit Test | `test_nutrition.py` | 5 | Portionsskalierung, Tagessumme, Ampel |
| Unit Test | `test_api_client.py` | 5 | API-Suche, Fehlerbehandlung, Fallback |
| Integration | `test_integration.py` | 3 | Profil speichern, Food hinzufügen, Dashboard |
| Integration | `test_auth.py` | 2 | Registrierung, Login |
| **Gesamt** | | **20** | |

## Unterschied Unit Test vs. Integrationstest

**Unit Tests** testen eine einzelne Funktion isoliert:
```python
def test_bmr_male():
    result = calculate_bmr(weight_kg=70.0, height_cm=175.0, age=30, gender="male")
    assert result == pytest.approx(1648.75, abs=0.01)
```
→ Kein Flask, keine Datenbank, kein HTTP. Nur die reine Funktion.

**Integrationstests** testen das Zusammenspiel mehrerer Komponenten:
```python
def test_food_entry_add(auth_client, app):
    client, user = auth_client
    client.post("/onboarding", data=VALID_PROFILE)
    response = client.post("/food/add", data=VALID_FOOD)
    assert response.status_code == 302
```
→ HTTP-Request → Route → Formular-Validierung → Datenbank → Redirect. Alles zusammen.

## Test-Fixtures (`conftest.py`)

Fixtures sind wiederverwendbare Bausteine, die vor jedem Test automatisch bereitgestellt werden:

```python
@pytest.fixture
def app():
    application = create_app(TestConfig)   # App mit Test-Konfiguration
    with application.app_context():
        db.create_all()                     # Tabellen erstellen
        yield application
        db.drop_all()                       # Nach dem Test aufräumen

@pytest.fixture
def client(app):
    return app.test_client()                # Simulierter Browser

@pytest.fixture
def auth_client(app, client):
    # User erstellen und einloggen
    user = User(username="testuser", password_hash=...)
    db.session.add(user)
    db.session.commit()
    # Session setzen (= eingeloggt)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
    return client, user
```

- `app` → Erstellt eine frische App mit leerer In-Memory-Datenbank
- `client` → Simuliert einen Browser, der Requests an die App schickt
- `auth_client` → Wie `client`, aber mit eingeloggtem User

## Mocking (API-Tests)

Für API-Tests wollen wir nicht wirklich das Internet aufrufen. Mit `patch()` ersetzen wir den echten HTTP-Call durch eine simulierte Antwort:

```python
with patch("app.api_client.requests.get") as mock_get:
    mock_get.return_value = _mock_response({"products": [...]})
    results = search_food("Haferflocken")
    assert len(results) == 1
```

Vorteile:
- Tests sind schnell (kein Netzwerk-Call)
- Tests sind zuverlässig (kein Abhängigkeit von externer API)
- Wir können Fehlerfälle simulieren (Timeout, 503, etc.)

## Tests ausführen

```bash
pytest tests/ -v --tb=short     # Alle Tests mit Details
pytest tests/test_calculator.py  # Nur Calculator-Tests
pytest -k "test_bmr"            # Nur Tests die "test_bmr" im Namen haben
```
