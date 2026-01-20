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


def get_departures(session_id: str, station: dict, max_departures: int = 10):
    """
    Liefert Abfahrten als Countdown (GTI-konform)
    """
    now = datetime.now()

    body = {
        "version": 63,
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

    resp = requests.post(GTI_DEPARTURE_URL, headers=headers, data=body_bytes)
    resp.raise_for_status()
    data = resp.json()

    base_time = data.get("time", {})
    departures_raw = data.get("departures", [])

    departures = []

    for d in departures_raw:
        line = d["line"]["name"]
        direction = d["line"]["direction"]
        vehicle = d["line"]["type"]["simpleType"]
        minutes = d.get("timeOffset")

        departures.append({
            "line": line,
            "direction": direction,
            "minutes": minutes,
            "vehicle": vehicle
        })

    return departures


def print_countdown(departures, station_name):
    print(f"\nNächste Abfahrten ab {station_name}:\n")

    for d in departures:
        if d["minutes"] <= 0:
            countdown = "sofort"
        else:
            countdown = f"{d['minutes']} min"

        print(
            f"{d['line']:>4} → {d['direction']:<30} {countdown:>6} [{d['vehicle']}]"
        )


if __name__ == "__main__":
    # 1️⃣ Session
    session_id = init_session()

    # 2️⃣ Station
    stations = find_station(session_id, HALTESTELLE)
    if not stations:
        exit("Keine Haltestelle gefunden")

    station = stations[0]
    print("Verwende Station:", station["name"], station["id"])

    # 3️⃣ Abfahrten (einmalig)
    departures = get_departures(session_id, station)
    print_countdown(departures, station["name"])
