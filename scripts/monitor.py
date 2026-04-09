import os
import sys
import time

import requests

url = os.environ.get("NUTRITRACK_URL", "https://nutritrack.onrender.com")
url = url + "/health"

versuche = 3
timeout = 30

for i in range(versuche):
    print("Versuch " + str(i + 1) + "/" + str(versuche) + ": Pruefe " + url + " ...")
    try:
        antwort = requests.get(url, timeout=timeout)
        if antwort.status_code == 200:
            print("Ergebnis: OK")
            sys.exit(0)
        else:
            print("Ergebnis: FEHLER - " + str(antwort.status_code))
    except Exception as fehler:
        print("Ergebnis: FEHLER - " + str(fehler))

    if i < versuche - 1:
        print("Warte 15 Sekunden vor erneutem Versuch...")
        time.sleep(15)

print("Alle " + str(versuche) + " Versuche fehlgeschlagen.")
sys.exit(1)
