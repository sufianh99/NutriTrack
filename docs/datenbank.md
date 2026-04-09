# Datenbank

## Was wir verwenden

**SQLite** als Datenbank und **SQLAlchemy** als ORM (Object-Relational Mapper).

SQLite ist eine dateibasierte Datenbank — es gibt keinen separaten Datenbankserver. Die gesamte Datenbank liegt in einer einzigen Datei unter `instance/nutritrack.db`.

## Warum SQLite?

- Kein Server nötig, keine Installation, keine Konfiguration
- Die Datenbank ist einfach eine Datei im Projektordner
- Für eine Webanwendung dieser Größe völlig ausreichend
- War Projektvorgabe

## Unsere Tabellen

Wir haben 4 Tabellen, die den 4 Model-Klassen in `app/models.py` entsprechen:

```
┌──────────────┐     ┌──────────────────┐
│    user       │     │   user_profile    │
├──────────────┤     ├──────────────────┤
│ id (PK)      │◄────│ user_id (FK)     │
│ username     │     │ age              │
│ password_hash│     │ height_cm        │
└──────────────┘     │ weight_kg        │
       │             │ gender           │
       │             │ activity_level   │
       │             │ goal             │
       │             └──────────────────┘
       │
       │         ┌──────────────────┐
       ├────────►│   daily_goal      │
       │         ├──────────────────┤
       │         │ user_id (FK)     │
       │         │ date             │
       │         │ calorie_goal     │
       │         │ protein_goal     │
       │         │ fat_goal         │
       │         │ carb_goal        │
       │         └──────────────────┘
       │
       │         ┌──────────────────┐
       └────────►│   food_entry      │
                 ├──────────────────┤
                 │ user_id (FK)     │
                 │ date             │
                 │ name             │
                 │ amount_g         │
                 │ calories_per_100g│
                 │ protein_per_100g │
                 │ fat_per_100g     │
                 │ carbs_per_100g   │
                 └──────────────────┘
```

**Beziehungen:**
- Ein `User` hat genau ein `UserProfile` (1:1)
- Ein `User` hat pro Tag ein `DailyGoal` (1:n)
- Ein `User` hat beliebig viele `FoodEntry`-Einträge (1:n)

Alle Tabellen sind über `user_id` als Fremdschlüssel mit der `user`-Tabelle verknüpft. So sind die Daten pro Benutzer isoliert.

## Wie die Datenbank erstellt wird

Wir schreiben kein SQL von Hand. SQLAlchemy liest unsere Model-Klassen und erstellt die Tabellen automatisch beim App-Start:

```python
# in app/__init__.py
with app.app_context():
    db.create_all()
```

`db.create_all()` schaut sich alle Klassen an, die von `db.Model` erben, und erstellt die passenden Tabellen — falls sie noch nicht existieren.

## Wie wir mit der Datenbank arbeiten

Statt SQL-Queries schreiben wir Python-Code:

```python
# Daten lesen
profile = db.session.execute(
    select(UserProfile).where(UserProfile.user_id == current_user.id)
).scalar_one_or_none()

# Daten schreiben
entry = FoodEntry(user_id=1, name="Banane", amount_g=120.0, ...)
db.session.add(entry)
db.session.commit()

# Daten löschen
db.session.delete(entry)
db.session.commit()
```

SQLAlchemy übersetzt das im Hintergrund in SQL-Statements.

## Testkonfiguration

Für Tests verwenden wir eine In-Memory-Datenbank statt einer Datei:

```python
class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
```

Die Datenbank existiert nur im RAM und wird nach jedem Test automatisch gelöscht. So beeinflussen sich Tests nicht gegenseitig.
