from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IntegrationPayload(BaseModel):
    payload: dict[str, Any]
    options: dict[str, Any] = Field(default_factory=dict)


class IntegrationResponse(BaseModel):
    ok: bool = True
    integration: str
    stage: str
    kernel_decision: dict[str, Any] = Field(default_factory=dict)
    transformed_payload: dict[str, Any] = Field(default_factory=dict)
    audit_payload: dict[str, Any] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
