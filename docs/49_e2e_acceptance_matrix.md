# E2E Acceptance Matrix

| Area | Check | Minimum condition |
|---|---|---|
| Kernel | Health endpoint | `/healthz` returns `ok` |
| Kernel | API contract | `/okada/diagnose` accepts first-wave request payloads |
| LiteLLM | Preflight | route map and config render without error |
| Open WebUI | Operator surface | pipe/filter files are present and syntactically loadable |
| Dify | Linkage readiness | HTTP payload and Code Node templates are present |
| LangGraph | Linkage readiness | graph example and human review contract are present |
| Harness | Execution | `scripts/e2e_compare.py` completes without error |
| Harness | Output | summary JSON contains totals and per-domain rows |
| Benchmark | Routing evidence | at least one routing scenario shows positive Okada gain |
| Benchmark | RAG evidence | at least one RAG scenario shows positive Okada gain |
