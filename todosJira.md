# NutriTrack - Jira Tickets

## Epic: Authentifizierung & Benutzerverwaltung

| Ticket | Titel | Priorität | Beschreibung |
|--------|-------|-----------|--------------|
| NT-001 | Passwort-Zurücksetzen | Hoch | Als Benutzer möchte ich mein Passwort per E-Mail zurücksetzen können, wenn ich es vergessen habe. |
| NT-002 | E-Mail-Verifizierung | Hoch | Als Benutzer soll meine E-Mail nach der Registrierung verifiziert werden, um Missbrauch zu verhindern. |
| NT-003 | Profil löschen / Account deaktivieren | Mittel | Als Benutzer möchte ich meinen Account und alle Daten löschen können (DSGVO). |
| NT-004 | Profilbild hochladen | Niedrig | Als Benutzer möchte ich ein Profilbild hochladen können. |

## Epic: Mahlzeiten-Tracking

| Ticket | Titel | Priorität | Beschreibung |
|--------|-------|-----------|--------------|
| NT-010 | Mahlzeit bearbeiten & löschen | Hoch | Als Benutzer möchte ich bereits erfasste Mahlzeiten bearbeiten oder löschen können. |
| NT-011 | Lebensmittel-Datenbank | Hoch | Als Benutzer möchte ich aus einer Datenbank bekannter Lebensmittel auswählen können, statt alle Nährwerte manuell einzugeben. |
| NT-012 | Favoriten / Häufige Mahlzeiten | Mittel | Als Benutzer möchte ich häufig gegessene Mahlzeiten als Favoriten speichern und schnell erneut eintragen können. |
| NT-013 | Barcode-Scanner | Mittel | Als Benutzer möchte ich den Barcode eines Produkts scannen, um Nährwerte automatisch zu laden. |
| NT-014 | Mahlzeiten kopieren | Niedrig | Als Benutzer möchte ich eine Mahlzeit von einem anderen Tag kopieren können. |
| NT-015 | Portionsgrößen-Rechner | Mittel | Als Benutzer möchte ich Portionsgrößen angeben (g, ml, Stück), damit Nährwerte automatisch berechnet werden. |

## Epic: Gewicht & Fortschritt

| Ticket | Titel | Priorität | Beschreibung |
|--------|-------|-----------|--------------|
| NT-020 | Gewichtsverlauf als Diagramm | Hoch | Als Benutzer möchte ich meinen Gewichtsverlauf als Liniendiagramm sehen. |
| NT-021 | Kalorienübersicht als Diagramm | Hoch | Als Benutzer möchte ich meine tägliche Kalorienaufnahme der letzten 7/30 Tage als Balkendiagramm sehen. |
| NT-022 | Makronährstoff-Verteilung (Pie Chart) | Mittel | Als Benutzer möchte ich die Verteilung von Protein, KH und Fett als Kreisdiagramm sehen. |
| NT-023 | Gewichtseintrag bearbeiten & löschen | Mittel | Als Benutzer möchte ich fehlerhafte Gewichtseinträge korrigieren oder löschen können. |
| NT-024 | BMI-Berechnung & Anzeige | Niedrig | Als Benutzer möchte ich meinen aktuellen BMI basierend auf Größe und Gewicht sehen. |
| NT-025 | Wochen-/Monatsbericht | Mittel | Als Benutzer möchte ich einen zusammenfassenden Bericht pro Woche/Monat erhalten (Durchschnitt kcal, Gewichtsentwicklung). |

## Epic: Dashboard & UX

| Ticket | Titel | Priorität | Beschreibung |
|--------|-------|-----------|--------------|
| NT-030 | Fortschrittsbalken Tagesziel | Hoch | Als Benutzer möchte ich auf dem Dashboard einen visuellen Fortschrittsbalken für mein Tagesziel sehen. |
| NT-031 | Responsive Design optimieren | Hoch | Die App soll auf Smartphones vollständig nutzbar sein. |
| NT-032 | Dark Mode | Niedrig | Als Benutzer möchte ich zwischen hellem und dunklem Design wechseln können. |
| NT-033 | Benachrichtigungen / Erinnerungen | Mittel | Als Benutzer möchte ich Erinnerungen erhalten, wenn ich noch keine Mahlzeit eingetragen habe. |
| NT-034 | Mehrsprachigkeit (DE/EN) | Niedrig | Die App soll auf Deutsch und Englisch verfügbar sein. |

## Epic: Fitness & Muskelaufbau

| Ticket | Titel | Priorität | Beschreibung |
|--------|-------|-----------|--------------|
| NT-040 | Trainingseinheiten loggen | Hoch | Als Benutzer möchte ich meine Workouts (Übung, Sätze, Wiederholungen, Gewicht) erfassen können. |
| NT-041 | Kalorienverbrauch durch Training | Mittel | Als Benutzer möchte ich den geschätzten Kalorienverbrauch eines Trainings sehen und vom Tagesziel abziehen. |
| NT-042 | Trainingsvorlagen | Mittel | Als Benutzer möchte ich Trainingsvorlagen erstellen und wiederverwenden können. |
| NT-043 | Fortschritt pro Übung (Diagramm) | Niedrig | Als Benutzer möchte ich sehen, wie sich mein Trainingsgewicht pro Übung über die Zeit entwickelt. |

## Epic: Technische Aufgaben

| Ticket | Titel | Priorität | Beschreibung |
|--------|-------|-----------|--------------|
| NT-050 | Unit Tests schreiben | Hoch | Test-Coverage für Models, Routes und Forms aufbauen (pytest). |
| NT-051 | CI/CD Pipeline einrichten | Hoch | GitHub Actions für Linting, Tests und Deployment konfigurieren. |
| NT-052 | Datenbank-Migrationen (Alembic) | Hoch | Flask-Migrate einrichten, damit Schema-Änderungen versioniert werden. |
| NT-053 | Produktions-Konfiguration | Hoch | SECRET_KEY aus Umgebungsvariable, PostgreSQL statt SQLite, HTTPS erzwingen. |
| NT-054 | Rate Limiting | Mittel | Login- und Registrierungs-Endpoints gegen Brute-Force absichern. |
| NT-055 | API-Endpunkte (REST) | Mittel | REST-API für Mobile-App oder Drittanbieter-Integrationen bereitstellen. |
| NT-056 | Logging & Error Tracking | Mittel | Strukturiertes Logging und Fehler-Tracking (z.B. Sentry) einrichten. |
| NT-057 | Docker-Setup | Niedrig | Dockerfile und docker-compose.yml für einfaches Deployment erstellen. |
| NT-058 | DSGVO-Konformität | Hoch | Datenexport, Löschfunktion, Datenschutzerklärung und Cookie-Hinweis implementieren. |
