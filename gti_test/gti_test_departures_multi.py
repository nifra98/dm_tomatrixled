# gti_test_departures_multi.py
import os
import json
import hmac
import hashlib
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("GTI_USERNAME")
PASSWORD = os.getenv("GTI_PASSWORD")

GTI_INIT_URL = "https://gti.geofox.de/gti/public/init"
GTI_DEPARTURE_URL = "https://gti.geofox.de/gti/public/departureList"


# -------------------------------------------------
# Auth / Signatur
# -------------------------------------------------
def generate_signature(body_bytes: bytes, password: str) -> str:
    sig = hmac.new(password.encode("utf-8"), body_bytes, hashlib.sha1).digest()
    return base64.b64encode(sig).decode()


# -------------------------------------------------
# Session initialisieren
# -------------------------------------------------
def init_session() -> str:
    body = {}
    body_bytes = json.dumps(body, separators=(",", ":")).encode("utf-8")
    signature = generate_signature(body_bytes, PASSWORD)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "geofox-auth-type": "HmacSHA1",
        "geofox-auth-user": USERNAME,
        "geofox-auth-signature": signature
    }

    r = requests.post(GTI_INIT_URL, headers=headers, data=body_bytes)
    r.raise_for_status()
    session_id = r.json()["id"]
    print("INIT Session-ID:", session_id)
    return session_id


# -------------------------------------------------
# Multi-Station DepartureList
# -------------------------------------------------
def get_departures_multi(session_id: str, stations: list, max_departures: int = 20):
    now = datetime.now()

    body = {
        "version": 63,
        "stations": stations,
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

    r = requests.post(GTI_DEPARTURE_URL, headers=headers, data=body_bytes)
    r.raise_for_status()
    data = r.json()

    # Gruppieren nach Station-ID
    grouped = {}
    for d in data.get("departures", []):
        station_id = d["station"]["id"]
        grouped.setdefault(station_id, []).append(d)

    return grouped


# -------------------------------------------------
# Ausgabe (LED-tauglich)
# -------------------------------------------------
def print_departures(grouped_departures: dict, stations: list):
    print("\nNächste Abfahrten:\n")

    for station in stations:
        sid = station["id"]
        name = station.get("combinedName", station.get("name"))

        print(f"📍 {name}")
        departures = grouped_departures.get(sid, [])

        if not departures:
            print("  keine Abfahrten\n")
            continue

        for d in departures:
            minutes = d.get("timeOffset")
            if minutes <= 0:
                minutes = "sofort"
            else:
                minutes = f"{minutes} min"
            line = d["line"]["name"]
            direction = d["line"]["direction"]
            print(f"  {minutes:>2} → {line} Richtung {direction}")
            #print(f"<{line}>  {direction}  {minutes}")

        print()


# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    session_id = init_session()

    # 👉 HIER deine beiden Haltestellen
    stations = [
        {
            #"name": "Grindelhof",
            "city": "Hamburg",
            "combinedName": "Hamburg, Grindelhof",
            "id": "Master:11035",
            "type": "STATION"
        },
        {
            #"name": "Bezirksamt Eimsbüttel",
            "city": "Hamburg",
            "combinedName": "Hamburg, Bezirksamt Eimsbüttel",
            "id": "Master:11028",
            "type": "STATION"
        }
    ]

    grouped = get_departures_multi(session_id, stations)
    print_departures(grouped, stations)
