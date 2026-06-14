# Adapter Metric Aggregator Acceptance

A summary layer is acceptable when:

- it returns non-empty adapter-specific metrics for supported adapters
- it preserves the original window summary
- proposal responses include adapter metrics in `summary.adapter_metrics`
- the layer does not break existing validation/adoption flows
