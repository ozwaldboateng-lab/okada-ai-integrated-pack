# Runtime Integration Guide

## Goal
This document explains how to attach the Okada Governance Kernel to existing OSS-based AI stacks without forking their core codebases.

## Design rule
Use extension points first.
Do not fork Dify, LiteLLM, LangGraph, or Open WebUI until the extension-based path is proven insufficient.

## Integration strategy by platform

### Dify
Use:
- HTTP Request node for `/okada/diagnose`
- Code node for response reshaping and branching variables
- Knowledge + workflow as the outer shell for RAG use cases

Why this path:
- Dify's HTTP Request node supports JSON POST and variable substitution from earlier workflow nodes.
- Dify's Code node can transform JSON outputs and expose branch variables.
- This keeps Okada logic outside Dify and lets workflow designers iterate quickly.

### LiteLLM
Use:
- Proxy custom callback handler
- `async_pre_call_hook` to ask the kernel for route decisions
- `async_post_call_success_hook` to emit audit events and collect route outcomes

Why this path:
- LiteLLM proxy hooks can modify incoming requests and outgoing responses.
- This makes LiteLLM the natural choke point for route governance.

### LangGraph
Use:
- node-level governance function before tool execution
- `interrupt()` for human approval or handoff
- durable checkpointing with `thread_id`

Why this path:
- LangGraph interruptions persist state and wait for resume commands, which directly matches Okada governance needs for halt / edit / approve / reject.

### Open WebUI
Use:
- Pipe for route-aware custom model behavior
- Filter for incoming/outgoing monitoring and audit shipping

Why this path:
- Pipes let you create custom "models" with Python logic
- Filters let you inspect and modify inbound/outbound messages

## Shared pattern
Every integration should do the same 5 things:
1. collect observables
2. call the kernel
3. translate the kernel response into platform-native controls
4. persist or forward audit data
5. remain fail-safe when the kernel is unavailable

## Fail-safe rule
If the kernel is down:
- Dify: continue with baseline branch or fallback branch
- LiteLLM: continue with default route or strongest-safe route
- LangGraph: escalate to human or stop high-risk tool calls
- Open WebUI: mark governance unavailable and continue with default behavior only if policy permits
