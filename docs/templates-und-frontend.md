# Templates und Frontend

## Überblick

Wir verwenden **Jinja2** (Flasks Template-Engine) für das HTML und **Bootstrap 5** für das Styling. Kein React, kein Vue — alles serverseitig gerendert.

## Template-Vererbung

Alle Templates erben von `base.html`. Das ist ein OOP-Konzept angewandt auf HTML:

```
base.html                    ← Navigation, Footer, Bootstrap-Einbindung
├── login.html               ← Erbt Layout, füllt eigenen Content
├── register.html
├── onboarding.html
├── profile.html
├── dashboard.html
└── food_form.html
```

**base.html** definiert Blöcke, die Kindtemplates überschreiben können:

```html
<!-- base.html -->
<title>NutriTrack - {% block title %}Startseite{% endblock %}</title>
<main>
    {% block content %}{% endblock %}
</main>
{% block scripts %}{% endblock %}
```

```html
<!-- dashboard.html -->
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block content %}
    <h1>Dein Dashboard</h1>
    ...
{% endblock %}
```

Das ist wie Vererbung bei Klassen: `base.html` ist die Basisklasse, die Kindtemplates überschreiben nur die Teile, die sich unterscheiden.

## Jinja2-Syntax

**Variablen ausgeben:**
```html
<p>Hallo {{ current_user.username }}!</p>
<p>Kalorien: {{ totals.calories }} kcal</p>
```

**Bedingungen:**
```html
{% if current_user.is_authenticated %}
    <a href="/dashboard">Dashboard</a>
{% else %}
    <a href="/login">Einloggen</a>
{% endif %}
```

**Schleifen:**
```html
{% for row in entry_rows %}
    <tr>
        <td>{{ row.entry.name }}</td>
        <td>{{ row.scaled.calories }} kcal</td>
    </tr>
{% endfor %}
```

## Flash Messages

Flask kann Einmal-Nachrichten senden (z.B. "Erfolgreich gespeichert"):

```python
# In routes.py:
flash("Lebensmittel hinzugefügt.", "success")
```

```html
<!-- In base.html: -->
{% for category, message in get_flashed_messages(with_categories=true) %}
    <div class="alert alert-{{ category }}">{{ message }}</div>
{% endfor %}
```

`category` ist eine Bootstrap-Klasse (`success` = grün, `danger` = rot, `warning` = gelb).

## Bootstrap 5

Bootstrap wird über CDN eingebunden (kein lokaler Download nötig):

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
```

Wir nutzen Bootstrap-Klassen für:
- **Navigation:** `navbar`, `navbar-dark`, `bg-success`
- **Layout:** `container`, `row`, `col`
- **Formulare:** `form-control`, `form-label`
- **Fortschrittsbalken:** `progress`, `progress-bar`
- **Farben:** `bg-success` (grün), `bg-danger` (rot)

## JavaScript (Vanilla)

Für die Lebensmittelsuche verwenden wir reines JavaScript ohne Bibliotheken:

```javascript
fetch(`/api/food-search?q=${suchbegriff}`)
    .then(response => response.json())
    .then(results => {
        // Dropdown anzeigen
        // Bei Klick: Formularfelder ausfüllen
    });
```

Das Script ist direkt in `food_form.html` im `{% block scripts %}`-Block eingebettet.

## Zusammenhang mit dem Backend

```
routes.py
    │
    ├── Daten zusammenstellen (Models, Calculator, Nutrition)
    │
    └── render_template("dashboard.html",
            profile=profile,
            goal=goal,
            entry_rows=entry_rows,
            totals=totals,
            statuses=statuses,
            ...)
            │
            ▼
        Jinja2 rendert HTML mit den übergebenen Daten
            │
            ▼
        Fertiges HTML → an den Browser
```

Jede Variable die in `render_template()` übergeben wird, ist im Template als `{{ variable }}` verfügbar.
