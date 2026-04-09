# API-Anbindung (Open Food Facts)

## Was ist die Open Food Facts API?

Open Food Facts ist eine offene Datenbank mit Nährwertinformationen zu Lebensmitteln. Über die API können wir Lebensmittel suchen und deren Nährwerte (Kalorien, Protein, Fett, Kohlenhydrate) abrufen, ohne sie manuell eintippen zu müssen.

## Wo im Projekt

Die gesamte API-Logik liegt in `app/api_client.py`. Das Modul hat eine zentrale Funktion:

```python
def search_food(query: str, max_results: int = 10) -> list[dict]:
```

Diese Funktion nimmt einen Suchbegriff (z.B. "Haferflocken") und gibt eine Liste von Lebensmitteln mit Nährwerten zurück.

## Wie die Suche funktioniert

```
User tippt "Haferflocken" ins Suchfeld
        │
        ▼
JavaScript (fetch) → GET /api/food-search?q=Haferflocken
        │
        ▼
routes.py (food_search) → ruft search_food("Haferflocken") auf
        │
        ▼
api_client.py → HTTP GET an Open Food Facts API
        │
        ▼
API antwortet mit JSON (Produktname, Nährwerte, ...)
        │
        ▼
api_client.py → Normalisiert die Daten in einheitliches Format
        │
        ▼
JSON-Antwort zurück an JavaScript → Füllt Formularfelder aus
```

## Fallback-Mechanismus

Die Open Food Facts API hat zwei URLs. Wenn die erste nicht erreichbar ist (z.B. Serverausfall), wird automatisch die zweite probiert:

```python
_SEARCH_URLS = [
    "https://search.openfoodfacts.org/search",        # Primär
    "https://world.openfoodfacts.org/api/v2/search",   # Fallback
]
```

In `_fetch_products()` wird jede URL der Reihe nach versucht:

```python
for url in _SEARCH_URLS:
    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        return resp.json().get("products", [])
    except Exception:
        continue  # Nächste URL probieren
```

## Fehlerbehandlung

Die `search_food()`-Funktion gibt **niemals** einen Fehler weiter. Bei jedem Problem wird eine leere Liste zurückgegeben:

```python
try:
    products = _fetch_products(query, max_results * 3)
    # ... Verarbeitung
    return results
except Exception:
    return []  # Bei Fehler: leere Liste statt Absturz
```

Das ist wichtig, weil die App auch ohne API-Verbindung funktionieren soll — der User kann Nährwerte immer noch manuell eintippen.

## Daten-Normalisierung

Die API liefert Daten in unterschiedlichen Formaten. Wir normalisieren sie in ein einheitliches Format:

```python
# API liefert:
{"energy-kcal_100g": 372, "proteins_100g": 13.5, "fat_100g": 7.0, ...}

# Wir geben zurück:
{"name": "Haferflocken", "calories_per_100g": 372.0, "protein_per_100g": 13.5, ...}
```

Außerdem:
- Produkte ohne Nährwerte werden herausgefiltert
- Doppelte Produktnamen werden entfernt (Deduplizierung)
- Markennamen werden angehängt: "Haferflocken (Alnatura)"
- Werte werden auf 1 Dezimalstelle gerundet

## Frontend-Integration

In `food_form.html` gibt es ein JavaScript, das bei der Eingabe im Suchfeld die API aufruft und die Formularfelder automatisch befüllt:

```javascript
// Vereinfacht:
fetch(`/api/food-search?q=${suchbegriff}`)
    .then(response => response.json())
    .then(results => {
        // Dropdown mit Ergebnissen anzeigen
        // Bei Klick: Formularfelder ausfüllen
    });
```

## Testen

In den Tests wird die API nicht wirklich aufgerufen. Stattdessen verwenden wir **Mocking** — wir simulieren die API-Antwort:

```python
with patch("app.api_client.requests.get") as mock_get:
    mock_get.return_value = _mock_response({"products": [...]})
    results = search_food("Haferflocken")
```

So sind die Tests schnell, zuverlässig und unabhängig von der Internetverbindung.
