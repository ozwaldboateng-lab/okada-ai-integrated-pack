from app.auto_calibration.proposal_generators import proposal_generator_service
from app.models.auto_calibration import CalibrationSummary, ProfileCatalogEntry
from app.models.contracts import PolicyProfile


def _entry(adapter_type: str, thresholds: list[str]) -> ProfileCatalogEntry:
    return ProfileCatalogEntry(
        profile_name=f"{adapter_type}_default",
        adapter_type=adapter_type,
        mode="suggest_only",
        mutable_thresholds=thresholds,
        mutable_weights=["W_dom", "W_hist", "W_comp"],
        adoption_gate={},
        rollback_gate={},
        window={},
    )


def _policy() -> PolicyProfile:
    return PolicyProfile(
        profile_name="test",
        thresholds={
            "T_clean": 0.45,
            "T_contam": 0.95,
            "promotion_threshold": 0.60,
            "abstain_threshold": 0.60,
            "freshness_threshold": 0.50,
            "unsafe_threshold": 0.80,
            "retrain_threshold": 0.80,
            "rollback_threshold": 0.80,
            "escalation_threshold": 0.80,
            "handoff_threshold": 0.90,
        },
        weights={"W_dom": 1.0, "W_hist": 1.0, "W_comp": 1.0},
    )


def test_rag_generator_raises_abstain_and_freshness_when_stale_and_conflicted() -> None:
    result = proposal_generator_service.generate(
        profile_name="rag_default",
        adapter_type="rag",
        summary=CalibrationSummary(
            window_size=20,
            rdiag_p40=0.42,
            rdiag_p80=0.88,
            mean_h_dom=0.55,
            mean_h_hist=0.42,
            mean_h_comp=0.38,
            adapter_metrics={
                "freshness_mean": 0.20,
                "grounding_confidence_mean": 0.35,
                "conflict_mean": 0.60,
                "stale_answer_rate": 0.40,
                "re_retrieve_pressure_mean": 0.70,
            },
        ),
        current_policy=_policy(),
        entry=_entry("rag", ["T_clean", "T_contam", "abstain_threshold", "freshness_threshold"]),
        max_delta=0.25,
    )
    assert result.strategy_name == "rag"
    assert result.thresholds["abstain_threshold"] > 0.60
    assert result.thresholds["freshness_threshold"] > 0.50
    assert any("freshness" in note.lower() for note in result.notes)


def test_routing_generator_updates_promotion_threshold_from_pressure() -> None:
    result = proposal_generator_service.generate(
        profile_name="routing_default",
        adapter_type="routing",
        summary=CalibrationSummary(
            window_size=50,
            rdiag_p40=0.30,
            rdiag_p80=0.72,
            mean_h_dom=0.70,
            mean_h_hist=0.20,
            mean_h_comp=0.35,
            adapter_metrics={
                "promotion_pressure_mean": 0.80,
                "budget_tight_rate": 0.70,
                "latency_load_mean": 0.50,
                "complexity_mean": 0.90,
            },
        ),
        current_policy=_policy(),
        entry=_entry("routing", ["T_clean", "T_contam", "promotion_threshold"]),
        max_delta=0.25,
    )
    assert result.strategy_name == "routing"
    assert result.thresholds["promotion_threshold"] != 0.60
    assert result.weights["W_comp"] >= 1.0


def test_agent_generator_raises_handoff_threshold_from_escalation_pressure() -> None:
    result = proposal_generator_service.generate(
        profile_name="agent_default",
        adapter_type="agent",
        summary=CalibrationSummary(
            window_size=30,
            rdiag_p40=0.50,
            rdiag_p80=1.00,
            mean_h_dom=0.40,
            mean_h_hist=0.35,
            mean_h_comp=0.50,
            adapter_metrics={
                "escalation_pressure_mean": 0.90,
                "planner_executor_mismatch_mean": 0.80,
                "retry_mean": 4.0,
                "unresolved_subgoal_mean": 2.0,
            },
        ),
        current_policy=_policy(),
        entry=_entry("agent", ["T_clean", "T_contam", "escalation_threshold", "handoff_threshold"]),
        max_delta=0.25,
    )
    assert result.strategy_name == "agent"
    assert result.thresholds["handoff_threshold"] != 0.90
    assert result.thresholds["escalation_threshold"] != 0.80
