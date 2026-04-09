# ORM-Mapping

## Was ist ORM?

ORM steht für **Object-Relational Mapping**. Es ist die Brücke zwischen Python-Klassen und Datenbanktabellen. Statt SQL zu schreiben, arbeiten wir mit Python-Objekten — SQLAlchemy übersetzt das automatisch in SQL.

## Wie das Mapping funktioniert

Jede Klasse in `app/models.py` wird einer Datenbanktabelle zugeordnet:

```
Python-Klasse          →    Datenbanktabelle
Klassen-Attribut       →    Tabellenspalte
Objekt-Instanz         →    Tabellenzeile
```

## Beispiel: FoodEntry

```python
class FoodEntry(db.Model):
    __tablename__ = "food_entry"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount_g: Mapped[float] = mapped_column(Float, nullable=False)
```

Was hier passiert:
- `__tablename__ = "food_entry"` → Die Klasse wird der Tabelle `food_entry` zugeordnet
- `Mapped[int]` → Typ-Annotation für Mypy (Typsicherheit)
- `mapped_column(Integer, primary_key=True)` → Spalte vom Typ Integer, ist Primärschlüssel
- `ForeignKey("user.id")` → Verweist auf die `id`-Spalte der `user`-Tabelle
- `nullable=False` → Darf nicht leer sein

## SQLAlchemy 2.x Stil

Wir verwenden den neuen SQLAlchemy 2.x Stil mit `Mapped[]` und `mapped_column()`. Der ältere Stil sah so aus:

```python
# ALT (SQLAlchemy 1.x)
name = db.Column(db.String(200), nullable=False)

# NEU (SQLAlchemy 2.x) - was wir verwenden
name: Mapped[str] = mapped_column(String(200), nullable=False)
```

Der Vorteil vom neuen Stil: Die Typ-Annotationen (`Mapped[str]`) machen den Code kompatibel mit Mypy. Der Type-Checker weiß dadurch, dass `entry.name` ein String ist.

## Fremdschlüssel (Foreign Keys)

Alle Tabellen sind über `user_id` mit der `user`-Tabelle verknüpft:

```python
user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
```

Das stellt sicher:
- Jeder Eintrag gehört zu einem existierenden User
- Die Datenbank verhindert ungültige Verweise
- Wir können alle Daten eines Users gezielt abfragen

## CRUD-Operationen

Durch das Mapping können wir Datenbankoperationen als Python-Code schreiben:

**Create:**
```python
entry = FoodEntry(user_id=1, name="Banane", amount_g=120.0, ...)
db.session.add(entry)
db.session.commit()
```

**Read:**
```python
entries = db.session.execute(
    select(FoodEntry).where(FoodEntry.user_id == current_user.id)
).scalars().all()
```

**Update:**
```python
form.populate_obj(entry)  # Übernimmt Formulardaten ins Objekt
db.session.commit()
```

**Delete:**
```python
db.session.delete(entry)
db.session.commit()
```

## Zusammenhang mit dem Rest

```
forms.py          →  Validiert Eingaben
    ↓
models.py         →  Mapped Python-Objekte auf DB-Tabellen
    ↓
SQLAlchemy ORM    →  Übersetzt in SQL
    ↓
SQLite            →  Speichert die Daten in nutritrack.db
```
