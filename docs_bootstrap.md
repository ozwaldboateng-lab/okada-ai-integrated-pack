# Implementation bootstrap note

This repository is intentionally conservative.
It preserves:
- source-of-truth spec pack
- auditable feature decomposition
- deterministic adapter stubs

It does not yet provide:
- calibrated thresholds
- learned policies
- production-grade storage
- full OSS plugins

The expected next step is to let a coding agent read `specs/okada-ai-spec/` and extend the stub adapters.
