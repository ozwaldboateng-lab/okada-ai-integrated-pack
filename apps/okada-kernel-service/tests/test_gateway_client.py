from __future__ import annotations

import httpx
import pytest

from app.integrations.gateway_client import OkadaGatewayClient


class DummyResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def test_gateway_client_posts_to_litellm_pre_route(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    def fake_post(url: str, json: dict, headers: dict, timeout: float):
        captured['url'] = url
        captured['json'] = json
        return DummyResponse({'integration': 'litellm', 'transformed_payload': {'model': 'strong-default'}})

    monkeypatch.setattr(httpx, 'post', fake_post)
    client = OkadaGatewayClient(base_url='http://localhost:8080', shared_token='x')
    result = client.litellm_pre_route({'model': 'cheap-default'}, options={'route_map': {}})

    assert captured['url'].endswith('/integrations/litellm/pre-route')
    assert captured['json']['payload']['model'] == 'cheap-default'
    assert result['transformed_payload']['model'] == 'strong-default'


@pytest.mark.asyncio
async def test_gateway_client_async_posts_to_post_audit(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    class DummyAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url: str, json: dict, headers: dict):
            captured['url'] = url
            captured['json'] = json
            return DummyResponse({'integration': 'litellm', 'audit_payload': {'spec_id': 'OKD-AI-005'}})

    monkeypatch.setattr(httpx, 'AsyncClient', DummyAsyncClient)
    client = OkadaGatewayClient(base_url='http://localhost:8080')
    result = await client.litellm_post_audit_async({'metadata': {'okada_audit_trace_id': 'a-1'}}, options={})

    assert captured['url'].endswith('/integrations/litellm/post-audit')
    assert result['audit_payload']['spec_id'] == 'OKD-AI-005'
