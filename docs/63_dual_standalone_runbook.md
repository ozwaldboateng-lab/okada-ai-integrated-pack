# Dual Standalone Runbook

## Step 1: prepare two copies
Create two separate working directories.

Example:
```bash
cp -R okada-ai-v1.5-codex-claude-standalone okada-ai-codex
cp -R okada-ai-v1.5-codex-claude-standalone okada-ai-claude
```

## Step 2: give the same task to both tools
Use the same acceptance criteria and the same source-of-truth references.

## Step 3: let each tool work independently
Do not ask them to coordinate.
Do not ask them to split the system by ownership unless you explicitly want that.

## Step 4: run local checks in each copy
```bash
pytest apps/okada-kernel-service/tests -q
python scripts/validate_specs.py
```

## Step 5: compare by eye
Use:
- changed files
- tests added or broken
- interface stability
- overall code clarity
- behavioral fit to the task

## Step 6: keep one result or manually combine
This repository does not require an automatic merge strategy by default.
