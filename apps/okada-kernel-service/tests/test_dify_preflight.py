from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import dify_preflight  # noqa: E402


def test_dify_gateway_payload_files_are_valid_json() -> None:
    pre_payload = json.loads((REPO_ROOT / "examples" / "dify" / "http_request_payload_pre.json").read_text(encoding="utf-8"))
    post_payload = json.loads((REPO_ROOT / "examples" / "dify" / "http_request_payload_post.json").read_text(encoding="utf-8"))
    fail_safe_payload = json.loads((REPO_ROOT / "examples" / "dify" / "http_request_payload_fail_safe.json").read_text(encoding="utf-8"))

    assert set(pre_payload) == {"payload", "options"}
    assert set(post_payload) == {"payload", "options"}
    assert set(fail_safe_payload) == {"payload", "options"}
    assert "retrieved_chunks" in post_payload["payload"]
    assert fail_safe_payload["options"]["default_action"] == "standard_retrieve"


def test_dify_preflight_reports_missing_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OKADA_BASE_URL", raising=False)

    assert dify_preflight.check_env() == ["OKADA_BASE_URL"]


def test_dify_preflight_renders_dify_placeholders() -> None:
    rendered = dify_preflight.render_template_placeholders(
        {
            "query": "{{#sys.query#}}",
            "chunks": "{{#knowledge.retrieved_chunks#}}",
            "score": "{{#sys.grounding_confidence#}}",
        }
    )

    assert rendered["query"] == "preflight query"
    assert isinstance(rendered["chunks"], list)
    assert rendered["score"] == 0.5
