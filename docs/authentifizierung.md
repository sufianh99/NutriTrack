# Authentifizierung

## Überblick

Wir verwenden **Flask-Login** für die Session-basierte Authentifizierung. Jeder Benutzer hat einen eigenen Account mit Username und Passwort.

## Wie Login funktioniert

```
User gibt Username + Passwort ein
        │
        ▼
routes.py (login)
        │
        ├── User in DB suchen (nach Username)
        ├── Passwort-Hash vergleichen
        │
        ├── Korrekt → Session erstellen → Redirect zu Dashboard
        └── Falsch  → Fehlermeldung anzeigen
```

## Passwort-Hashing

Passwörter werden **nie** im Klartext gespeichert. Wir verwenden Werkzeug für das Hashing:

```python
# Beim Registrieren: Passwort → Hash
password_hash = generate_password_hash("meinPasswort123")
# Ergebnis: "scrypt:32768:8:1$..."  (nicht umkehrbar)

# Beim Login: Eingabe gegen Hash prüfen
check_password_hash(user.password_hash, "meinPasswort123")  # True oder False
```

Der Hash kann nicht zurück in das Passwort umgewandelt werden. Man kann nur prüfen, ob ein eingegebenes Passwort zum gespeicherten Hash passt.

## User-Model mit UserMixin

```python
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
```

`UserMixin` ist ein Mixin-Klasse von Flask-Login. Sie liefert automatisch Methoden, die Flask-Login braucht:
- `is_authenticated` → Ist der User eingeloggt?
- `is_active` → Ist der Account aktiv?
- `get_id()` → Gibt die User-ID als String zurück

## User Loader

Flask-Login muss wissen, wie es einen User aus der Datenbank laden kann. Das definieren wir in `app/__init__.py`:

```python
@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))
```

Bei jedem Request schaut Flask-Login in der Session nach der User-ID und lädt den User über diese Funktion.

## Route-Schutz mit @login_required

Alle geschützten Routes haben den `@login_required` Decorator:

```python
@bp.route("/dashboard")
@login_required
def dashboard():
    ...
```

Wenn ein nicht eingeloggter User `/dashboard` aufruft, wird er automatisch zu `/login` weitergeleitet.

## Datenisolation

Jede Datenbankabfrage filtert nach `current_user.id`:

```python
entries = db.session.execute(
    select(FoodEntry).where(FoodEntry.user_id == current_user.id)
).scalars().all()
```

So sieht User A nur seine eigenen Daten und nicht die von User B.

## Formulare

Zwei Formulare für die Authentifizierung in `app/forms.py`:

**LoginForm:** Username + Passwort
**RegisterForm:** Username + Passwort + Passwort-Bestätigung

Die Passwort-Bestätigung wird mit `EqualTo` geprüft:
```python
confirm_password = PasswordField(
    "Passwort bestätigen",
    validators=[EqualTo("password", message="Passwörter stimmen nicht überein.")]
)
```
