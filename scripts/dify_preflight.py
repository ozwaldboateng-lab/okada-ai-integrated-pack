from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_PRE = ROOT / "examples" / "dify" / "http_request_payload_pre.json"
PAYLOAD_POST = ROOT / "examples" / "dify" / "http_request_payload_post.json"
REQUIRED_ENV = ["OKADA_BASE_URL"]


def render_template_placeholders(obj):
    if isinstance(obj, dict):
        return {k: render_template_placeholders(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [render_template_placeholders(v) for v in obj]
    if isinstance(obj, str) and "sys.query" in obj:
        return "preflight query"
    if isinstance(obj, str) and "knowledge.retrieved_chunks" in obj:
        return [
            {"source": "preflight-a.md", "chunk_id": 1, "freshness_score": 0.2, "conflict": True},
            {"source": "preflight-b.md", "chunk_id": 2, "freshness_score": 0.9},
        ]
    if isinstance(obj, str) and "{{#" in obj:
        return 0.5
    return obj


def check_env() -> list[str]:
    return [key for key in REQUIRED_ENV if not os.getenv(key)]


def load_payload(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return render_template_placeholders(json.load(fh))


def post_gateway(base_url: str, path: str, payload: dict, headers: dict[str, str]) -> dict:
    response = httpx.post(f"{base_url}{path}", json=payload, headers=headers, timeout=10.0)
    response.raise_for_status()
    return response.json()


def main() -> int:
    missing = check_env()
    if missing:
        print("Missing required environment variables:", ", ".join(missing))
        return 1

    base_url = os.getenv("OKADA_BASE_URL", "http://localhost:8080").rstrip("/")
    token = os.getenv("OKADA_SHARED_TOKEN", "")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        pre_response = post_gateway(base_url, "/integrations/dify/rag/pre-retrieval", load_payload(PAYLOAD_PRE), headers)
        post_response = post_gateway(base_url, "/integrations/dify/rag/post-retrieval", load_payload(PAYLOAD_POST), headers)
        fail_safe_response = post_gateway(
            base_url,
            "/integrations/dify/fail-safe",
            {"payload": {"reason": "preflight"}, "options": {"default_action": "standard_retrieve"}},
            headers,
        )
    except Exception as exc:
        print(f"Dify preflight failed: {exc}")
        return 1

    print("Dify preflight succeeded.")
    print(
        "pre="
        f"{pre_response.get('transformed_payload', {}).get('okada_recommended_action')} "
        "post="
        f"{post_response.get('transformed_payload', {}).get('okada_recommended_action')} "
        "fail_safe="
        f"{fail_safe_response.get('transformed_payload', {}).get('okada_governance_available')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
