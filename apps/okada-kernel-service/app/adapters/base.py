from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.contracts import DiagnoseRequest, PolicyProfile


@dataclass
class AdapterDecision:
    normalized_inputs: dict
    derived_features: dict
    regime: str
    type_class: str
    trust_state: str
    first_visible_handle: list[str]
    recommended_action: str
    alternatives: list[str]


class BaseAdapter(ABC):
    name: str

    @abstractmethod
    def diagnose(self, request: DiagnoseRequest, policy: PolicyProfile) -> AdapterDecision:
        raise NotImplementedError

    def route(self, request: DiagnoseRequest, policy: PolicyProfile) -> AdapterDecision:
        return self.diagnose(request, policy)

    def intervene(self, request: DiagnoseRequest, policy: PolicyProfile) -> AdapterDecision:
        return self.diagnose(request, policy)
