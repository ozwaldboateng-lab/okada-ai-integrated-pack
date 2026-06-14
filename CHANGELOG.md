## Latest

- v1.15 adds lab-aware validation and champion/challenger replay gating

# Changelog

## v1.11
- added calibration window aggregator for audit-backed replay windows
- added `/okada/auto-calibration/windows/resolve` endpoint
- integrated aggregated window resolution into proposal/validation and scheduler runs
- added window resolution history, docs, registry entry, schemas, and tests

## v1.10
- Added scheduler plan catalog, status tracking, and due-plan execution for auto-calibration.
- Added champion/challenger candidate preparation, shadow evaluation, and promotion APIs.
- Added scheduler/challenger stores, docs, and tests.


## v1.3
- Added shared dual-agent handoff files: `AGENTS.md`, `CLAUDE.md`, `TASKS.md`
- Added shared/Codex/Claude bootstrap prompts under `prompts/`
- Added dual-agent handoff and parallel worktree strategy docs
- Prepared repository for either Codex-style or Claude Code-style continuation

# Changelog

## v1.1.0
- Added integration-gateway endpoints for LiteLLM, Dify, LangGraph, and Open WebUI
- Added local development Makefile, demo script, and status utility
- Added integration API tests
- Added local dev quickstart and operator demo docs

- Added Open WebUI detailed integration package with runtime helpers, Pipe/Filter examples, runbook, acceptance matrix, preflight script, and tests.

## v0.7.0
- added Dify detailed integration docs, runbook, acceptance matrix, and codegen prompt
- added Dify runtime helper module and tests
- added pre/post HTTP payload templates and code-node snippets
- added Dify preflight script and env example

# Changelog

## v0.6.0
- Added LiteLLM-focused runtime helpers for routing payload build, route mutation, and audit payload generation
- Added render_litellm_config.py and litellm_preflight.py
- Added deployable LiteLLM compose template and env example under ops/litellm/
- Added route_map.json and config template for callback-driven routing
- Added LiteLLM detailed design, runbook, acceptance matrix, and codegen prompt
- Added tests for LiteLLM runtime helpers

## v0.5.0
- Added runtime integration guide and acceptance test plan
- Added kernel Dockerfile and integration compose template
- Added Dify HTTP Request + Code node example pack
- Added LiteLLM proxy config and custom callback handler example
- Added LangGraph interrupt-based agent governance example
- Added Open WebUI Pipe and Filter examples
- Added runtime smoke fixtures and script
- Added auth-aware HTTP client and one extra test
## v1.9
- Integrated Auto-Calibration Manager into the kernel service.
- Added proposal/validate/adopt endpoints, adopted policy persistence, and routing-focused tests.

## v1.13
- Added adapter-specific auto-calibration proposal generators for routing, rag, monitoring, drift, and agent.
- Integrated proposal generation into auto-calibration propose() with strategy notes.
- Added proposal generator docs, registry entry, and tests.

## v1.14 - calibration lab replay
- added calibration lab replay service for current vs proposed policy comparison on fixture suites
- added lab APIs, fixture suite manifest, markdown report persistence, and report history
- added calibration lab tests and CLI helper
