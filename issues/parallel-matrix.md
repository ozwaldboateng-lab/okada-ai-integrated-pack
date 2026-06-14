# Parallel Execution Matrix

## Safe to run in parallel
- TASK-KERNEL-002 policy parameter registry
- TASK-LIT-001 live pre-route hook
- TASK-DIFY-001 pre-retrieval gateway wiring
- TASK-LANG-001 step governance middleware
- TASK-OWUI-001 pipe/filter packaging
- TASK-BENCH-001 benchmark fixture expansion
- TASK-DOC-001 operator walkthrough refresh

## Serial dependencies
- TASK-KERNEL-001 must land before calibration-sensitive runtime tasks are finalized.
- TASK-LIT-002 depends on TASK-LIT-001.
- TASK-DIFY-002 depends on TASK-DIFY-001.
- TASK-LANG-002 depends on TASK-LANG-001.
- TASK-E2E-002 depends on TASK-LIT-001, TASK-DIFY-001, TASK-LANG-001, TASK-OWUI-001.

## Recommended worktree names
- `wt/kernel-policy`
- `wt/litellm-live`
- `wt/dify-rag-live`
- `wt/langgraph-live`
- `wt/openwebui-console`
- `wt/e2e-benchmark`
