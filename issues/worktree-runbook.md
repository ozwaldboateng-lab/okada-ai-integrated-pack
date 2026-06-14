# Worktree Runbook

## Branch naming
Use `feature/<TASK-ID>-short-name`.

## Commit style
Prefix commit subject with the task id.
Example: `TASK-LIT-001 wire LiteLLM pre-route callback to gateway`

## Merge rule
One pull request per task. Do not mix tasks unless explicitly marked as a bundled pair.

## Required checks
- run task-specific verification commands
- update issue status
- if behavior changed, update docs and fixtures
