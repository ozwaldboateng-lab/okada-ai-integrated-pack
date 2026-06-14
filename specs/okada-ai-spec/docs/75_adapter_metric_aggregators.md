# OKD-AI-CORE-004 Adapter Metric Aggregators

This specification defines a summary layer that turns resolved calibration windows into adapter-shaped replay summaries.

## Common outputs

- mean utility
- success rate
- mean quality
- grounded accuracy
- mean cost
- p95 latency
- abstain rate
- handoff rate
- catastrophic rate

## Adapter outputs

### Routing
- complexity mean
- budget tight rate
- latency load mean
- retrieval need mean
- promotion pressure mean

### RAG
- freshness mean
- grounding confidence mean
- conflict mean
- index age mean
- stale answer rate
- re-retrieve pressure mean

### Monitoring
- fallback rate mean
- override rate mean
- latency instability mean
- output shift mean
- unsafe signal mean

### Drift
- feature drift mean
- uncertainty drift mean
- calibration lag mean
- performance decay mean
- challenger disagreement mean
- retrain pressure mean

### Agent
- planner/executor mismatch mean
- tool disagreement mean
- retry mean
- unresolved subgoal mean
- route split mean
- escalation pressure mean
