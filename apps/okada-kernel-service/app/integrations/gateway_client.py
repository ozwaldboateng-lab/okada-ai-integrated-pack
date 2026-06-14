from __future__ import annotations

import os
from typing import Any

import httpx


class OkadaGatewayClient:
    """Thin client for integration-gateway endpoints.

    This keeps external examples aligned on a single contract:
    OSS-side glue code calls /integrations/* and lets the gateway build
    canonical kernel requests internally.
    """

    def __init__(
        self,
        base_url: str | None = None,
        *,
        shared_token: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = (base_url or os.getenv('OKADA_BASE_URL', 'http://localhost:8080')).rstrip('/')
        self.shared_token = shared_token or os.getenv('OKADA_SHARED_TOKEN')
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers = {'Content-Type': 'application/json'}
        if self.shared_token:
            headers['Authorization'] = f'Bearer {self.shared_token}'
        return headers

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = httpx.post(
            f'{self.base_url}{path}',
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    async def _apost(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f'{self.base_url}{path}',
                json=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    def litellm_pre_route(self, payload: dict[str, Any], *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._post('/integrations/litellm/pre-route', {'payload': payload, 'options': options or {}})

    async def litellm_pre_route_async(self, payload: dict[str, Any], *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self._apost('/integrations/litellm/pre-route', {'payload': payload, 'options': options or {}})

    def litellm_post_audit(self, payload: dict[str, Any], *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._post('/integrations/litellm/post-audit', {'payload': payload, 'options': options or {}})

    async def litellm_post_audit_async(self, payload: dict[str, Any], *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self._apost('/integrations/litellm/post-audit', {'payload': payload, 'options': options or {}})

    def dify_rag_pre_retrieval(self, payload: dict[str, Any], *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._post('/integrations/dify/rag/pre-retrieval', {'payload': payload, 'options': options or {}})

    def dify_rag_post_retrieval(self, payload: dict[str, Any], *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._post('/integrations/dify/rag/post-retrieval', {'payload': payload, 'options': options or {}})

    def dify_fail_safe(self, payload: dict[str, Any], *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._post('/integrations/dify/fail-safe', {'payload': payload, 'options': options or {}})

    def langgraph_step(self, payload: dict[str, Any], *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._post('/integrations/langgraph/step', {'payload': payload, 'options': options or {}})

    def langgraph_human_review(self, payload: dict[str, Any], *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._post('/integrations/langgraph/human-review', {'payload': payload, 'options': options or {}})

    def openwebui_pipe(self, payload: dict[str, Any], *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._post('/integrations/openwebui/pipe', {'payload': payload, 'options': options or {}})

    def openwebui_filter(self, payload: dict[str, Any], *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._post('/integrations/openwebui/filter', {'payload': payload, 'options': options or {}})
