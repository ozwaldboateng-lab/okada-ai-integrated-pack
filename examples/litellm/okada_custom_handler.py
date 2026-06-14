from __future__ import annotations

import os
from typing import Any, Literal

try:
    from litellm.integrations.custom_logger import CustomLogger
    from litellm.proxy.proxy_server import DualCache, UserAPIKeyAuth
except Exception:  # pragma: no cover - documentation/runtime fallback only
    class CustomLogger:  # type: ignore[override]
        pass

    class DualCache:  # pragma: no cover
        pass

    class UserAPIKeyAuth:  # pragma: no cover
        pass

from app.integrations.gateway_client import OkadaGatewayClient
from app.integrations.litellm_runtime import load_route_map


class OkadaLiteLLMHandler(CustomLogger):
    """LiteLLM custom handler that talks only to the integration gateway."""

    def __init__(self) -> None:
        super().__init__()
        self.gateway = OkadaGatewayClient(
            base_url=os.getenv('OKADA_BASE_URL', 'http://localhost:8080'),
            shared_token=os.getenv('OKADA_SHARED_TOKEN'),
        )
        self.route_map = load_route_map(os.getenv('OKADA_ROUTE_MAP_PATH'))
        self.policy_profile = {
            'profile_name': os.getenv('OKADA_POLICY_PROFILE', 'default'),
            'deterministic_mode': os.getenv('OKADA_DETERMINISTIC_MODE', 'true').lower() == 'true',
        }

    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal[
            'completion',
            'text_completion',
            'embeddings',
            'image_generation',
            'moderation',
            'audio_transcription',
        ],
    ):
        result = await self.gateway.litellm_pre_route_async(
            data,
            options={'policy_profile': self.policy_profile, 'route_map': self.route_map},
        )
        return result.get('transformed_payload', data)

    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response: Any,
    ) -> Any:
        metadata = data.get('metadata', {}) or {}
        if not metadata.get('okada_audit_trace_id'):
            return response
        response_summary = {'status': 'success', 'response_type': type(response).__name__}
        try:
            await self.gateway.litellm_post_audit_async(data, options={'response_summary': response_summary})
        except Exception:
            pass
        return response
