"""Shared helpers: env loading, agent credentials, bank API client."""

import json
import os
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env():
    """Minimal .env loader (no python-dotenv dependency)."""
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k, v)


def load_credentials(agent_name: str) -> tuple[str, str]:
    """Read agent_id/api_key for one peer from agent_config.yaml."""
    path = os.path.join(ROOT, "agent_config.yaml")
    agent_id = api_key = None
    current = None
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.endswith(":") and not stripped.startswith(("agent_id", "api_key")):
                current = stripped[:-1]
            elif current == agent_name and stripped.startswith("agent_id:"):
                agent_id = stripped.split(":", 1)[1].strip().strip('"')
            elif current == agent_name and stripped.startswith("api_key:"):
                api_key = stripped.split(":", 1)[1].strip().strip('"')
    if not agent_id or not api_key:
        raise SystemExit(f"credenciales de {agent_name} no encontradas en agent_config.yaml")
    return agent_id, api_key


def bank_call(method: str, path: str, payload: dict | None = None, api_prefix: bool = True) -> dict:
    """Call the RSoft Agentic Bank backend. Requires BANK_API_URL in .env.

    api_prefix=False targets root-level endpoints (/stats, /health) that
    live outside /api/v1.
    """
    base = os.environ.get("BANK_API_URL", "").rstrip("/")
    if not base:
        return {"error": "BANK_API_URL not configured — running in standalone demo mode"}
    if not api_prefix and base.endswith("/api/v1"):
        base = base[: -len("/api/v1")]
    headers = {"Content-Type": "application/json"}
    if os.environ.get("BANK_BACKEND_API_KEY"):
        headers["X-API-Key"] = os.environ["BANK_BACKEND_API_KEY"]
    req = urllib.request.Request(
        base + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except Exception as e:  # surface errors to the LLM as data, not crashes
        return {"error": str(e)}
