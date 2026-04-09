# Linting und Code-Qualität

## Überblick

Wir verwenden drei Tools, die unseren Code automatisch auf Qualität prüfen:

| Tool | Aufgabe | Beispiel |
|------|---------|----------|
| **Black** | Formatierung | Einrückung, Zeilenumbrüche, Anführungszeichen |
| **Ruff** | Linting | Unused Imports, falsche Variablennamen, Code-Fehler |
| **Mypy** | Typ-Prüfung | Falscher Typ übergeben, fehlende Rückgabewerte |

Alle drei laufen automatisch in der CI/CD-Pipeline bei jedem Push.

## Black (Formatter)

Black formatiert den Code automatisch nach einem festen Standard. Es gibt keine Konfigurationsoptionen — alle im Team haben den gleichen Stil.

**Was Black macht:**
```python
# Vorher (uneinheitlich):
x = {"name":"Banane","kcal" :89, "protein":1.1}

# Nachher (Black-formatiert):
x = {"name": "Banane", "kcal": 89, "protein": 1.1}
```

**In der CI-Pipeline:**
```yaml
- name: Format check (Black)
  run: black --check .
```

`--check` bedeutet: Black ändert nichts, sondern prüft nur. Wenn Code nicht formatiert ist, schlägt der CI-Job fehl.

**Lokal anwenden:**
```bash
black .          # Alle Dateien formatieren
black --check .  # Nur prüfen, nichts ändern
```

## Ruff (Linter)

Ruff prüft den Code auf häufige Fehler und Probleme. Es ersetzt ältere Tools wie Flake8 und isort.

**Was Ruff findet:**
```python
from datetime import date    # F401: 'date' imported but unused
import os                    # F401: 'os' imported but unused

def calc(x):
    y = x * 2               # F841: 'y' assigned but never used
```

**In der CI-Pipeline:**
```yaml
- name: Lint (Ruff)
  run: ruff check .
```

**Lokal anwenden:**
```bash
ruff check .        # Prüfen
ruff check --fix .  # Automatisch beheben wo möglich
```

**Konfiguration in `pyproject.toml`:**
```toml
[tool.ruff]
line-length = 88
```

## Mypy (Type Checker)

Mypy prüft, ob die Typen im Code zusammenpassen. Wir verwenden Type Annotations, damit Mypy weiß, welchen Typ jede Variable hat.

**Was Mypy findet:**
```python
def calculate_bmr(weight_kg: float, height_cm: float, age: int) -> float:
    ...

# Mypy meldet Fehler wenn:
calculate_bmr("siebzig", 175.0, 30)  # str statt float!
calculate_bmr(70.0, 175.0, 30.5)     # float statt int!
```

**In der CI-Pipeline:**
```yaml
- name: Type check (Mypy)
  run: mypy app/
```

**Zusammenspiel mit SQLAlchemy:**
Die `Mapped[int]`-Annotationen in unseren Models sind nicht nur für SQLAlchemy, sondern auch für Mypy:

```python
class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80))
```

Mypy weiß dadurch: `user.id` ist ein `int` und `user.username` ist ein `str`.

## Reihenfolge in der Pipeline

Die Tools laufen in einer bewussten Reihenfolge:

```
1. Black    →  Ist der Code richtig formatiert?
2. Ruff     →  Gibt es Code-Fehler (unused imports, ...)?
3. Mypy     →  Stimmen die Typen?
4. pytest   →  Laufen die Tests durch?
```

Wenn Black fehlschlägt, laufen die anderen gar nicht erst. So bekommt man immer den einfachsten Fehler zuerst angezeigt.

## Konfiguration

Alle drei Tools werden in `pyproject.toml` konfiguriert:

```toml
[tool.black]
line-length = 88

[tool.ruff]
line-length = 88

[tool.mypy]
ignore_missing_imports = true
disallow_untyped_defs = true
```
