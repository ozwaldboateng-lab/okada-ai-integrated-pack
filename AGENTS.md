# AGENTS.md

This repository is prepared for autonomous or semi-autonomous coding agents.
Use this file as the default implementation contract unless a more specific task file overrides it.

## 1. Project goal
Build the **Okada Governance Kernel** as an external decision service that improves end-to-end AI system performance under fixed model pools, fixed knowledge sources, and fixed budget constraints.

This repository is **not** a new base model project.
It is a governance layer over existing OSS stacks:
- Dify for app/RAG/workflow
- LiteLLM for model gateway/routing
- LangGraph for agent runtime and human handoff
- Open WebUI for operator console and audit-facing workflows

## 2. Source of truth priority
When files disagree, use this order:
1. `specs/okada-ai-spec/registry/**/*.yaml`
2. `api/*.yaml` and `schemas/*.json`
3. `docs/*.md`
4. implementation code under `apps/okada-kernel-service/`
5. examples under `examples/`

Do not silently invent behavior that conflicts with registry YAML.

## 3. Core design constraints
Every implementation must preserve the Okada decomposition:
- `H_dom`: dominant route
- `H_hist`: retained history / load
- `H_comp`: competitor pressure
- `V_first`: first visible handle
- `regime`: `clean | mixed | contaminated`
- optional `type_class`: `I | II | III`

Never reduce the system to a single opaque score without keeping the decomposition visible in audit output.

## 4. What success means
The target claim is not “the model is smarter.”
The target claim is:

> Under the same model pool, same knowledge sources, and same budget constraints,
> the Okada-governed system achieves better end-to-end performance than simpler baselines.

Prefer implementations that improve:
- task success
- groundedness
- stale/contaminated context handling
- catastrophic failure containment
- cost per successful task
- latency under fixed quality

## 5. How this repo should be used by Codex and Claude Code
This repository is intended for **standalone parallel implementation**, not role division.

That means:
- Codex may implement the same task in its own copy of the repo.
- Claude Code may implement the same task in its own copy of the repo.
- They do **not** need to coordinate or share branches.
- Human review compares the outputs and the developer experience by eye.

Do not assume a merge workflow unless explicitly asked.
Do not assume that another agent is handling a different subsystem.

## 6. Recommended task style
Good tasks:
- one adapter behavior
- one gateway behavior
- one acceptance test expansion
- one docs+code consistency repair
- one integration example refinement

Bad tasks:
- “finish the whole platform”
- “make everything production-ready”
- “rewrite the repo structure”

## 7. Editing rules
- Make the smallest coherent change that completes the task.
- Keep public interfaces stable unless the task is explicitly about redesigning them.
- Update docs and fixtures when behavior changes.
- Add or update tests for every meaningful behavior change.
- Prefer explicit dataclasses/models and typed payload builders over ad hoc dict mutation.
- Keep gateway/client code thin; put decision logic in the kernel service.

## 8. Safety / non-goals
Do not:
- claim universal superiority
- hard-code production secrets
- embed API keys in examples
- silently widen scope from governance to general autonomy or alignment claims
- replace domain detectors with vague Okada-only heuristics

## 9. Required checks before handoff
Run as many as are relevant:
```bash
pytest apps/okada-kernel-service/tests -q
python scripts/validate_specs.py
python scripts/e2e_compare.py --pretty
```
If a task changes only docs/prompts and not executable code, say so explicitly.

## 10. Handoff format
When finishing a task, report:
1. what changed
2. which files are source-of-truth affected
3. what tests were run
4. what remains open
