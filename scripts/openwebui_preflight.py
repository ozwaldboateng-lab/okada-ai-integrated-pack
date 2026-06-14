from __future__ import annotations

import json
import os
from pathlib import Path

import httpx
import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "examples" / "openwebui" / "pipes_manifest.yaml"
MANUAL_EVAL_PLAN = ROOT / "fixtures" / "e2e" / "openwebui_manual_eval.json"


def load_manifest() -> dict:
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


def load_manual_eval_plan() -> dict:
    return json.loads(MANUAL_EVAL_PLAN.read_text(encoding="utf-8"))


def check_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    component_files = [ROOT / "examples" / "openwebui" / component["file"] for component in manifest.get("components", [])]
    for component_file in component_files:
        if not component_file.exists():
            errors.append(f"missing artifact: {component_file}")
    endpoints = {component.get("endpoint") for component in manifest.get("components", [])}
    expected = {"/integrations/openwebui/pipe", "/integrations/openwebui/filter"}
    if endpoints != expected:
        errors.append(f"unexpected endpoints: {sorted(endpoints)}")
    return errors


def check_manual_eval_plan(plan: dict) -> list[str]:
    errors: list[str] = []
    cases = plan.get("cases", [])
    adapter_types = {case.get("adapter_type") for case in cases}
    if "routing" not in adapter_types:
        errors.append("manual eval plan must include a routing case")
    if "rag" not in adapter_types:
        errors.append("manual eval plan must include a RAG case")
    expected_artifacts = set(plan.get("expected_artifacts", []))
    if "data/audit/audit_records.jsonl" not in expected_artifacts:
        errors.append("manual eval plan must link audit_records.jsonl")
    if "data/benchmarks/e2e_summary.json" not in expected_artifacts:
        errors.append("manual eval plan must link e2e_summary.json")
    for case in cases:
        if not case.get("fixture_id") or not case.get("screen") or not case.get("expected_action"):
            errors.append(f"manual eval case is incomplete: {case.get('case_id', '<missing case_id>')}")
    return errors


def run_gateway_smoke(base_url: str) -> dict:
    pipe_response = httpx.post(
        f"{base_url.rstrip('/')}/integrations/openwebui/pipe",
        json={
            "payload": {
                "chat_id": "owui-preflight",
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Need a careful answer with sources."}],
                "metadata": {"budget_remaining": 0.7, "latency_load_state": 0.2},
            },
            "options": {
                "user": {"id": "operator-preflight"},
                "cheap_model_id": os.getenv("OPENWEBUI_OKADA_CHEAP_MODEL_ID", "gpt-4o-mini"),
                "strong_model_id": os.getenv("OPENWEBUI_OKADA_STRONG_MODEL_ID", "gpt-4.1"),
            },
        },
        timeout=10.0,
    )
    pipe_response.raise_for_status()
    filter_response = httpx.post(
        f"{base_url.rstrip('/')}/integrations/openwebui/filter",
        json={
            "payload": {
                "chat_id": "owui-preflight",
                "messages": [{"role": "user", "content": "Why did the answer change?"}],
                "metadata": {"fallback_rate": 0.2, "override_rate": 0.1},
            },
            "options": {"user": {"id": "operator-preflight"}},
        },
        timeout=10.0,
    )
    filter_response.raise_for_status()
    pipe = pipe_response.json()
    filter_payload = filter_response.json()
    return {
        "pipe_selected_model": pipe.get("transformed_payload", {}).get("selected_model"),
        "pipe_action": pipe.get("transformed_payload", {}).get("metadata", {}).get("okada_action"),
        "filter_action": filter_payload.get("transformed_payload", {}).get("metadata", {}).get("okada_action"),
        "filter_audit_spec": filter_payload.get("audit_payload", {}).get("spec_id"),
    }


def main() -> int:
    base_url = os.getenv("OKADA_BASE_URL", "http://localhost:8080")
    manifest = load_manifest()
    manual_eval_plan = load_manual_eval_plan()
    manifest_errors = check_manifest(manifest)
    manual_eval_errors = check_manual_eval_plan(manual_eval_plan)
    if manifest_errors or manual_eval_errors:
        print(
            json.dumps(
                {"ok": False, "manifest_errors": manifest_errors, "manual_eval_errors": manual_eval_errors},
                indent=2,
            )
        )
        return 1
    try:
        response = httpx.get(f"{base_url}/healthz", timeout=5.0)
        response.raise_for_status()
        smoke = run_gateway_smoke(base_url)
    except Exception as exc:
        print(f"[openwebui_preflight] kernel unreachable: {exc}")
        return 1

    print("[openwebui_preflight] kernel reachable")
    print(f"[openwebui_preflight] base_url={base_url}")
    print(f"[openwebui_preflight] manifest_components={len(manifest.get('components', []))}")
    print(f"[openwebui_preflight] manual_eval_cases={len(manual_eval_plan.get('cases', []))}")
    print(f"[openwebui_preflight] gateway_smoke={json.dumps(smoke, sort_keys=True)}")
    print("[openwebui_preflight] remember Open WebUI Pipe/Filter code runs as trusted Python")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
