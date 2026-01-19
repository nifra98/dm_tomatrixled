# gti_test_departures.py
import json
import hmac
import hashlib
import base64
import requests
from datetime import datetime
from gti_test import init_session, find_station, USERNAME, PASSWORD, HALTESTELLE

GTI_DEPARTURE_URL = "https://gti.geofox.de/gti/public/departureList"

def generate_signature(body_bytes: bytes, password: str) -> str:
    sig = hmac.new(password.encode("utf-8"), body_bytes, hashlib.sha1).digest()
    return base64.b64encode(sig).decode()


def get_departures(session_id: str, station: dict, max_departures: int = 20):
    """Ruft die nächsten Abfahrten für eine Haltestelle ab (mit vollständigem Station-Objekt)"""
    now = datetime.now()
    body = {
        "version": 63,  # feste Version laut Beispiel
        "station": station,
        "time": {
            "date": now.strftime("%d.%m.%Y"),
            "time": now.strftime("%H:%M")
        },
        "maxList": max_departures,
        "maxTimeOffset": 200,
        "useRealtime": True
    }

    body_bytes = json.dumps(body, separators=(",", ":")).encode("utf-8")
    signature = generate_signature(body_bytes, PASSWORD)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "geofox-auth-type": "HmacSHA1",
        "geofox-auth-user": USERNAME,
        "geofox-auth-signature": signature,
        "geofox-session-id": session_id
    }

    response = requests.post(GTI_DEPARTURE_URL, headers=headers, data=body_bytes)
    response.raise_for_status()
    data = response.json()

    departures = data.get("departures", [])
    if not departures:
        print("Keine Abfahrten gefunden!")
        return []

    print(f"\nNächste {len(departures)} Abfahrten für {station.get('name')} ({station.get('id')}):")
    for d in departures:
        line = d.get("line") or d.get("vehicleType")
        dest = d.get("direction") or d.get("destination")
        planned_time = d.get("plannedDepartureTime") or d.get("time")
        real_time = d.get("realDepartureTime") or ""
        print(f"{planned_time} (real: {real_time}) → {line} Richtung {dest}")

    return departures


if __name__ == "__main__":
    # 1️⃣ Session starten
    session_id = init_session()

    # 2️⃣ Haltestelle suchen
    stations = find_station(session_id, HALTESTELLE)
    if not stations:
        exit("Keine Haltestellen gefunden!")

    station = stations[0]
    print("\nVerwende Station:", station["name"], "ID:", station["id"])

    # 3️⃣ Einmalig Abfahrten abrufen
    get_departures(session_id, station)
