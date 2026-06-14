from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REQUIRED_ENV = [
    "OKADA_BASE_URL",
    "OPENAI_API_BASE",
    "OPENAI_API_KEY",
    "LITELLM_MASTER_KEY",
    "CHEAP_MODEL_NAME",
    "STRONG_MODEL_NAME",
]


def check_env(required_env: list[str] | None = None) -> list[str]:
    return [key for key in (required_env or REQUIRED_ENV) if not os.getenv(key)]


def check_kernel(base_url: str) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}/healthz", timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
            return bool(body.get("status") == "ok"), json.dumps(body)
    except urllib.error.URLError as exc:
        return False, str(exc)


def _load_route_map(path: str | None) -> dict | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def check_route_map(path: str | None) -> tuple[bool, str]:
    if not path:
        return True, "No route map path set; default in-code mapping will be used"
    route_map = Path(path)
    if not route_map.exists():
        return False, f"Route map does not exist: {route_map}"
    try:
        content = json.loads(route_map.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON route map: {exc}"
    return isinstance(content, dict), f"Loaded {len(content) if isinstance(content, dict) else 0} route entries"


def post_json(base_url: str, path: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def run_gateway_smoke(base_url: str, route_map_path: str | None) -> tuple[bool, str]:
    route_map = _load_route_map(route_map_path)
    pre_route_payload = {
        "payload": {
            "model": "cheap-default",
            "messages": [{"role": "user", "content": "preflight routing smoke"}],
            "metadata": {
                "complexity_proxy": 0.95,
                "historical_route_success": 0.35,
                "budget_remaining": 0.7,
                "latency_load_state": 0.2,
                "risk_class": "high",
            },
        },
        "options": {"route_map": route_map} if route_map is not None else {},
    }
    try:
        pre_route = post_json(base_url, "/integrations/litellm/pre-route", pre_route_payload)
        transformed = pre_route.get("transformed_payload") or {}
        if not transformed.get("metadata", {}).get("okada_audit_trace_id"):
            return False, "pre-route response did not include okada_audit_trace_id"
        post_audit = post_json(
            base_url,
            "/integrations/litellm/post-audit",
            {"payload": transformed, "options": {"response_summary": {"status": "preflight"}}},
        )
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return False, str(exc)
    if pre_route.get("integration") != "litellm" or post_audit.get("integration") != "litellm":
        return False, "unexpected integration response"
    return True, f"pre-route action={transformed.get('metadata', {}).get('okada_action')} post-audit=OK"


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight checks for LiteLLM + Okada integration")
    parser.add_argument("--base-url", default=os.getenv("OKADA_BASE_URL", "http://localhost:8080"))
    parser.add_argument("--route-map", default=os.getenv("OKADA_ROUTE_MAP_PATH"))
    args = parser.parse_args()

    missing = check_env()
    if missing:
        print("Missing required environment variables:", ", ".join(missing))
        return 1

    kernel_ok, kernel_msg = check_kernel(args.base_url)
    print(f"Kernel health: {'OK' if kernel_ok else 'FAIL'} :: {kernel_msg}")
    if not kernel_ok:
        return 1

    route_ok, route_msg = check_route_map(args.route_map)
    print(f"Route map: {'OK' if route_ok else 'FAIL'} :: {route_msg}")
    if not route_ok:
        return 1

    smoke_ok, smoke_msg = run_gateway_smoke(args.base_url, args.route_map)
    print(f"Gateway smoke: {'OK' if smoke_ok else 'FAIL'} :: {smoke_msg}")
    if not smoke_ok:
        return 1

    print("Preflight completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
