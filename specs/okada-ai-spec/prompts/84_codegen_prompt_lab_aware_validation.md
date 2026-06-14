Implement lab-aware validation for the Okada auto-calibration system.

Requirements:
- extend validation request with optional lab replay controls
- run calibration lab replay inside validation when requested
- include lab summary and report ids in validation response
- let champion/challenger shadow evaluation pass the same flags through validation
- store latest lab suite/report references on candidate state
- add tests for routing validation and rag shadow evaluation with lab replay enabled
