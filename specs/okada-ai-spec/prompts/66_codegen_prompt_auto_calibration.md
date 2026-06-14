You are extending the Okada AI platform with an Auto-Calibration Manager.

Source of truth order:
1. registry/core/okd-ai-core-002-auto-calibration.yaml
2. registry/policies/auto_calibration_profiles.yaml
3. api/okada-auto-calibration.openapi.yaml
4. schemas/*.json
5. docs/66_auto_calibration_overview.md

Implement the following without changing the existing meaning of adapter outputs:
- proposal endpoint skeleton
- replay validation endpoint skeleton
- adoption gate endpoint skeleton
- config publication interface stub
- audit record persistence stub

Constraints:
- do not auto-adopt for agent by default
- keep modes explicit: suggest_only, approval_gated, shadow_challenger, guarded_auto_adopt
- keep thresholds and weights configurable
- preserve deterministic behavior in tests
- expose dry-run first

Deliverables:
- code
- tests
- minimal runbook update
