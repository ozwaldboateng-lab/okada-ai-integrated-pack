# Shared coding-agent contract

You are working inside the Okada AI Kernel repository.

## Objective
Advance the implementation while preserving the specification-driven design.

## Hard constraints
- Source of truth is the YAML registry under `specs/okada-ai-spec/registry/`.
- Preserve the Okada decomposition fields: `H_dom`, `H_hist`, `H_comp`, `V_first`, `regime`.
- Keep OSS-specific glue thin. Business/policy logic should remain in the kernel/gateway layer.
- Do not make sweeping repo-wide rewrites unless explicitly asked.
- Update tests and docs when behavior changes.

## Preferred work style
- Small, reviewable diffs
- Clear file-by-file changes
- Explain assumptions
- Run relevant tests before handoff

## Handoff format
Return:
1. summary of changes
2. files changed
3. tests run
4. open risks / follow-ups
