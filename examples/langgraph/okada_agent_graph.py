from __future__ import annotations

import os

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app.integrations.gateway_client import OkadaGatewayClient
from state_schema import AgentState


GATEWAY = OkadaGatewayClient(
    base_url=os.getenv("OKADA_BASE_URL", "http://localhost:8080"),
    shared_token=os.getenv("OKADA_SHARED_TOKEN"),
)


def plan_node(state: AgentState) -> AgentState:
    state["current_step"] = "plan"
    state["plan"] = f"Search internal knowledge and answer: {state['user_request']}"
    state["tool_name"] = "search_docs"
    state["tool_input"] = state["user_request"]
    return state


def governance_node(stage: str):
    def _node(state: AgentState) -> AgentState:
        state["current_step"] = stage
        response = GATEWAY.langgraph_step(state, options={"stage": stage})
        mutated = response.get("transformed_payload", state)
        if mutated.get("requires_interrupt"):
            review = interrupt(
                {
                    "message": "Okada governance requested review",
                    "recommended_action": mutated.get("governance_action", "continue"),
                    "regime": mutated.get("governance_regime", "mixed"),
                    "audit_trace_id": mutated.get("audit_trace_id", ""),
                    "plan": mutated.get("plan", ""),
                    "tool_name": mutated.get("tool_name", ""),
                    "thread_id": mutated.get("thread_id", ""),
                    "checkpoint_id": mutated.get("checkpoint_id", ""),
                    "run_id": mutated.get("run_id", ""),
                }
            )
            merged = GATEWAY.langgraph_human_review(
                {"state": mutated, "human_review": review},
                options={"default_action": mutated.get("governance_action", "continue")},
            )
            mutated = merged.get("transformed_payload", mutated)
        return mutated

    return _node


def tool_node(state: AgentState) -> AgentState:
    state["current_step"] = "tool"
    state["tool_output"] = f"tool({state['tool_name']}) => result for {state['tool_input']}"
    return state


def replan_node(state: AgentState) -> AgentState:
    state["current_step"] = "replan"
    state["plan"] = f"Replanned: summarize first, then answer {state['user_request']}"
    state["tool_name"] = "summarize_context"
    state["tool_input"] = state["user_request"]
    return state


def final_node(state: AgentState) -> AgentState:
    state["current_step"] = "final"
    if state.get("governance_action") == "abort":
        state["final_answer"] = "Aborted due to Okada governance."
    else:
        state["final_answer"] = f"{state.get('plan', '')} | {state.get('tool_output', '')}"
    return state


def route_after_governance(state: AgentState) -> str:
    action = state.get("governance_action", "continue")
    if action == "abort":
        return "final"
    if action == "replan":
        return "replan"
    return "tool"


def route_after_post_tool(state: AgentState) -> str:
    action = state.get("governance_action", "continue")
    if action == "abort":
        return "final"
    if action == "replan":
        return "replan"
    return "final"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan_node)
    graph.add_node("governance_before_tool", governance_node("before_tool"))
    graph.add_node("tool", tool_node)
    graph.add_node("governance_after_tool", governance_node("after_tool"))
    graph.add_node("replan", replan_node)
    graph.add_node("final", final_node)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "governance_before_tool")
    graph.add_conditional_edges("governance_before_tool", route_after_governance, {"tool": "tool", "replan": "replan", "final": "final"})
    graph.add_edge("replan", "tool")
    graph.add_edge("tool", "governance_after_tool")
    graph.add_conditional_edges("governance_after_tool", route_after_post_tool, {"replan": "replan", "final": "final"})
    graph.add_edge("final", END)
    return graph.compile(checkpointer=MemorySaver())
