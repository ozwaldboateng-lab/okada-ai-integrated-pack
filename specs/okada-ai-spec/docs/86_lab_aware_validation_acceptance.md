# Lab-aware Validation Acceptance

A build is acceptable when:
- validate endpoint accepts lab replay controls
- validation response contains lab fields when replay is enabled
- shadow challenger evaluation can run with lab replay enabled
- candidate state stores latest lab summary references
- tests cover both validation and champion/challenger lab-aware flows
