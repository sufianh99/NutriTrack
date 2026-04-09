import os
import sys

import requests

url = os.environ.get("NUTRITRACK_URL", "https://nutritrack.onrender.com")
url = url + "/health"

print("Pruefe " + url + " ...")

try:
    antwort = requests.get(url, timeout=10)
    if antwort.status_code == 200:
        print("Ergebnis: OK")
        sys.exit(0)
    else:
        print("Ergebnis: FEHLER - " + str(antwort.status_code))
        sys.exit(1)
except Exception as fehler:
    print("Ergebnis: FEHLER - " + str(fehler))
    sys.exit(1)
