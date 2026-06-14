from __future__ import annotations

from app.integrations.http_client import OkadaHttpClient


def test_http_client_headers_include_token(monkeypatch):
    monkeypatch.setenv("OKADA_SHARED_TOKEN", "test-token")
    client = OkadaHttpClient(base_url="http://example.com")
    headers = client._headers()
    assert headers["Authorization"] == "Bearer test-token"
    assert headers["Content-Type"] == "application/json"
