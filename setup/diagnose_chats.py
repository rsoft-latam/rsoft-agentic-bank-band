"""Diagnose the 403 on room creation: print full error bodies."""

import json
import urllib.error
import urllib.request
from provision import BASE, load_env_key


def probe(method, path, key, payload=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"X-API-Key": key, "Content-Type": "application/json",
                 "User-Agent": "curl/8.6.0"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()[:400]
            print(f"{method} {path} -> {r.status}\n  {body}\n")
    except urllib.error.HTTPError as e:
        print(f"{method} {path} -> {e.code}\n  {e.read().decode()[:400]}\n")


if __name__ == "__main__":
    key = load_env_key()
    probe("GET", "/api/v1/me/chats", key)
    probe("POST", "/api/v1/me/chats", key, {"chat": {}})
    probe("POST", "/api/v1/me/chats", key, {"chat": {"name": "loan-demo"}})
    probe("POST", "/api/v1/chats", key, {"chat": {"name": "loan-demo"}})
