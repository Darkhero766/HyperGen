"""Tests for repeatable benchmark aggregation."""
import pytest
from hypergen.benchmark import run_benchmark_batch

def test_batch_runs_each_scenario_for_each_repetition():
    calls = []
    def fake_run(scenario_id, agent_mode):
        calls.append((scenario_id, agent_mode))
        return {"scenario_id": scenario_id, "passed": True, "status": "PASS"}
    report = run_benchmark_batch(["a", "b"], "demo", 3, fake_run)
    assert len(calls) == 6
    assert report["execution_count"] == 6
    assert report["passed"] == 6
    assert report["pass_rate"] == 1.0
    assert report["scenario_summary"]["a"]["executions"] == 3

def test_batch_detects_inconsistent_outcomes():
    count = 0
    def fake_run(scenario_id, agent_mode):
        nonlocal count
        count += 1
        passed = count % 2 == 1
        return {"scenario_id": scenario_id, "passed": passed, "status": "PASS" if passed else "FAIL"}
    report = run_benchmark_batch(["flaky"], "demo", 4, fake_run)
    summary = report["scenario_summary"]["flaky"]
    assert summary["pass_rate"] == 0.5
    assert summary["consistent_outcome"] is False

def test_batch_records_errors_and_continues():
    def fake_run(scenario_id, agent_mode):
        if scenario_id == "broken":
            raise RuntimeError("provider unavailable")
        return {"scenario_id": scenario_id, "passed": True, "status": "PASS"}
    report = run_benchmark_batch(["ok", "broken"], "nvidia_tools", 2, fake_run)
    assert report["execution_count"] == 4
    assert report["failed_or_errors"] == 2
    assert all(x["status"] == "ERROR" for x in report["results"] if x["scenario_id"] == "broken")

@pytest.mark.parametrize("repetitions", [0, -1, 21])
def test_batch_rejects_invalid_repetition_count(repetitions):
    with pytest.raises(ValueError):
        run_benchmark_batch(["case"], "demo", repetitions, lambda *_: {})

def test_batch_rejects_empty_scenario_list():
    with pytest.raises(ValueError):
        run_benchmark_batch([], "demo", 1, lambda *_: {})
