from __future__ import annotations

import json
from pathlib import Path

from app.benchmark.e2e_compare import DEFAULT_OUTPUT, load_cases, run_case, summarize, write_summary


def test_e2e_cases_exist():
    cases = load_cases()
    assert cases
    assert any(case['spec_id'] == 'OKD-AI-005' for case in cases)
    scenario_ids = {case['scenario_id'] for case in cases}
    assert {
        'routing-ambiguous-mid-cost',
        'rag-stale-low-conflict',
        'agent-clean-linear-plan',
        'agent-derailment-no-human-risk',
    }.issubset(scenario_ids)


def test_e2e_summary_has_positive_gain_for_some_cases():
    results = [run_case(case) for case in load_cases()]
    summary = summarize(results)
    assert summary['total_cases'] >= 4
    assert summary['wins'] >= 2
    assert summary['total_gain'] > 0
    assert summary['fixture_dir']


def test_e2e_summary_writes_reproducible_output(tmp_path: Path):
    results = [run_case(case) for case in load_cases()]
    summary = summarize(results)
    output = tmp_path / 'e2e_summary.json'

    text = write_summary(summary, output, pretty=True)
    loaded = json.loads(output.read_text(encoding='utf-8'))

    assert text.endswith('}')
    assert loaded['total_cases'] == summary['total_cases']
    assert loaded['results'] == summary['results']


def test_e2e_default_output_points_under_data_benchmarks():
    assert DEFAULT_OUTPUT.parts[-3:] == ('data', 'benchmarks', 'e2e_summary.json')


def test_dify_documented_rag_demo_cases_match_expected_outcomes():
    results = {result['scenario_id']: result for result in [run_case(case) for case in load_cases()]}

    assert results['rag-clean-grounded']['regime'] == 'clean'
    assert results['rag-clean-grounded']['okada_action'] == 'no_retrieval'
    assert results['rag-stale-low-conflict']['regime'] == 'contaminated'
    assert results['rag-stale-low-conflict']['okada_action'] == 'abstain'
    assert results['rag-stale-conflict']['regime'] == 'contaminated'
    assert results['rag-stale-conflict']['okada_action'] == 'abstain'


def test_langgraph_agent_fixture_matrix_matches_expected_outcomes():
    results = {result['scenario_id']: result for result in [run_case(case) for case in load_cases()]}

    assert results['agent-clean-linear-plan']['type_class'] == 'I'
    assert results['agent-clean-linear-plan']['regime'] == 'clean'
    assert results['agent-clean-linear-plan']['okada_action'] == 'continue'
    assert results['agent-recoverable-noise']['type_class'] == 'II'
    assert results['agent-recoverable-noise']['okada_action'] == 'continue'
    assert results['agent-derailment-no-human-risk']['type_class'] == 'III'
    assert results['agent-derailment-no-human-risk']['okada_action'] == 'human_handoff'
