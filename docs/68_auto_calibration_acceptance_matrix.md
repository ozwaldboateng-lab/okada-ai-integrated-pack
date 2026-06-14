# Auto-Calibration Acceptance Matrix

| Adapter | Default Mode | Minimum Window | Accept if | Reject if | Rollback if |
|---|---|---:|---|---|---|
| routing | guarded_auto_adopt | 500 requests or 6h | utility up, cost not worse beyond margin | utility down | catastrophic or utility cliff |
| rag | shadow_challenger | 300 grounded cases or 12h | grounded acc up, stale answer down | abstain spike, recall collapse | stale answer spike |
| monitoring | approval_gated | 1d | early detection up, false alert acceptable | unsafe miss up | rollback precision drop |
| drift | approval_gated | 7d | recovery cost efficiency up | false retrain spike | rollback/retrain instability |
| agent | suggest_only | 7d | only advisory by default | any opaque degradation | any catastrophic increase |
