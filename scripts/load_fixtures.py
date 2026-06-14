from __future__ import annotations

import json
from pathlib import Path


def iter_jsonl(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)


def main() -> None:
    fixture_dir = Path(__file__).resolve().parents[1] / "specs" / "okada-ai-spec" / "fixtures"
    for fixture in sorted(fixture_dir.glob("*.jsonl")):
        count = sum(1 for _ in iter_jsonl(fixture))
        print(f"{fixture.name}: {count} records")


if __name__ == "__main__":
    main()
