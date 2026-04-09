# Projektretrospektive - NutriTrack

**Datum:** 09.04.2026
**Projektlaufzeit:** 25.03.2026 - 09.04.2026

---

## Was lief gut?

- **Klare Aufgabenverteilung** - Jedes Teammitglied wusste, woran es arbeitet. Die phasenbasierte Planung hat geholfen, Aufgaben sauber abzugrenzen.
- **Frühe CI/CD-Einrichtung** - Automatisierte Quality Gates (Formatter, Linter, Tests) haben Fehler früh sichtbar gemacht und Diskussionen über Code-Stil vermieden.
- **Modularer Code** - Business-Logik wurde vom Framework getrennt gehalten, was das parallele Arbeiten und Testen deutlich vereinfacht hat.
- **Gute Testabdeckung** - Alle Kernfunktionen sind durch Unit- und Integrationstests abgesichert. Das hat uns Sicherheit bei Änderungen gegeben.
- **Kommunikation im Team** - Kurze Abstimmungen zwischen den Phasen haben Missverständnisse früh aufgelöst.

---

## Was lief nicht gut?

- **Querschnittsthemen zu spät bedacht** - Die Authentifizierung kam erst in der letzten Phase. Das hat Nacharbeit am gesamten Datenmodell verursacht. Solche Grundsatzentscheidungen müssen früher fallen.
- **Zeitdruck in den letzten Phasen** - Die ersten Phasen liefen schnell, aber gegen Ende wurde es eng. Bessere Puffer einplanen.
- **Frontend-Tests fehlen** - Wir haben Backend-Tests gut abgedeckt, aber die UI hat keine automatisierten Tests. Das ist ein blinder Fleck.
- **Dokumentation teilweise nachträglich** - Einiges wurde erst nach der Implementierung dokumentiert statt begleitend. Das kostet extra Zeit und Infos gehen verloren.
- **Wenig Code-Reviews** - Nicht jeder Commit wurde von einem zweiten Paar Augen geprüft. Bei einem größeren Team wäre das ein Risiko.

---

## Was haben wir gelernt?

1. **Architekturentscheidungen früh treffen** - Auch wenn ein Feature spät gebaut wird, muss das Datenmodell von Anfang an darauf vorbereitet sein.
2. **CI/CD ist kein Nice-to-Have** - Die Pipeline hat uns mehrfach vor kaputten Commits bewahrt. Früh einrichten lohnt sich immer.
3. **Phasenplanung mit Akzeptanzkriterien** verhindert Scope Creep und gibt eine klare Definition of Done.
4. **Externe APIs sind unzuverlässig** - Fallbacks und sauberes Error-Handling sind Pflicht, nicht optional.
5. **Kleine, atomare Commits** machen die Git-Historie nachvollziehbar und Rollbacks einfach.

---

## Was nehmen wir ins nächste Projekt mit?

| Beibehalten | Ändern |
|-------------|--------|
| Phasenbasierte Entwicklung mit klaren Zielen | Querschnittsthemen (Auth, Rollen) in Phase 1 klären |
| CI/CD ab Tag 1 | Coverage-Reporting in die Pipeline aufnehmen |
| Getrennte Business-Logik und Framework-Code | Frontend-Tests mindestens für kritische Flows |
| Atomare Commits mit klaren Messages | Dokumentation begleitend statt nachträglich |
| Automatisierte Code-Formatierung | Code-Reviews für jeden Merge etablieren |

---

## Stimmungsbild im Team

| Frage | Bewertung |
|-------|-----------|
| Wie zufrieden seid ihr mit dem Ergebnis? | Sehr zufrieden - alle Kernziele erreicht |
| Wie war die Zusammenarbeit? | Gut, kurze Wege, wenig Reibung |
| Würdet ihr den Prozess wiederholen? | Ja, mit den oben genannten Anpassungen |
| Was war der größte Erfolgsmoment? | Erste grüne CI-Pipeline + alle Tests grün |
| Was war der frustrierendste Moment? | Nachträglicher Umbau des Datenmodells für Multi-User |
