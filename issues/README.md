# Issue Execution Pack

This directory turns the current specification-and-bootstrap repository into a parallelizable execution plan for Codex and Claude Code.

## Goals
- provide issue-sized work units
- make dependencies explicit
- allow parallel worktree execution
- keep source-of-truth aligned with `specs/` and `apps/okada-kernel-service/`

## Workflow
1. Pick one epic and one ready task.
2. Create a dedicated worktree/branch named after the task id.
3. Complete only the acceptance criteria in that task.
4. Run the listed verification commands.
5. Update `issues/status-board.yaml`.

## Status values
- backlog
- ready
- in_progress
- blocked
- review
- done

## Priority values
- p0
- p1
- p2
- p3
