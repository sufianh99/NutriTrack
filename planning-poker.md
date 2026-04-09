# Planning Poker - NutriTrack

**Datum:** 25.03.2026
**Teilnehmer:** Tristan, Nils, Lukas, Sufian
**Skala:** Fibonacci (1, 2, 3, 5, 8, 13)

---

## Schätzungen

| Aufgabe | Tristan | Nils | Lukas | Sufian | Ergebnis |
|---------|---------|------|-------|--------|----------|
| Datenmodell & Datenbankstruktur aufsetzen | 3 | 5 | 3 | 3 | **3** |
| Kalorienrechner (Mifflin-St-Jeor) | 2 | 2 | 3 | 2 | **2** |
| Ernährungstracking mit Dashboard | 5 | 8 | 5 | 5 | **5** |
| CI/CD-Pipeline & Tests | 3 | 3 | 5 | 3 | **3** |
| Open Food Facts API anbinden | 5 | 5 | 5 | 8 | **5** |
| Login & Registrierung | 3 | 5 | 3 | 3 | **3** |
| Bestehende Daten auf Multi-User umbauen | 5 | 8 | 5 | 5 | **5** |

---

## Notizen aus den Diskussionen

- **Dashboard:** Nils hat höher geschätzt wegen der Fortschrittsbalken, aber Bootstrap macht das einfacher als gedacht.
- **CI/CD:** Lukas hatte wenig Erfahrung mit GitHub Actions, deshalb höhere Schätzung. Team hat Unterstützung angeboten.
- **API:** Sufian hat darauf hingewiesen, dass die Open Food Facts API teilweise unvollständige Daten liefert. Wir müssen Fallbacks einbauen.
- **Multi-User-Umbau:** Im Nachhinein war das eher eine 8. Das nachträgliche Ändern der Datenbankstruktur war aufwändiger als erwartet.
