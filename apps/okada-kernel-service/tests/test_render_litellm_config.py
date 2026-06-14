from __future__ import annotations

import sys
from pathlib import Path

from scripts import render_litellm_config


def test_render_litellm_config_accepts_explicit_route_map(tmp_path: Path, monkeypatch) -> None:
    template = tmp_path / "proxy.template.yaml"
    output = tmp_path / "proxy.yaml"
    route_map = tmp_path / "route_map.json"
    template.write_text("model: ${CHEAP_MODEL_NAME}\nmaster_key: ${LITELLM_MASTER_KEY}\n", encoding="utf-8")
    route_map.write_text('{"cheap_route": {"target_model": "cheap-default"}}\n', encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "replace-me")
    monkeypatch.setenv("LITELLM_MASTER_KEY", "master")
    monkeypatch.setenv("CHEAP_MODEL_NAME", "openai/gpt-4o-mini")
    monkeypatch.setenv("STRONG_MODEL_NAME", "openai/gpt-4.1")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "render_litellm_config.py",
            "--template",
            str(template),
            "--route-map",
            str(route_map),
            "--output",
            str(output),
        ],
    )

    assert render_litellm_config.main() == 0
    assert "openai/gpt-4o-mini" in output.read_text(encoding="utf-8")
    assert Path(render_litellm_config.os.environ["OKADA_ROUTE_MAP_PATH"]) == route_map
