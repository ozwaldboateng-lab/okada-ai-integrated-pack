from __future__ import annotations

from app.auto_calibration.store import adopted_policy_store
from app.config.policy_registry import policy_parameter_registry
from app.config.settings import settings
from app.models.contracts import PolicyProfile


def resolve_policy(profile: PolicyProfile | None) -> PolicyProfile:
    profile_name = profile.profile_name if profile is not None else settings.default_policy
    thresholds = policy_parameter_registry.defaults_for("threshold")
    weights = policy_parameter_registry.defaults_for("weight")
    preferred_actions: dict[str, list[str]] = {}

    adopted = adopted_policy_store.get(profile_name)
    if adopted:
        thresholds.update(dict(adopted.get("thresholds") or {}))
        weights.update(dict(adopted.get("weights") or {}))
        preferred_actions.update(dict(adopted.get("preferred_actions") or {}))

    thresholds.update(policy_parameter_registry.env_overrides_for("threshold"))
    weights.update(policy_parameter_registry.env_overrides_for("weight"))

    if profile is not None:
        thresholds.update(profile.thresholds)
        weights.update(profile.weights)
        preferred_actions.update(profile.preferred_actions)

    return PolicyProfile(
        profile_name=profile_name,
        deterministic_mode=profile.deterministic_mode if profile is not None else True,
        thresholds=thresholds,
        weights=weights,
        preferred_actions=preferred_actions,
    )
