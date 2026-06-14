Use this repository in dual standalone mode.

Operating assumptions:
- Codex and Claude Code may both receive the same task.
- They work in separate copies of the repo.
- They do not coordinate.
- Human review compares outputs by eye.

For any implementation task:
- keep changes scoped
- follow registry/API/schema before docs/examples
- preserve Okada decomposition visibility
- add or update tests when behavior changes
- avoid unnecessary renames or infrastructure expansion
