# CI/CD-Pipeline

## Was ist CI/CD?

- **CI (Continuous Integration):** Bei jedem Push wird der Code automatisch geprüft (Formatierung, Linting, Tests)
- **CD (Continuous Deployment):** Wenn alle Prüfungen bestanden sind, wird die App automatisch deployt

## Unsere Pipeline

Konfiguriert in `.github/workflows/ci.yml`. GitHub Actions führt die Pipeline bei jedem Push auf `main` und bei jedem Pull Request aus.

## Ablauf

```
git push auf main
        │
        ▼
┌─── Job: quality ──────────────────┐
│  1. Python 3.12 einrichten        │
│  2. Dependencies installieren     │
│  3. black --check .               │ ← Formatierung ok?
│  4. ruff check .                  │ ← Keine Linting-Fehler?
│  5. mypy app/                     │ ← Typen korrekt?
│  6. pytest tests/ -v --tb=short   │ ← Tests bestanden?
└───────────────────────────────────┘
        │ Alles grün?
        ▼
┌─── Job: deploy ───────────────────┐
│  Render Deploy-Hook aufrufen      │ ← App deployen
└───────────────────────────────────┘
        │
        ▼
┌─── Job: monitor ──────────────────┐
│  30 Sekunden warten               │
│  Health Check: GET /health        │ ← Läuft die App?
└───────────────────────────────────┘
```

## Die drei Jobs

### 1. quality

Läuft bei **jedem** Push und Pull Request. Prüft den Code in 4 Schritten:

```yaml
- name: Format check (Black)
  run: black --check .

- name: Lint (Ruff)
  run: ruff check .

- name: Type check (Mypy)
  run: mypy app/

- name: Test (pytest)
  run: pytest tests/ -v --tb=short
```

Die Schritte laufen **sequenziell** — wenn einer fehlschlägt, werden die folgenden nicht ausgeführt. So sieht man sofort, wo das Problem liegt.

### 2. deploy

Läuft **nur** wenn:
- Der Push auf `main` war (nicht bei Pull Requests)
- Der `quality`-Job bestanden hat

Ruft einen Webhook bei Render auf, der das Deployment auslöst:

```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

### 3. monitor

Läuft **nach** dem Deploy. Wartet 30 Sekunden und prüft dann, ob die App erreichbar ist:

```yaml
- name: Health check
  run: python scripts/monitor.py
```

Das Script ruft `GET /health` auf und erwartet `{"status": "ok"}`.

## Warum sequenziell und nicht parallel?

Die 4 Quality-Schritte laufen nacheinander, nicht gleichzeitig. Der Grund: Wenn Black fehlschlägt (Formatierung falsch), macht es keinen Sinn Ruff oder Mypy laufen zu lassen. Man bekommt so immer den einfachsten Fehler zuerst.

## Trigger

```yaml
on:
  push:
    branches: [main]       # Bei Push auf main
  pull_request:
    branches: [main]       # Bei PR gegen main
```
