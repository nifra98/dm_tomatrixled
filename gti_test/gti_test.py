# gti_test_find_station.py
import os
import json
import hmac
import hashlib
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("GTI_USERNAME")
PASSWORD = os.getenv("GTI_PASSWORD")
HALTESTELLE = os.getenv("HALTESTELLE") or "Grindelhof"

GTI_INIT_URL = "https://gti.geofox.de/gti/public/init"
GTI_CHECKNAME_URL = "https://gti.geofox.de/gti/public/checkName"


def generate_signature(body_bytes: bytes, password: str) -> str:
    sig = hmac.new(password.encode("utf-8"), body_bytes, hashlib.sha1).digest()
    return base64.b64encode(sig).decode()


def init_session():
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
    session_id = r.json().get("id")
    print("INIT Session-ID:", session_id)
    return session_id


def find_station(session_id: str, name: str):
    # Body nach Schema CNRequest
    body = {
        "theName": {
            "name": name,
            "type": "STATION"
        },
        "maxList": 10
    }
    body_bytes = json.dumps(body, separators=(",", ":")).encode("utf-8")
    signature = generate_signature(body_bytes, PASSWORD)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "geofox-auth-type": "HmacSHA1",
        "geofox-auth-user": USERNAME,
        "geofox-auth-signature": signature
    }

    response = requests.post(GTI_CHECKNAME_URL, headers=headers, data=body_bytes)
    print("HTTP-Status:", response.status_code)
    response.raise_for_status()

    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # Haltestellen auslesen
    results = data.get("results") or data.get("stop") or []
    if not results:
        print("Keine Haltestellen gefunden!")
        return []
    else:
        print("Gefundene Stationen:")
        for s in results:
            print(f"ID: {s.get('id')}, Name: {s.get('name')}, Stadt: {s.get('city')}")
    return results


if __name__ == "__main__":
    sid = init_session()
    find_station(sid, HALTESTELLE)
