from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field

from app.integrations.gateway_client import OkadaGatewayClient


class Filter:
    class Valves(BaseModel):
        OKADA_BASE_URL: str = Field(default=os.getenv("OKADA_BASE_URL", "http://localhost:8080"))
        OKADA_SHARED_TOKEN: str = Field(default=os.getenv("OKADA_SHARED_TOKEN", ""))

    def __init__(self):
        self.valves = self.Valves()
        self.gateway = OkadaGatewayClient(
            base_url=self.valves.OKADA_BASE_URL,
            shared_token=self.valves.OKADA_SHARED_TOKEN or None,
        )

    async def inlet(self, body: dict, __user__: dict | None = None) -> dict[str, Any]:
        response = self.gateway.openwebui_filter(body, options={"user": __user__ or {}})
        transformed = response.get("transformed_payload", {})
        body.setdefault("metadata", {}).update(transformed.get("metadata", {}))
        body.setdefault("metadata", {})["okada_filter_audit_payload"] = response.get("audit_payload", {})
        return body

    async def outlet(self, body: dict, __user__: dict | None = None) -> dict[str, Any]:
        return body
