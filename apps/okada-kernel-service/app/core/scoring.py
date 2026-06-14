from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.models.contracts import PolicyProfile


ADAPTER_DEFAULTS: dict[str, dict[str, float]] = {
    "monitoring": {},
    "mlops": {},
    "agent": {},
    "rag": {
        "grounding_confidence": 1.0,
        "source_freshness": 1.0,
    },
    "routing": {
        "historical_route_success": 1.0,
        "budget_remaining": 1.0,
    },
}


def _to_float(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def flatten_numeric(data: dict[str, Any]) -> dict[str, float]:
    flat: dict[str, float] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            nested = flatten_numeric(value)
            for nkey, nvalue in nested.items():
                flat[f"{key}.{nkey}"] = nvalue
        elif isinstance(value, list):
            if value and all(isinstance(v, (int, float, bool)) for v in value):
                flat[key] = sum(_to_float(v) for v in value) / len(value)
        else:
            flat[key] = _to_float(value)
    return flat


def bounded(value: float, *, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def normalize_numeric_inputs(data: dict[str, Any], *, defaults: dict[str, float] | None = None) -> dict[str, float]:
    normalized = {key: bounded(value) for key, value in flatten_numeric(data).items()}
    for key, value in (defaults or {}).items():
        normalized.setdefault(key, bounded(value))
    return normalized


def normalize_monitoring_observables(data: dict[str, Any]) -> dict[str, float]:
    return normalize_numeric_inputs(data, defaults=ADAPTER_DEFAULTS["monitoring"])


def normalize_drift_observables(data: dict[str, Any]) -> dict[str, float]:
    return normalize_numeric_inputs(data, defaults=ADAPTER_DEFAULTS["mlops"])


def normalize_agent_observables(data: dict[str, Any]) -> dict[str, float]:
    return normalize_numeric_inputs(data, defaults=ADAPTER_DEFAULTS["agent"])


def normalize_rag_observables(data: dict[str, Any]) -> dict[str, float]:
    return normalize_numeric_inputs(data, defaults=ADAPTER_DEFAULTS["rag"])


def normalize_routing_observables(data: dict[str, Any]) -> dict[str, float]:
    return normalize_numeric_inputs(data, defaults=ADAPTER_DEFAULTS["routing"])


ADAPTER_NORMALIZERS = {
    "monitoring": normalize_monitoring_observables,
    "mlops": normalize_drift_observables,
    "agent": normalize_agent_observables,
    "rag": normalize_rag_observables,
    "routing": normalize_routing_observables,
}


def normalize_observables_for_adapter(adapter_type: str, data: dict[str, Any]) -> dict[str, float]:
    try:
        normalizer = ADAPTER_NORMALIZERS[adapter_type]
    except KeyError as exc:
        raise KeyError(f"Unsupported adapter normalizer: {adapter_type}") from exc
    return normalizer(data)


@dataclass(frozen=True)
class ScoreContract:
    h_dom: float
    h_hist: float
    h_comp: float
    r_diag: float
    regime: str

    def as_derived_features(self) -> dict[str, float]:
        return {
            "H_dom": round(self.h_dom, 4),
            "H_hist": round(self.h_hist, 4),
            "H_comp": round(self.h_comp, 4),
            "R_diag": round(self.r_diag, 4),
        }


def build_score_contract(*, h_dom: float, h_hist: float, h_comp: float, policy: PolicyProfile) -> ScoreContract:
    bounded_dom = bounded(h_dom)
    bounded_hist = bounded(h_hist)
    bounded_comp = bounded(h_comp)
    r_diag = (policy.weights["W_hist"] * abs(bounded_hist) + policy.weights["W_comp"] * abs(bounded_comp)) / (
        policy.weights["W_dom"] * abs(bounded_dom) + 1e-6
    )

    if bounded_dom >= 0.65 and r_diag < policy.thresholds["T_clean"]:
        regime = "clean"
    elif bounded_dom >= 0.35 and r_diag < policy.thresholds["T_contam"]:
        regime = "mixed"
    else:
        regime = "contaminated"

    return ScoreContract(
        h_dom=bounded_dom,
        h_hist=bounded_hist,
        h_comp=bounded_comp,
        r_diag=r_diag,
        regime=regime,
    )
