# Completion Status and Windows Runbook

## Current Completion Estimate

Development tasks are roughly 90-95% complete.

The remaining work is mostly environment and operator validation:
- Git is unavailable in the current Windows environment, so commit/diff review is not complete.
- Docker Compose full-stack startup has static and preflight coverage, but should still be run in the final target environment.
- Dify and Open WebUI imports require manual confirmation inside those external applications.
- The FastAPI/TestClient warning is known and intentionally ignored for this pass.

## Completed Task Areas

| Area | Status | Evidence |
|---|---|---|
| Kernel scoring and adapter normalization | complete | adapter tests and kernel acceptance fixtures |
| Kernel policy registry | complete | env-backed policy resolution tests |
| Audit backend contract | complete | JSONL backend tests and contract doc |
| LiteLLM gateway path | complete | preflight, route matrix, compose/runbook alignment |
| Dify gateway import pack | complete | payload pack, fail-safe behavior, RAG walkthrough |
| LangGraph gateway path | complete | step middleware, resume outcomes, Type I/II/III matrix |
| Open WebUI Pipe/Filter pack | complete | manifest, preflight, manual route-and-audit workflow |
| Integrated compose path | complete for documented path | `ops/integrated/docker-compose.kernel-gateway-ui.yml` |
| E2E benchmark harness | complete | fixture suite and summary writer |
| Operator docs | complete for current scope | start-here flow and platform runbooks |

## Canonical Local Verification

Run from the repository root:

```powershell
Set-Location C:\Users\masaki\Documents\Codex\2026-06-13\md\okada-ai-v2.0-all-in-one
python -m pytest -q
```

Expected current result:

```text
111 passed, 1 warning
```

The warning is:

```text
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated
```

This warning was intentionally ignored.

## Windows PowerShell Quickstart

Install dependencies if needed:

```powershell
Set-Location C:\Users\masaki\Documents\Codex\2026-06-13\md\okada-ai-v2.0-all-in-one
python -m pip install -e .[dev]
```

Start the kernel service:

```powershell
Set-Location C:\Users\masaki\Documents\Codex\2026-06-13\md\okada-ai-v2.0-all-in-one
python -m uvicorn app.main:app --app-dir apps/okada-kernel-service --host 127.0.0.1 --port 8080
```

In a second PowerShell window, run:

```powershell
$env:OKADA_BASE_URL = "http://127.0.0.1:8080"
python scripts/litellm_preflight.py
python scripts/dify_preflight.py
python scripts/langgraph_preflight.py
python scripts/openwebui_preflight.py
python scripts/e2e_compare.py --pretty
python scripts/dev_status.py
```

## Preferred Integrated Stack

The preferred Docker Compose path is:

```powershell
docker compose -f ops/integrated/docker-compose.kernel-gateway-ui.yml --env-file ops/integrated/.env up -d
```

Use `ops/integrated/.env.example` as the source for:
- `OKADA_BASE_URL`
- `OKADA_SHARED_TOKEN`
- `OPENAI_API_KEY`
- `LITELLM_MASTER_KEY`
- `CHEAP_MODEL_NAME`
- `STRONG_MODEL_NAME`
- `OPENWEBUI_OKADA_CHEAP_MODEL_ID`
- `OPENWEBUI_OKADA_STRONG_MODEL_ID`

`docker-compose.yml` is only a local kernel-only shortcut.
`ops/docker-compose.integration.yml` is only a legacy compatibility template.

## Operator Demo Path

Use this order:

1. Read `docs/53_operator_demo_flow.md`.
2. Start the integrated stack or local kernel.
3. Run the gateway preflights.
4. Run `python scripts/e2e_compare.py --pretty`.
5. Review `data/benchmarks/e2e_summary.json`.
6. Review `data/audit/audit_records.jsonl`.

For Open WebUI manual evaluation, use:

```text
docs/61_openwebui_manual_eval_workflow.md
fixtures/e2e/openwebui_manual_eval.json
```

## Useful Files

| Purpose | File |
|---|---|
| Start-here operator flow | `docs/53_operator_demo_flow.md` |
| Integrated runbook | `docs/47_integrated_runbook.md` |
| E2E reporting | `docs/54_e2e_reporting.md` |
| Gateway examples | `docs/55_gateway_unified_examples.md` |
| LiteLLM runbook | `docs/31_litellm_runbook.md` |
| Dify runbook | `docs/35_dify_runbook.md` |
| LangGraph runbook | `docs/39_langgraph_runbook.md` |
| Open WebUI runbook | `docs/43_openwebui_runbook.md` |
| Audit backend contract | `docs/93_audit_backend_contract.md` |

## Remaining Validation Checklist

- Confirm `git` is installed or use another diff/backup workflow before delivery.
- Run the preferred Docker Compose stack on the final machine.
- Import Dify assets into an actual Dify workspace.
- Install Open WebUI Pipe and Filter into an actual Open WebUI instance.
- Confirm model provider keys and model names match the target account.
- Archive `data/benchmarks/e2e_summary.json` and `data/audit/audit_records.jsonl` for handoff evidence.
