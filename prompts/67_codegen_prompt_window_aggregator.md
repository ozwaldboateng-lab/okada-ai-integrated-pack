Implement the calibration window aggregator already defined in this repository.

Goals:
- preserve the current audit log contract
- map audit records into WindowRecord objects
- support request, time, and request_or_time strategies
- allow profile-derived defaults from `auto_calibration_profiles.yaml`
- expose `POST /okada/auto-calibration/windows/resolve`
- integrate with auto-calibration proposal/validation flow so scheduler jobs can run without inline windows
- keep changes backward compatible with existing tests and integration endpoints

Constraints:
- do not replace the current auto-calibration service
- do not remove manual inline window support
- prefer simple deterministic heuristics over hidden learning logic
- every resolution must write a history entry
