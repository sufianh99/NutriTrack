# NutriTrack
Dein buddy für Gewichtsverlust und Muskelaufbau

## Lokale Entwicklung (WSL/Ubuntu)
- Voraussetzungen: Python 3.11+, pip, Git; empfohlen: WSL Ubuntu
- Repository: in `~/Projects/Nutritracker/NutriTrack`

```bash
cd ~/Projects/Nutritracker/NutriTrack
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
mkdir -p instance
python run.py
```

Hinweise:
- Die SQLite-Datei liegt standardmäßig unter `NutriTrack/instance/nutritrack.db` (siehe `config.py`).
- `SECRET_KEY` und `DATABASE_URL` können per Umgebungsvariablen oder `.env` gesetzt werden; sonst greifen Default-Werte aus `config.py`.
- Abbruch: `Strg+C` im Terminal beendet den Server.

Bei DB-Problemen: venv aktivieren, alte SQLite löschen, App neu starten, damit das Schema neu erstellt wird.
```bash
cd ~/Projects/Nutritracker/NutriTrack
deactivate 2>/dev/null || true
source .venv/bin/activate
rm -f instance/nutritrack.db
python run.py
```
