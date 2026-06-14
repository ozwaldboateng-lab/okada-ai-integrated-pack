from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal


ParameterKind = Literal["threshold", "weight"]


@dataclass(frozen=True)
class PolicyParameter:
    name: str
    kind: ParameterKind
    default: float
    env_var: str


class PolicyParameterRegistry:
    def __init__(self, parameters: list[PolicyParameter]) -> None:
        self._parameters = {parameter.name: parameter for parameter in parameters}

    def defaults_for(self, kind: ParameterKind) -> dict[str, float]:
        return {name: parameter.default for name, parameter in self._parameters.items() if parameter.kind == kind}

    def env_overrides_for(self, kind: ParameterKind) -> dict[str, float]:
        overrides: dict[str, float] = {}
        for name, parameter in self._parameters.items():
            if parameter.kind != kind:
                continue
            raw_value = os.getenv(parameter.env_var)
            if raw_value is None:
                continue
            overrides[name] = float(raw_value)
        return overrides


policy_parameter_registry = PolicyParameterRegistry(
    [
        PolicyParameter(
            name="T_clean",
            kind="threshold",
            default=0.45,
            env_var="OKADA_POLICY_THRESHOLD_T_CLEAN",
        ),
        PolicyParameter(
            name="T_contam",
            kind="threshold",
            default=0.95,
            env_var="OKADA_POLICY_THRESHOLD_T_CONTAM",
        ),
        PolicyParameter(
            name="high_risk_bonus",
            kind="threshold",
            default=0.15,
            env_var="OKADA_POLICY_THRESHOLD_HIGH_RISK_BONUS",
        ),
        PolicyParameter(
            name="W_dom",
            kind="weight",
            default=1.0,
            env_var="OKADA_POLICY_WEIGHT_W_DOM",
        ),
        PolicyParameter(
            name="W_hist",
            kind="weight",
            default=1.0,
            env_var="OKADA_POLICY_WEIGHT_W_HIST",
        ),
        PolicyParameter(
            name="W_comp",
            kind="weight",
            default=1.0,
            env_var="OKADA_POLICY_WEIGHT_W_COMP",
        ),
    ]
)
