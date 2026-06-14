from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.core.service import kernel_service
from app.models.contracts import DiagnoseRequest

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_FIXTURE_DIR = REPO_ROOT / 'fixtures' / 'e2e'
DEFAULT_OUTPUT = REPO_ROOT / 'data' / 'benchmarks' / 'e2e_summary.json'


def load_cases(fixture_dir: Path | None = None) -> list[dict[str, Any]]:
    resolved_fixture_dir = fixture_dir or DEFAULT_FIXTURE_DIR
    rows: list[dict[str, Any]] = []
    for path in sorted(resolved_fixture_dir.glob('*_cases.jsonl')):
        with path.open('r', encoding='utf-8') as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    req = DiagnoseRequest.model_validate(case['request'])
    mode = case.get('mode', 'diagnose')
    if mode == 'route':
        response = kernel_service.route(req, persist_audit=False)
    elif mode == 'intervene':
        response = kernel_service.intervene(req, persist_audit=False)
    else:
        response = kernel_service.diagnose(req, persist_audit=False)

    okada_action = response.recommended_action
    baseline_action = case['baseline_action']
    score_table = case.get('score_table', {})
    okada_score = float(score_table.get(okada_action, 0.0))
    baseline_score = float(score_table.get(baseline_action, 0.0))
    preferred_actions = set(case.get('preferred_actions', []))

    return {
        'scenario_id': case['scenario_id'],
        'spec_id': case['spec_id'],
        'okada_action': okada_action,
        'baseline_action': baseline_action,
        'okada_score': okada_score,
        'baseline_score': baseline_score,
        'utility_gain': round(okada_score - baseline_score, 4),
        'okada_matches_preferred': okada_action in preferred_actions,
        'baseline_matches_preferred': baseline_action in preferred_actions,
        'regime': response.regime,
        'type_class': response.type_class,
    }


def summarize(results: list[dict[str, Any]], *, fixture_dir: Path | None = None) -> dict[str, Any]:
    total = len(results)
    wins = sum(1 for r in results if r['utility_gain'] > 0)
    ties = sum(1 for r in results if r['utility_gain'] == 0)
    losses = total - wins - ties
    total_gain = round(sum(r['utility_gain'] for r in results), 4)

    by_spec: dict[str, dict[str, Any]] = {}
    for r in results:
        spec = r['spec_id']
        row = by_spec.setdefault(spec, {'count': 0, 'wins': 0, 'total_gain': 0.0})
        row['count'] += 1
        if r['utility_gain'] > 0:
            row['wins'] += 1
        row['total_gain'] = round(row['total_gain'] + r['utility_gain'], 4)

    return {
        'total_cases': total,
        'wins': wins,
        'ties': ties,
        'losses': losses,
        'total_gain': total_gain,
        'fixture_dir': str((fixture_dir or DEFAULT_FIXTURE_DIR).resolve()),
        'by_spec': by_spec,
        'results': results,
    }


def write_summary(summary: dict[str, Any], output: Path, *, pretty: bool = False) -> str:
    text = json.dumps(summary, ensure_ascii=False, indent=2 if pretty else None)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text + ('\n' if not text.endswith('\n') else ''), encoding='utf-8')
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture-dir', type=Path, default=DEFAULT_FIXTURE_DIR)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--no-write', action='store_true')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    fixture_dir = args.fixture_dir.resolve()
    results = [run_case(case) for case in load_cases(fixture_dir)]
    summary = summarize(results, fixture_dir=fixture_dir)

    text = json.dumps(summary, ensure_ascii=False, indent=2 if args.pretty else None)
    print(text)
    if not args.no_write:
        write_summary(summary, args.output, pretty=args.pretty)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
