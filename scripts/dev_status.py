from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_FILE = ROOT / "data" / "audit" / "audit_records.jsonl"
BENCH_FILE = ROOT / "data" / "benchmarks" / "e2e_summary.json"


def main() -> None:
    audit_count = 0
    if AUDIT_FILE.exists():
        with AUDIT_FILE.open("r", encoding="utf-8") as handle:
            audit_count = sum(1 for line in handle if line.strip())

    summary: dict[str, object] = {}
    if BENCH_FILE.exists():
        summary = json.loads(BENCH_FILE.read_text(encoding="utf-8"))

    print("Okada AI Dev Status")
    print("====================")
    print(f"Audit records : {audit_count}")
    if summary:
        print(f"Benchmark suite : {summary.get('suite_name', 'unknown')}")
        print(f"Okada wins      : {summary.get('okada_better_cases', 'n/a')}")
        print(f"Baseline wins   : {summary.get('baseline_better_cases', 'n/a')}")
        print(f"Total cases     : {summary.get('total_cases', 'n/a')}")


if __name__ == "__main__":
    main()
