# NutriTrack

## What This Is

Eine webbasierte Ernährungs-Tracking-Anwendung, die Nutzern hilft, ihren täglichen Energie- und Nährstoffbedarf individuell zu berechnen und ihre Ernährung datenbasiert zu tracken. Zwei Kernmodule: Bedarfsberechnung (Mifflin-St-Jeor) und Ernährungstracking mit Soll/Ist-Vergleich. Richtet sich an Personen, die Kalorienverbrauch und Makronährstoffzufuhr kontrollieren möchten.

## Core Value

Nutzer können ihren individuellen Tagesbedarf berechnen und ihre tatsächliche Nahrungsaufnahme dagegen tracken — mit sofort sichtbarem Soll/Ist-Vergleich und farblicher Ampel.

## Requirements

### Validated

- ✓ Flask-App-Struktur mit SQLAlchemy und SQLite — existing
- ✓ Grundlegende Templates mit Bootstrap 5 — existing

### Active

- [ ] Nutzerprofil anlegen (Alter, Größe, Gewicht, Geschlecht, Aktivitätslevel, Ziel)
- [ ] Grundumsatz berechnen (Mifflin-St-Jeor-Formel)
- [ ] Gesamtumsatz mit Aktivitätsfaktor berechnen
- [ ] Kalorienziel aus Ziel ableiten (abnehmen/halten/zunehmen)
- [ ] Makroverteilung berechnen (Protein 25%, Fett 30%, KH 45%)
- [ ] Lebensmittel manuell hinzufügen (Name, Menge, Nährwerte)
- [ ] Nährwerte auf Portionsgröße umrechnen
- [ ] Tägliche Nährwerte aufaddieren
- [ ] Dashboard mit Soll/Ist-Vergleich
- [ ] Farbliche Fortschrittsanzeige (normal/grün/orange-rot)
- [ ] Daten in SQLite speichern
- [ ] Mindestens 5 Unit Tests + Integrationstests (pytest)
- [ ] GitHub Actions CI-Pipeline (Black, Ruff, Mypy, Tests)
- [ ] Klassendiagramm
- [ ] Sequenzdiagramm der CI/CD-Pipeline

### Out of Scope

- Benutzer-Login / Registrierung — Projektvorgabe: Won't Have, Single-User-App
- Mobile App — Won't Have, Web-only
- Barcode-Scanner — Won't Have, zu aufwändig
- Social Features / Chatbot — Won't Have, nicht im Scope

## Context

- **Brownfield:** Bestehende Flask-App mit Auth-System (Login/Register), das entfernt/umgebaut werden muss — Projektdoku sagt explizit "kein Login"
- **Akademisches Projekt:** Abgabe mit Pflicht-Nachweisen (CI-Pipeline, Tests, Diagramme, SDLC-Beschreibung, README)
- **Berechnungslogik:** Mifflin-St-Jeor-Formel für Grundumsatz, PAL-Faktoren (1.2–1.9), Ziel-Modifikatoren (-15%/0%/+10%), Makrosplit 25/30/45
- **Datenbankmodell:** 4 Tabellen — users, daily_goals, food_entries, foods_cache (optional)
- **Sprint-basiert:** 4 Sprints geplant (Grundstruktur → Tracking → CI/CD → Erweiterungen)
- **Should Have:** Open Food Facts API, Tagesverlauf, Einträge bearbeiten/löschen, Tageszusammenfassung, Logging
- **Could Have:** Auto-Deployment, /health-Endpunkt, Monitoring-Skript

## Constraints

- **Tech Stack**: Python/Flask, SQLite, Jinja2, pytest — Projektvorgabe
- **QA Tools**: Black, Ruff, Mypy — müssen in CI-Pipeline integriert sein
- **CI/CD**: GitHub Actions — Pflichtbestandteil der Abgabe
- **Diagramme**: Klassendiagramm + Sequenzdiagramm CI/CD — Pflicht-Nachweis
- **Tests**: Mindestens 5 Unit Tests + Integrationstests — Pflicht
- **Single User**: Kein Auth, ein Nutzerprofil via Onboarding

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Auth-System entfernen | Projektdoku sagt "Won't Have: Benutzer-Login", Single-User-App | — Pending |
| Mifflin-St-Jeor statt Harris-Benedict | Genauere, modernere Formel für Grundumsatz | — Pending |
| SQLite statt PostgreSQL | Einfachheit, kein Server nötig, Projektvorgabe | — Pending |
| Open Food Facts als externe API | Kostenlos, offen, gute Abdeckung | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-24 after initialization*
