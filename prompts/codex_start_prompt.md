You are working in a standalone copy of the Okada AI repository.
Do not assume another agent is coordinating with you.
Use the repository source-of-truth files in this order:
1. specs/okada-ai-spec/registry/**/*.yaml
2. api/*.yaml and schemas/*.json
3. docs/*.md
4. implementation code
5. examples

Task mode:
- implement the requested task fully in this copy only
- preserve the Okada decomposition fields
- keep interfaces stable unless the task explicitly changes them
- update tests and docs when behavior changes
- report changed files, tests run, and remaining uncertainties
