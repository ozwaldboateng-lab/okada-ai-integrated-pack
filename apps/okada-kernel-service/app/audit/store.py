from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.config.settings import settings
from app.models.contracts import AuditRecord


class AuditBackend(Protocol):
    def write(self, record: AuditRecord) -> AuditRecord:
        ...

    def list_records(self) -> list[AuditRecord]:
        ...


class JsonlAuditBackend:
    def __init__(self, audit_dir: Path | None = None) -> None:
        self.audit_dir = audit_dir or settings.audit_dir
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.audit_dir / "audit_records.jsonl"

    def write(self, record: AuditRecord) -> AuditRecord:
        with self.audit_file.open("a", encoding="utf-8") as fh:
            fh.write(record.model_dump_json())
            fh.write("\n")
        return record

    def list_records(self) -> list[AuditRecord]:
        if not self.audit_file.exists():
            return []
        records: list[AuditRecord] = []
        for line in self.audit_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(AuditRecord.model_validate_json(line))
        return records


def build_audit_backend(backend_name: str | None = None, *, audit_dir: Path | None = None) -> AuditBackend:
    backend = (backend_name or settings.audit_backend).lower()
    if backend == "jsonl":
        return JsonlAuditBackend(audit_dir=audit_dir)
    raise ValueError(f"Unsupported audit backend: {backend}")


class AuditStore:
    def __init__(self, backend: AuditBackend | None = None) -> None:
        self.backend = backend or build_audit_backend()

    def write(self, record: AuditRecord) -> AuditRecord:
        return self.backend.write(record)

    def list_records(self) -> list[AuditRecord]:
        return self.backend.list_records()


audit_store = AuditStore()
