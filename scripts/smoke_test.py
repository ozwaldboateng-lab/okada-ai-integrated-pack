from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    fixture = Path(__file__).resolve().parents[1] / "specs" / "okada-ai-spec" / "fixtures" / "rag_cases.jsonl"
    first = json.loads(fixture.read_text(encoding="utf-8").splitlines()[0])
    payload = {
        "spec_id": "OKD-AI-004",
        "adapter_type": "rag",
        "observables": first.get("observables", {}),
        "context": first.get("context", {}),
        "history_state": {},
        "resource_state": {},
    }
    client = TestClient(app)
    response = client.post("/okada/diagnose", json=payload)
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()
