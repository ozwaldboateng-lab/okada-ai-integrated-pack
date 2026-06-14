from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import e2e_stack_preflight  # noqa: E402


def test_e2e_preflight_points_to_preferred_integrated_compose() -> None:
    assert e2e_stack_preflight.PREFERRED_COMPOSE_FILE == Path("ops/integrated/docker-compose.kernel-gateway-ui.yml")


def test_e2e_compose_contract_uses_current_env_names() -> None:
    compose = e2e_stack_preflight.load_compose(REPO_ROOT / e2e_stack_preflight.PREFERRED_COMPOSE_FILE)

    assert e2e_stack_preflight.check_compose_contract(compose) == []
    litellm_env = compose["services"]["litellm-proxy"]["environment"]
    assert "OKADA_BASE_URL" in litellm_env
    assert "OKADA_KERNEL_URL" not in litellm_env
    assert "CHEAP_MODEL_NAME" in litellm_env
    assert "STRONG_MODEL_NAME" in litellm_env


def test_e2e_env_example_contains_required_runtime_keys() -> None:
    env_keys = e2e_stack_preflight.load_env_example(REPO_ROOT / e2e_stack_preflight.PREFERRED_ENV_FILE)

    assert {"OKADA_BASE_URL", "LITELLM_MASTER_KEY", "OPENAI_API_KEY"}.issubset(env_keys)
