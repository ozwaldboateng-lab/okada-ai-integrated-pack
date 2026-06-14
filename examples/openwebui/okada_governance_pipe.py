from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field

from app.integrations.gateway_client import OkadaGatewayClient


class Pipe:
    class Valves(BaseModel):
        NAME_PREFIX: str = Field(default="OKADA/")
        CHEAP_MODEL_ID: str = Field(default="gpt-4o-mini")
        STRONG_MODEL_ID: str = Field(default="gpt-4.1")
        OKADA_BASE_URL: str = Field(default=os.getenv("OKADA_BASE_URL", "http://localhost:8080"))
        OKADA_SHARED_TOKEN: str = Field(default=os.getenv("OKADA_SHARED_TOKEN", ""))

    def __init__(self):
        self.valves = self.Valves()
        self.gateway = OkadaGatewayClient(
            base_url=self.valves.OKADA_BASE_URL,
            shared_token=self.valves.OKADA_SHARED_TOKEN or None,
        )

    def pipes(self):
        return [{"id": "okada.router", "name": f"{self.valves.NAME_PREFIX}router"}]

    async def pipe(self, body: dict, __user__: dict | None = None) -> Any:
        response = self.gateway.openwebui_pipe(
            body,
            options={
                "user": __user__ or {},
                "cheap_model_id": self.valves.CHEAP_MODEL_ID,
                "strong_model_id": self.valves.STRONG_MODEL_ID,
            },
        )
        transformed = response.get("transformed_payload", {})
        metadata = transformed.get("metadata", {})
        return {
            "selected_model": transformed.get("selected_model", self.valves.CHEAP_MODEL_ID),
            "okada_regime": metadata.get("okada_regime"),
            "okada_action": metadata.get("okada_action"),
            "okada_audit_trace_id": metadata.get("okada_audit_trace_id"),
            "okada_type_class": metadata.get("okada_type_class"),
            "okada_alternatives": metadata.get("okada_alternatives", []),
        }
