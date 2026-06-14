from __future__ import annotations

from app.adapters.agent import AgentAdapter
from app.adapters.base import BaseAdapter
from app.adapters.drift import DriftAdapter
from app.adapters.monitoring import MonitoringAdapter
from app.adapters.rag import RagAdapter
from app.adapters.routing import RoutingAdapter


class AdapterRegistry:
    def __init__(self) -> None:
        self._by_type: dict[str, BaseAdapter] = {
            "monitoring": MonitoringAdapter(),
            "mlops": DriftAdapter(),
            "agent": AgentAdapter(),
            "rag": RagAdapter(),
            "routing": RoutingAdapter(),
        }

    def get(self, adapter_type: str) -> BaseAdapter:
        try:
            return self._by_type[adapter_type]
        except KeyError as exc:
            raise KeyError(f"Unsupported adapter_type: {adapter_type}") from exc


registry = AdapterRegistry()
