from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.core.service import kernel_service
from app.integrations.dify_runtime import (
    build_post_retrieval_payload,
    build_pre_retrieval_payload,
    fail_safe_variables,
    transform_kernel_response,
)
from app.integrations.langgraph_runtime import (
    apply_governance_decision,
    build_agent_governance_payload,
    build_audit_payload as build_langgraph_audit_payload,
    merge_human_review,
)
from app.integrations.litellm_runtime import (
    apply_routing_decision,
    build_audit_payload as build_litellm_audit_payload,
    build_routing_request,
)
from app.integrations.openwebui_runtime import (
    build_filter_audit_payload,
    build_filter_request,
    build_pipe_request,
    transform_filter_decision,
    transform_pipe_decision,
)
from app.models.contracts import DiagnoseRequest
from app.models.gateway_contracts import IntegrationPayload, IntegrationResponse

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/healthz")
def integrations_healthz() -> dict[str, str]:
    return {"status": "ok", "service": "integration-gateway"}


@router.post("/litellm/pre-route", response_model=IntegrationResponse)
def litellm_pre_route(request: IntegrationPayload) -> IntegrationResponse:
    routing_request = build_routing_request(request.payload, policy_profile=request.options.get("policy_profile"))
    decision = kernel_service.route(routing_request)
    mutated = apply_routing_decision(
        request.payload,
        decision.model_dump(),
        route_map=request.options.get("route_map"),
    )
    return IntegrationResponse(
        integration="litellm",
        stage="pre-route",
        kernel_decision=decision.model_dump(),
        transformed_payload=mutated,
        notes=["Model routing decision applied."],
    )


@router.post("/litellm/post-audit", response_model=IntegrationResponse)
def litellm_post_audit(request: IntegrationPayload) -> IntegrationResponse:
    audit_payload = build_litellm_audit_payload(request.payload)
    return IntegrationResponse(
        integration="litellm",
        stage="post-audit",
        audit_payload=audit_payload,
        notes=["Audit payload derived from LiteLLM call state."],
    )


@router.post("/dify/rag/pre-retrieval", response_model=IntegrationResponse)
def dify_pre_retrieval(request: IntegrationPayload) -> IntegrationResponse:
    payload = request.payload
    kernel_request = DiagnoseRequest.model_validate(build_pre_retrieval_payload(
        user_query=payload.get("user_query", ""),
        context=payload.get("context"),
        history_state=payload.get("history_state"),
        resource_state=payload.get("resource_state"),
        policy_profile=request.options.get("policy_profile"),
    ))
    decision = kernel_service.diagnose(kernel_request)
    transformed = transform_kernel_response(decision.model_dump())
    return IntegrationResponse(
        integration="dify",
        stage="rag-pre-retrieval",
        kernel_decision=decision.model_dump(),
        transformed_payload=transformed,
        notes=["Pre-retrieval governance variables generated for Dify."],
    )


@router.post("/dify/rag/post-retrieval", response_model=IntegrationResponse)
def dify_post_retrieval(request: IntegrationPayload) -> IntegrationResponse:
    payload = request.payload
    kernel_request = DiagnoseRequest.model_validate(build_post_retrieval_payload(
        user_query=payload.get("user_query", ""),
        retrieved_chunks=payload.get("retrieved_chunks", []),
        retrieval_metadata=payload.get("retrieval_metadata"),
        context=payload.get("context"),
        history_state=payload.get("history_state"),
        resource_state=payload.get("resource_state"),
        policy_profile=request.options.get("policy_profile"),
    ))
    decision = kernel_service.diagnose(kernel_request)
    transformed = transform_kernel_response(decision.model_dump())
    return IntegrationResponse(
        integration="dify",
        stage="rag-post-retrieval",
        kernel_decision=decision.model_dump(),
        transformed_payload=transformed,
        notes=["Post-retrieval governance variables generated for Dify."],
    )


