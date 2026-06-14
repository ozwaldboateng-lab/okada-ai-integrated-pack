from __future__ import annotations

import json
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "runtime_smoke"


def main() -> None:
    base_url = "http://localhost:8080"
    for name in ["routing_request.json", "agent_request.json"]:
        payload = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
        endpoint = "/okada/route" if payload["adapter_type"] == "routing" else "/okada/intervene"
        response = httpx.post(f"{base_url}{endpoint}", json=payload, timeout=10.0)
        response.raise_for_status()
        print(name, "=>", response.json()["recommended_action"], response.json()["regime"])


if __name__ == "__main__":
    main()
