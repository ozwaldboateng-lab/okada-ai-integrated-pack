# 32. LiteLLM Acceptance Matrix

## Acceptance slice A: connectivity
- Kernel `/healthz` is reachable.
- LiteLLM callback can call `/okada/route`.
- LiteLLM callback can ship `/okada/audit`.

## Acceptance slice B: route mutation
- Cheap-path case keeps cheap model.
- Strong-promotion case switches to strong model.
- Metadata includes `okada_regime`, `okada_action`, `okada_strategy`, `okada_audit_trace_id`.
- `examples/litellm/route_matrix.json` demonstrates at least `cheap_route`,
  `bounded_hybrid`, and `promote_strong_model`.

## Acceptance slice C: audit completion
- Successful request produces an audit record.
- Audit record contains action, strategy, target model.

## Acceptance slice D: graceful degradation
- Missing route map path falls back to in-code defaults.
- Audit shipping failure does not break the main response path.

## Smoke command

```bash
python scripts/integration_demo.py
```
