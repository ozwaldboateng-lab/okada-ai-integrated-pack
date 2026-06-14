# Okada AI Kernel Service (Integrated Startup Pack)

This repository is the runtime-integration expansion of the bootstrap implementation for the Okada Governance Kernel.

## What is included
- FastAPI service for `/okada/diagnose`, `/okada/route`, `/okada/intervene`, `/okada/audit`, `/healthz`
- Source-of-truth specs under `specs/okada-ai-spec/`
- Adapter stubs for monitoring / drift / agent / rag / routing
- JSONL-backed audit persistence
- Runtime integration examples for:
  - Dify HTTP Request + Code Node
  - LiteLLM Proxy custom pre/post hooks
  - LangGraph interrupt-based agent governance
  - Open WebUI Pipe / Filter style extensions
- Smoke tests and fixture loading script

## Important limitations
This is still not the final calibrated system.
Thresholds and weights remain placeholders.
The goal of this pack is to provide:
- stable interfaces
- executable kernel service
- concrete runtime integration templates
- code-generation-ready handoff material

The kernel now exposes adapter-aware normalization and score contract helpers for
the first-wave adapters. These helpers make boundary behavior deterministic, but
the default thresholds and weights are still calibrated placeholders until
empirical benchmark results are used to tune them.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --app-dir apps/okada-kernel-service --reload --port 8080
```

## Run tests
```bash
pytest apps/okada-kernel-service/tests -q
```

Run first-wave adapter acceptance scenarios:
```bash
pytest apps/okada-kernel-service/tests/test_kernel_acceptance.py -q
```

## Runtime integration quick map
- `examples/dify/`:
  blueprint and payloads for calling the kernel from Dify via HTTP Request node and post-processing via Code node.
- `examples/litellm/`:
  LiteLLM proxy config template, route map, config renderer, preflight checks, and custom callback handler that calls the kernel before/after model execution.
- `examples/langgraph/`:
  interrupt-driven graph example that uses the kernel for continue / replan / handoff / abort decisions.
- `examples/openwebui/`:
  Pipe and Filter examples for routing and audit/governance.

## Repository layout
- `apps/okada-kernel-service/`: service implementation
- `specs/okada-ai-spec/`: source-of-truth specification pack
- `examples/`: runtime integration examples
- `scripts/`: validation and smoke utilities
- `ops/`: deployment and environment examples
- `docs/53_operator_demo_flow.md`: start-here operator walkthrough for the unified gateway demo
- `docs/94_completion_status_and_windows_runbook.md`: completion status, Windows PowerShell commands, and remaining validation checklist
- `docs/95_project_overview_ja.md`: Japanese overview for third-party explanation

## Latest packaged variants
- v0.7 adds Dify-first detailed runtime integration assets.

- v0.8 adds LangGraph-first detailed runtime integration assets.


- v0.9 adds Open WebUI-first detailed runtime integration assets.
- v1.0 adds an integrated startup pack, E2E stack runbook, and the first baseline-vs-Okada benchmark harness.

- v1.1 adds integration-gateway endpoints, local dev quickstart utilities, demo scripts, and integration API tests.


## Dual-agent development support
This repo now includes:
- `AGENTS.md`: shared operating contract for coding agents
- `CLAUDE.md`: Claude Code oriented repo instructions
- `TASKS.md`: current backlog suggestions
- `prompts/`: start prompts for Codex / Claude Code / shared handoff
- `docs/59_dual_agent_handoff.md`: shared handoff guidance
- `docs/60_parallel_worktree_strategy.md`: parallel lane strategy

## Auto-Calibration
This repository now includes bootstrap support for guarded auto-calibration under `/okada/auto-calibration/*`.
Profiles are loaded from `specs/okada-ai-spec/registry/policies/auto_calibration_profiles.yaml`, and adopted profile values can be resolved through `profile_name`.

## Scheduler and Champion/Challenger
- v1.10 adds cadence-driven auto-calibration scheduler plans.
- v1.10 adds shadow challenger candidate preparation, evaluation, and promotion endpoints.


## Recent addition

- Lab-aware validation can replay calibration suites during `/validate` and champion/challenger shadow evaluation.
