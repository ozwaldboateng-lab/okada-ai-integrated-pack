# OKD-AI-003 詳細設計

- Document ID: OAI-DD-003
- Spec ID: OKD-AI-003

## 1. 目的
agent adapter は multi-step agent runtime において、clean route の崩れを早く見つけ、continue / constrained_continue / replan / handoff / abort を決める。

## 2. 呼び出しタイミング
- planner 後
- tool selection 前
- tool result 後
- final answer 前

## 3. 入力観測量
### 必須
- `planner_executor_mismatch`
- `tool_disagreement`
- `retry_count`
- `unresolved_subgoal_count`
- `route_split_frequency`

### 任意
- `retrieval_contradiction_rate`
- `context_age_penalty`
- `tool_failure_severity`
- `high_risk_action_flag`
- `human_confirmation_available`

## 4. feature construction
- `H_dom`: plan adherence + progress continuity
- `H_hist`: stale context + unresolved residue + failed-branch carry-over
- `H_comp`: alternative path pressure + conflicting tool evidence
- `V_first`: earliest contradiction / mismatch / loop symptom
- `route_integrity_score`
- `escalation_pressure_score`

## 5. LangGraph integration
### 推奨ノード配置
- `planner_node`
- `okada_gate_pre_tool`
- `tool_node`
- `okada_gate_post_tool`
- `okada_gate_pre_answer`

### interrupt policy
- `mixed + high_risk_action_flag` -> interrupt_for_human candidate
- `contaminated` -> handoff or abort

## 6. action policy
- clean -> `continue`
- mixed + recoverable -> `constrained_continue`
- mixed + progress collapse -> `replan`
- contaminated + human available -> `human_handoff`
- contaminated + human unavailable + high risk -> `abort`

## 7. tool policy shaping
agent adapter は action だけでなく tool policy を返す。
例:
- disable write-capable tools
- allow read-only tools only
- require intermediate confirmation before irreversible action

## 8. pseudocode
```text
features = derive_agent_features(step_context)
if regime == clean:
    action = continue
elif regime == mixed and features["route_integrity_score"] >= T_recover:
    action = constrained_continue
elif regime == mixed:
    action = replan
else:
    action = human_handoff if context.human_available else abort
```

## 9. 最小ベンチマーク
- clean success
- noisy but recoverable run
- tool loop failure
- contradiction-driven derailment
- high-risk action scenario

## 10. 実装上の注意
- mismatch と disagreement を別物として保持する
- human handoff は単なる failure ではなく policy action として記録する
- retry count は task depth 正規化を行う
