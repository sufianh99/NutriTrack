"""Monitoring-Skript für die NutriTrack Produktionsumgebung.

Prüft den Health-Endpoint und gibt strukturierte Statusinformationen aus.
Kann manuell oder automatisiert (CI/CD, Cron) ausgeführt werden.

Verwendung:
    # Mit Umgebungsvariable:
    NUTRITRACK_URL=https://nutritrack.onrender.com python scripts/monitor.py

    # Oder direkt mit Default-URL:
    python scripts/monitor.py
"""

import os
import sys
import time

import requests

PROD_URL = os.environ.get("NUTRITRACK_URL", "https://nutritrack.onrender.com")
HEALTH_ENDPOINT = f"{PROD_URL}/health"
TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 5


def check_health() -> dict[str, object]:
    """Prüft den Health-Endpoint und gibt Statusinformationen zurück."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            start = time.time()
            resp = requests.get(HEALTH_ENDPOINT, timeout=TIMEOUT)
            response_time = round((time.time() - start) * 1000)

            return {
                "status": "ok" if resp.status_code == 200 else "error",
                "http_code": resp.status_code,
                "response_time_ms": response_time,
                "body": resp.json() if resp.status_code == 200 else resp.text,
                "attempt": attempt,
            }
        except requests.ConnectionError:
            print(f"  Versuch {attempt}/{MAX_RETRIES}: Verbindung fehlgeschlagen")
        except requests.Timeout:
            print(f"  Versuch {attempt}/{MAX_RETRIES}: Timeout ({TIMEOUT}s)")
        except Exception as exc:
            print(f"  Versuch {attempt}/{MAX_RETRIES}: {exc}")

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    return {"status": "unreachable", "http_code": 0, "response_time_ms": 0, "attempt": MAX_RETRIES}


def main() -> None:
    print(f"NutriTrack Monitoring")
    print(f"URL: {HEALTH_ENDPOINT}")
    print("-" * 40)

    result = check_health()

    if result["status"] == "ok":
        print(f"Status:       OK")
        print(f"HTTP Code:    {result['http_code']}")
        print(f"Antwortzeit:  {result['response_time_ms']} ms")
        print(f"Response:     {result['body']}")
        sys.exit(0)
    elif result["status"] == "unreachable":
        print(f"Status:       NICHT ERREICHBAR")
        print(f"Versuche:     {result['attempt']}/{MAX_RETRIES}")
        print("Die Anwendung antwortet nicht.")
        sys.exit(1)
    else:
        print(f"Status:       FEHLER")
        print(f"HTTP Code:    {result['http_code']}")
        print(f"Antwortzeit:  {result['response_time_ms']} ms")
        sys.exit(1)


if __name__ == "__main__":
    main()
