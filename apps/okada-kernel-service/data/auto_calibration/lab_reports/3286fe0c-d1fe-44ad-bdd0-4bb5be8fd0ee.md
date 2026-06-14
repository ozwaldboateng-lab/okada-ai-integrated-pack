# Calibration Lab Report 3286fe0c-d1fe-44ad-bdd0-4bb5be8fd0ee

- profile_name: rag_default
- spec_id: OKD-AI-004
- adapter_type: rag
- suite_name: rag_replay_smoke
- proposal_source: provided_policy

## Summary

- current_total_gain_vs_baseline: 1.05
- proposed_total_gain_vs_baseline: 1.05
- proposed_total_gain_vs_current: 0.0
- current_preferred_match_rate: 1.0
- proposed_preferred_match_rate: 1.0

## Policies

### Current Policy
```json
{
  "profile_name": "rag_default",
  "deterministic_mode": true,
  "thresholds": {
    "T_clean": 0.5854,
    "T_contam": 1.0639,
    "high_risk_bonus": 0.15,
    "abstain_threshold": 0.5463,
    "freshness_threshold": 0.4263
  },
  "weights": {
    "W_dom": 1.7049,
    "W_hist": 1.1537,
    "W_comp": 0.5525
  },
  "preferred_actions": {}
}
```

### Proposed Policy
```json
{
  "profile_name": "rag_default",
  "deterministic_mode": true,
  "thresholds": {
    "T_clean": 0.5854,
    "T_contam": 1.0639,
    "high_risk_bonus": 0.15,
    "abstain_threshold": 0.5463,
    "freshness_threshold": 0.4263
  },
  "weights": {
    "W_dom": 1.7049,
    "W_hist": 1.1537,
    "W_comp": 0.5525
  },
  "preferred_actions": {}
}
```

## Case Results

| scenario_id | baseline_action | current_action | proposed_action | current_gain | proposed_gain | proposed_vs_current |
|---|---|---|---|---:|---:|---:|
| rag-stale-conflict | standard_retrieval | abstain | abstain | 0.6000 | 0.6000 | 0.0000 |
| rag-clean-grounded | deeper_retrieve | no_retrieval | no_retrieval | 0.4500 | 0.4500 | 0.0000 |
