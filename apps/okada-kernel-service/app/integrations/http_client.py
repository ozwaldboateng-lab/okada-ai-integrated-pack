from __future__ import annotations

import os
from typing import Any

import httpx

from app.models.contracts import DiagnoseRequest, DiagnoseResponse


class OkadaHttpClient:
    def __init__(
        self,
        base_url: str | None = None,
        *,
        shared_token: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = (base_url or os.getenv("OKADA_BASE_URL", "http://localhost:8080")).rstrip("/")
        self.shared_token = shared_token or os.getenv("OKADA_SHARED_TOKEN")
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.shared_token:
            headers["Authorization"] = f"Bearer {self.shared_token}"
        return headers

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}{path}",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def diagnose(self, request: DiagnoseRequest) -> DiagnoseResponse:
        return DiagnoseResponse.model_validate(self._post("/okada/diagnose", request.model_dump()))

    def route(self, request: DiagnoseRequest) -> DiagnoseResponse:
        return DiagnoseResponse.model_validate(self._post("/okada/route", request.model_dump()))

    def intervene(self, request: DiagnoseRequest) -> DiagnoseResponse:
        return DiagnoseResponse.model_validate(self._post("/okada/intervene", request.model_dump()))
