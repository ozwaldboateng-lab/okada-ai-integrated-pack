from __future__ import annotations

import pytest

from app.adapters.registry import registry
from app.core.policy import resolve_policy
from app.core.scoring import normalize_observables_for_adapter
from app.models.contracts import DiagnoseRequest


def make_request(adapter_type: str, spec_id: str, observables: dict | None = None, context: dict | None = None) -> DiagnoseRequest:
    default_observables = {
        "fallback_rate": 0.2,
        "override_rate": 0.1,
        "latency_instability": 0.1,
        "feature_drift_score": 0.3,
        "planner_executor_mismatch": 0.4,
        "tool_disagreement": 0.2,
        "grounding_confidence": 0.5,
        "chunk_conflict_rate": 0.4,
        "complexity_proxy": 0.7,
        "historical_route_success": 0.8,
        "budget_remaining": 0.4,
    }
    return DiagnoseRequest(
        spec_id=spec_id,
        adapter_type=adapter_type,  # type: ignore[arg-type]
        observables=default_observables if observables is None else observables,
        context=context or {},
        history_state={},
        resource_state={},
    )


def test_all_stub_adapters_return_decomposition() -> None:
    cases = [
        ("monitoring", "OKD-AI-001"),
        ("mlops", "OKD-AI-002"),
        ("agent", "OKD-AI-003"),
        ("rag", "OKD-AI-004"),
        ("routing", "OKD-AI-005"),
    ]
    policy = resolve_policy(None)
    for adapter_type, spec_id in cases:
        decision = registry.get(adapter_type).diagnose(make_request(adapter_type, spec_id), policy)
        assert "H_dom" in decision.derived_features
        assert "H_hist" in decision.derived_features
        assert "H_comp" in decision.derived_features
        assert decision.regime in {"clean", "mixed", "contaminated"}


@pytest.mark.parametrize(
    ("adapter_type", "spec_id", "observables", "expected_regime"),
    [
        ("monitoring", "OKD-AI-001", {}, "clean"),
        ("monitoring", "OKD-AI-001", {"fallback_rate": 1.0}, "mixed"),
        ("monitoring", "OKD-AI-001", {"fallback_rate": 1.0, "override_rate": 1.0, "latency_instability": 1.0}, "contaminated"),
        ("mlops", "OKD-AI-002", {}, "clean"),
        ("mlops", "OKD-AI-002", {"feature_drift_score": 1.0}, "mixed"),
        (
            "mlops",
            "OKD-AI-002",
            {"feature_drift_score": 1.0, "uncertainty_drift": 1.0, "performance_decay_proxy": 1.0},
            "contaminated",
        ),
        ("agent", "OKD-AI-003", {}, "clean"),
        ("agent", "OKD-AI-003", {"planner_executor_mismatch": 1.0, "route_split_frequency": 1.0}, "mixed"),
        (
            "agent",
            "OKD-AI-003",
            {"planner_executor_mismatch": 1.0, "route_split_frequency": 1.0, "retry_count": 1.0},
            "contaminated",
        ),
        ("rag", "OKD-AI-004", {}, "clean"),
        ("rag", "OKD-AI-004", {"chunk_conflict_rate": 1.0, "grounding_confidence": 0.55}, "mixed"),
        ("rag", "OKD-AI-004", {"chunk_conflict_rate": 1.0, "grounding_confidence": 0.0}, "contaminated"),
        ("routing", "OKD-AI-005", {}, "clean"),
        ("routing", "OKD-AI-005", {"complexity_proxy": 1.0, "latency_load_state": 1.0}, "mixed"),
        (
            "routing",
            "OKD-AI-005",
            {"complexity_proxy": 1.0, "latency_load_state": 1.0, "retrieval_need_estimate": 1.0, "budget_remaining": 0.0},
            "contaminated",
        ),
    ],
)
def test_adapter_regime_boundaries(adapter_type: str, spec_id: str, observables: dict, expected_regime: str) -> None:
    policy = resolve_policy(None)
    decision = registry.get(adapter_type).diagnose(make_request(adapter_type, spec_id, observables), policy)

    assert decision.regime == expected_regime
    assert all(0.0 <= decision.derived_features[key] <= 1.0 for key in ("H_dom", "H_hist", "H_comp"))
    assert decision.derived_features["R_diag"] >= 0.0


def test_adapter_normalization_clamps_inputs_and_applies_defaults() -> None:
    normalized = normalize_observables_for_adapter(
        "rag",
        {
            "chunk_conflict_rate": 2.0,
            "grounding_confidence": -1.0,
            "nested": {"flag": True, "ratio": 1.5},
        },
    )

    assert normalized["chunk_conflict_rate"] == 1.0
    assert normalized["grounding_confidence"] == 0.0
    assert normalized["source_freshness"] == 1.0
    assert normalized["nested.flag"] == 1.0
    assert normalized["nested.ratio"] == 1.0
