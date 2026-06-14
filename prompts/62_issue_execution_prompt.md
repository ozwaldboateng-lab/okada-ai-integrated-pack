# Dual-agent issue execution prompt

Use this repository as the source of truth.
Work on exactly one task file from `issues/tasks/`.

## Required behavior
1. Read `AGENTS.md`, `CLAUDE.md`, `TASKS.md`, and the selected issue file.
2. Read only the minimum supporting specs/docs needed for that issue.
3. Make the scoped change.
4. Run the verification commands listed in the issue.
5. Summarize what changed, what is still stubbed, and what should be done next.

## Forbidden behavior
- Do not silently widen scope to adjacent tasks.
- Do not change issue ids or acceptance criteria.
- Do not rewrite source-of-truth registry files unless needed by the task.
