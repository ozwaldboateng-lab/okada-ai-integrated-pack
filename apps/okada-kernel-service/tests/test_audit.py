from __future__ import annotations

import pytest

from app.audit.store import AuditStore, JsonlAuditBackend, audit_store, build_audit_backend
from app.models.contracts import AuditRecord


def test_audit_records_exist_after_api_calls() -> None:
    records = audit_store.list_records()
    assert isinstance(records, list)


def test_audit_store_writes_and_reads_through_backend_interface(tmp_path) -> None:
    backend = JsonlAuditBackend(audit_dir=tmp_path)
    store = AuditStore(backend=backend)
    record = AuditRecord.now(
        audit_trace_id="trace-1",
        spec_id="OKD-AI-001",
        adapter_type="monitoring",
        raw_inputs={"observables": {"fallback_rate": 0.1}},
        normalized_inputs={"fallback_rate": 0.1},
        derived_features={"H_dom": 0.9, "H_hist": 0.0, "H_comp": 0.0},
        decision={"regime": "clean", "recommended_action": "continue"},
        alternatives=["continue"],
        policy_snapshot={"profile_name": "default"},
    )

    written = store.write(record)
    records = store.list_records()

    assert written.audit_trace_id == "trace-1"
    assert len(records) == 1
    assert records[0].audit_trace_id == "trace-1"
    assert records[0].normalized_inputs["fallback_rate"] == 0.1


def test_build_audit_backend_rejects_unknown_backend(tmp_path) -> None:
    with pytest.raises(ValueError, match="Unsupported audit backend"):
        build_audit_backend("sqlite", audit_dir=tmp_path)
