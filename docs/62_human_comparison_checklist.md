# Human Comparison Checklist

Use this checklist when comparing Codex and Claude Code results by eye.

## 1. Did it solve the asked task?
- fully
- partially
- mostly unrelated

## 2. Did it stay faithful to the source of truth?
Check alignment with:
- registry YAML
- OpenAPI / schemas
- adapter semantics
- audit requirements

## 3. How clean is the code?
- file locality
- interface clarity
- overengineering level
- unnecessary renames
- test readability

## 4. How safe is the change?
- preserves decomposition fields
- does not break public contracts casually
- includes fail-safe behavior
- keeps secrets out of code/examples

## 5. How useful is the output beyond the code?
- docs updated
- tests added
- reasoning visible in audit/log paths
- runbook impact understood

## 6. How did the tool behave?
- followed the prompt well
- stayed in scope
- recovered from ambiguity well
- produced a practical implementation path

## 7. Final human decision
- keep Codex result
- keep Claude Code result
- hybridize manually
- reject both and rerun
