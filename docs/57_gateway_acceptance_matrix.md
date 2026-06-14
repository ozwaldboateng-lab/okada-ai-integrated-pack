# Gateway Acceptance Matrix

| Area | Condition | Expected |
|---|---|---|
| LiteLLM | pre-route hook fires | transformed payload returned |
| LiteLLM | post-call success | audit payload posted via gateway |
| Dify | pre-retrieval request | branch variables available |
| Dify | post-retrieval request | branch variables available |
| LangGraph | step governance | mutated state returned |
| LangGraph | human review | merged state returned |
| Open WebUI | pipe | selected model and metadata returned |
| Open WebUI | filter | metadata and audit payload returned |
