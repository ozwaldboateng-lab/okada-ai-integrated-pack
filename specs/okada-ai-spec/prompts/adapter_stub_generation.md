# Adapter Stub Generation Request

各 adapter について、以下の共通骨格を守って stub を生成してください。

- class name: `{SpecId}Adapter` ではなく意味のある名前にするが、spec_id は class attribute に持つ
- methods:
  - `validate_input(payload)`
  - `normalize(payload)`
  - `derive_features(payload)`
  - `classify(payload)`
  - `map_action(payload)`
  - `build_audit_record(payload, decision)`
- required outputs:
  - `H_dom`
  - `H_hist`
  - `H_comp`
  - `V_first`
  - `regime`
  - `recommended_action`
- TODO は明示する
- 閾値を固定値にせず config lookup にする
