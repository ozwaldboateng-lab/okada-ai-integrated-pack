# TASKS.md

This backlog is intended for **either Codex or Claude Code working standalone**.
The same task may be given to both tools independently.

## Good starting tasks
1. Tighten adapter validation for one adapter (`monitoring`, `drift`, `agent`, `rag`, or `routing`).
2. Improve one integration example so it matches current gateway payloads exactly.
3. Add missing audit fields to one runtime integration path.
4. Expand one fixture family and its tests.
5. Improve one runbook based on current code behavior.

## Suggested first task set
- Task A: make `rag` integration payloads stricter and better tested
- Task B: improve `litellm` pre-route decision audit coverage
- Task C: refine `langgraph` human-review contract handling
- Task D: improve `openwebui` filter fail-safe behavior

## How to use this file
- Pick one task.
- Give the same task to Codex and Claude Code if you want side-by-side comparison.
- Compare outputs by eye.
- Keep whichever result you prefer.

## Not the default mode
This file does **not** assume subsystem role division.
