# Scheduler + Champion/Challenger Overview

This pack adds two operating layers on top of auto-calibration.

1. **Scheduler**
   - runs proposal/validation on a cadence
   - can auto-adopt guarded profiles
   - can create shadow candidates for challenger mode

2. **Champion/Challenger**
   - stores challenger candidates
   - evaluates candidates on shadow windows
   - promotes eligible challengers to champion

Safety posture:
- suggestion-only and approval-gated profiles never auto-adopt
- shadow-challenger profiles create candidates first
- guarded-auto-adopt profiles only adopt when validation gates pass