@router.post("/dify/fail-safe", response_model=IntegrationResponse)
def dify_fail_safe(request: IntegrationPayload) -> IntegrationResponse:
    transformed = fail_safe_variables(
        reason=request.payload.get("reason", "governance_unavailable"),
        default_action=request.options.get("default_action", "standard_retrieve"),
        default_regime=request.options.get("default_regime", "mixed"),
    )
    return IntegrationResponse(
        integration="dify",
        stage="fail-safe",
        transformed_payload=transformed,
        notes=["Generated fail-safe branch variables for Dify."],
    )


@router.post("/langgraph/step", response_model=IntegrationResponse)
def langgraph_step(request: IntegrationPayload) -> IntegrationResponse:
    kernel_request = DiagnoseRequest.model_validate(build_agent_governance_payload(
        state=request.payload,
        stage=request.options.get("stage", request.payload.get("current_step", "runtime_step")),
        policy_profile=request.options.get("policy_profile"),
    ))
    decision = kernel_service.intervene(kernel_request)
    mutated = apply_governance_decision(request.payload, decision.model_dump())
    audit_payload = build_langgraph_audit_payload(mutated)
    return IntegrationResponse(
        integration="langgraph",
        stage="step-governance",
        kernel_decision=decision.model_dump(),
        transformed_payload=mutated,
        audit_payload=audit_payload,
        notes=["Agent state annotated with governance decision."],
    )


@router.post("/langgraph/human-review", response_model=IntegrationResponse)
def langgraph_human_review(request: IntegrationPayload) -> IntegrationResponse:
    state = request.payload.get("state", {})
    review = request.payload.get("human_review", {})
    default_action = request.options.get("default_action", "continue")
    merged = merge_human_review(state, review, default_action=default_action)
    audit_payload = build_langgraph_audit_payload(merged)
    return IntegrationResponse(
        integration="langgraph",
        stage="human-review",
        transformed_payload=merged,
        audit_payload=audit_payload,
        notes=["Human review decision merged into LangGraph state."],
    )


def _strong_model_id(options: dict[str, Any]) -> str:
    return str(options.get("strong_model_id", "strong-default"))


def _cheap_model_id(options: dict[str, Any]) -> str:
    return str(options.get("cheap_model_id", "cheap-default"))


@router.post("/openwebui/pipe", response_model=IntegrationResponse)
def openwebui_pipe(request: IntegrationPayload) -> IntegrationResponse:
    kernel_request = build_pipe_request(
        request.payload,
        user=request.options.get("user"),
        history_state=request.options.get("history_state"),
        resource_state=request.options.get("resource_state"),
        policy_profile=request.options.get("policy_profile"),
    )
    decision = kernel_service.route(kernel_request)
    transformed = transform_pipe_decision(
        request.payload,
        decision.model_dump(),
        cheap_model_id=_cheap_model_id(request.options),
        strong_model_id=_strong_model_id(request.options),
    )
    return IntegrationResponse(
        integration="openwebui",
        stage="pipe",
        kernel_decision=decision.model_dump(),
        transformed_payload=transformed,
        notes=["Open WebUI Pipe decision generated."],
    )


@router.post("/openwebui/filter", response_model=IntegrationResponse)
def openwebui_filter(request: IntegrationPayload) -> IntegrationResponse:
    kernel_request = build_filter_request(
        request.payload,
        user=request.options.get("user"),
        history_state=request.options.get("history_state"),
        resource_state=request.options.get("resource_state"),
        policy_profile=request.options.get("policy_profile"),
    )
    decision = kernel_service.diagnose(kernel_request)
    transformed = transform_filter_decision(request.payload, decision.model_dump())
    audit_payload = build_filter_audit_payload(transformed, response_summary=request.options.get("response_summary"))
    return IntegrationResponse(
        integration="openwebui",
        stage="filter",
        kernel_decision=decision.model_dump(),
        transformed_payload=transformed,
        audit_payload=audit_payload,
        notes=["Open WebUI Filter decision generated."],
    )
