# Dual Standalone Usage

## Purpose
This repository is packaged so that **Codex** and **Claude Code** can each work on the same project independently.

The default mode is:
- same repository contents
- same source of truth
- same task
- separate working copies
- human visual comparison afterward

## Recommended operating model
### Option 1: unzip twice
- `okada-ai-codex/`
- `okada-ai-claude/`

### Option 2: clone twice
- one directory for Codex
- one directory for Claude Code

## What stays identical
- specs
- API contracts
- schema files
- prompts / acceptance criteria
- evaluation scripts

## What stays separate
- edited files
- local environment
- generated code
- test outputs
- agent reasoning and implementation path

## Why this mode is useful
It lets you compare:
- quality of code changes
- speed of execution
- prompt-following fidelity
- debugging behavior
- whether the tool drifts from the source of truth

## What not to over-engineer
You do not need by default:
- branch choreography
- worktree coordination
- merge contracts
- issue assignment by subsystem

Those can be added later, but they are not the baseline operating assumption for this pack.
