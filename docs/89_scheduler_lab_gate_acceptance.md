# Scheduler Lab Gate Acceptance

## Routing

- running `routing_guarded_daily` with inline window records executes `routing_replay_smoke`
- scheduler result contains `lab_executed=true`
- scheduler result contains a non-null `lab_report_id`

## RAG

- running `rag_shadow_daily` with inline window records executes `rag_replay_smoke`
- scheduler result contains `action=candidate_created`
- scheduler result contains `lab_executed=true`

## Fallback behavior

- plans without lab configuration continue to use standard validation
