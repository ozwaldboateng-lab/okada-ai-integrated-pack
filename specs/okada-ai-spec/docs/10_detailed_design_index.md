# 詳細設計インデックス

- Document ID: OAI-DD-INDEX-001
- Version: 0.2
- Status: Draft

## 1. 目的
本インデックスは、概要設計から実装可能な詳細設計へ降りる際の参照順を固定する。
本パックでは、**Core と First Wave 5本** を、コード生成AIがそのまま分解できる粒度まで落とす。

## 2. 読む順序
1. `docs/00_overview_design.md`
2. `docs/11_core_detailed_design.md`
3. `docs/12_adapter_monitoring_detailed_design.md`
4. `docs/13_adapter_drift_detailed_design.md`
5. `docs/14_adapter_agent_detailed_design.md`
6. `docs/15_adapter_rag_detailed_design.md`
7. `docs/16_adapter_routing_detailed_design.md`
8. `docs/17_state_machines.md`
9. `docs/18_oss_insertion_points.md`
10. `docs/19_storage_and_audit_model.md`
11. `docs/20_codegen_handoff.md`

## 3. source of truth の優先順位
1. `registry/core/*.yaml` と `registry/adapters/*.yaml`
2. `api/okada-governance.openapi.yaml`
3. `schemas/*.json`
4. `docs/*.md`
5. `fixtures/*.jsonl`

## 4. 実装者向けの約束
- 文言が衝突した場合は YAML を優先する
- API の必須/任意は OpenAPI / JSON Schema を優先する
- 未固定の閾値は `T_*` 識別子のまま実装し、config に逃がす
- 重み `W_*` は hard-code せず policy profile から注入する
- 監査ログは省略しない
