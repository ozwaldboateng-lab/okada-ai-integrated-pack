from __future__ import annotations

from fastapi import APIRouter

from app.core.service import kernel_service
from app.models.contracts import AuditRecord, DiagnoseRequest, DiagnoseResponse

router = APIRouter()


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/okada/diagnose", response_model=DiagnoseResponse)
def diagnose(request: DiagnoseRequest) -> DiagnoseResponse:
    return kernel_service.diagnose(request)


@router.post("/okada/route", response_model=DiagnoseResponse)
def route(request: DiagnoseRequest) -> DiagnoseResponse:
    return kernel_service.route(request)


@router.post("/okada/intervene", response_model=DiagnoseResponse)
def intervene(request: DiagnoseRequest) -> DiagnoseResponse:
    return kernel_service.intervene(request)


@router.post("/okada/audit", response_model=AuditRecord)
def create_audit(record: AuditRecord) -> AuditRecord:
    return kernel_service.create_audit(record)


@router.get("/okada/audit", response_model=list[AuditRecord])
def list_audit() -> list[AuditRecord]:
    return kernel_service.list_audits()
