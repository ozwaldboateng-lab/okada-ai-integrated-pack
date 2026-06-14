# コンポーネント責務マッピング

- Document ID: OAI-IMP-002
- Version: 0.3

## 1. コンポーネント一覧
| Component | Primary Responsibility | Input | Output |
|---|---|---|---|
| okada.api | 外部API受付 | HTTP request | normalized response |
| okada.core | 共通特徴量生成と regime 判定 | normalized observables | kernel decision |
| okada.adapters.monitoring | trust window 判定 | monitoring observables | action proposal |
| okada.adapters.drift | drift intervention 判定 | drift observables | action proposal |
| okada.adapters.agent | route contamination 判定 | agent step state | action proposal |
| okada.adapters.rag | retrieval / abstain 判定 | retrieval evidence state | action proposal |
| okada.adapters.routing | route selection 判定 | route candidates | selected route |
| okada.audit | audit record 保存 | decision trace | persisted trace |
| okada.config | config / policy profile 読込 | YAML/ENV | runtime config |
| okada.integrations.dify | Dify 連携 | workflow metadata | okada request |
| okada.integrations.litellm | LiteLLM 連携 | proxy metadata | route / audit call |
| okada.integrations.langgraph | LangGraph 連携 | graph state | governance decision |
| okada.integrations.openwebui | Open WebUI 表示/検索 | audit query | audit read model |

## 2. adapter 共通責務
全 adapter は最低限以下を実装する。
- input validation
- observable normalization
- feature derivation
- regime classification
- action mapping
- audit payload composition

## 3. adapter 非責務
- external model call 実行
- vector DB 実装
- workflow engine 制御本体
- UI rendering

## 4. 依存方向
`api -> core -> adapters -> audit/config`
`integrations -> api or direct service client`
UI/OSS 連携層から adapter への直接 import を避け、必ず service API か service client を通す。

## 5. 実装原則
- ドメイン知識は adapter に置く
- 共通 scoring helper は core に置く
- audit schema は adapter ごとに拡張可だが base schema を壊さない
