"""Provision the Loan Committee agents + demo room on Band.

Registers the 6 peers, creates the shared deal room, adds everyone as
member, and persists credentials to agent_config.yaml (Band shows each
agent api_key only once).

Usage: python3 setup/provision.py
"""

import json
import os
import sys
import urllib.request

BASE = "https://app.band.ai"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AGENTS = [
    ("BankGatekeeper", "KYA/identity triage for RSoft Agentic Bank. Verifies the borrower and recruits the loan committee."),
    ("BankAnalyst", "Credit risk analyst. Publishes credit score, default probability and loan terms to the deal room."),
    ("BankCFO", "Treasury officer. Approves or rejects funding against liquidity and concentration limits."),
    ("BankSettler", "Settlement agent. Disburses USDC on Base Sepolia and posts the tx hash as evidence."),
    ("BankAuditor", "Compliance auditor. Reviews the full deal thread and issues an explainable verdict."),
    ("BorrowerClient1", "Autonomous borrower agent (RSoft client-1). Requests loans and signs terms."),
]


def load_env_key():
    with open(os.path.join(ROOT, ".env")) as f:
        for line in f:
            if line.startswith("BAND_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("BAND_API_KEY not found in .env")


def call(method, path, key, payload=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "X-API-Key": key,
            "Content-Type": "application/json",
            # Cloudflare delante de app.band.ai rechaza el UA default de urllib
            "User-Agent": "curl/8.6.0",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    key = load_env_key()

    existing = {a["name"] for a in call("GET", "/api/v1/me/agents", key)["data"]}
    creds = {}
    for name, desc in AGENTS:
        if name in existing:
            print(f"skip (ya existe): {name}")
            continue
        resp = call("POST", "/api/v1/me/agents/register", key,
                    {"agent": {"name": name, "description": desc}})
        data = resp["data"]
        creds[name] = {
            "agent_id": data["agent"]["id"],
            "api_key": data["credentials"]["api_key"],
        }
        print(f"registrado: {name} -> {data['agent']['id']}")

    if creds:
        # persistir de inmediato: las api_keys no se pueden volver a leer
        cfg_path = os.path.join(ROOT, "agent_config.yaml")
        lines = ["agents:\n"]
        for name, c in creds.items():
            lines += [f"  {name}:\n",
                      f"    agent_id: \"{c['agent_id']}\"\n",
                      f"    api_key: \"{c['api_key']}\"\n"]
        with open(cfg_path, "a") as f:
            f.writelines(lines)
        print(f"credenciales guardadas en {cfg_path}")

    room = call("POST", "/api/v1/me/chats", key, {"chat": {}})
    room_id = room["data"]["id"] if "data" in room else room["id"]
    print(f"sala demo creada: {room_id}")

    all_agents = call("GET", "/api/v1/me/agents", key)["data"]
    for a in all_agents:
        try:
            call("POST", f"/api/v1/me/chats/{room_id}/participants", key,
                 {"participant": {"participant_id": a["id"], "role": "member"}})
            print(f"añadido a sala: {a['name']}")
        except Exception as e:
            print(f"WARN no se pudo añadir {a['name']}: {e}")

    with open(os.path.join(ROOT, ".env"), "a") as f:
        f.write(f"\nDEMO_ROOM_ID={room_id}\n")
    print("DEMO_ROOM_ID añadido a .env")


if __name__ == "__main__":
    main()
