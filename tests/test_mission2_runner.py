from __future__ import annotations
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from hypergen.benchmark_runner import RateLimitedClient, load_models, run, summarize, validate_results, wilson

def test_wilson_bounds():
    assert wilson(0, 0) is None
    assert wilson(0, 10)[0] == 0
    assert wilson(10, 10)[1] == 1
    assert wilson(5, 10)[0] < .5 < wilson(5, 10)[1]

def test_schema_rejects_invalid_and_duplicates():
    with pytest.raises(ValueError):
        validate_results({"schema_version": "1.0", "runs": [{"verdict": "PASS"}]})
    row = {"run_id": "a", "scenario_id": "x", "scenario_version": "1", "model": "m",
           "seed": 0, "tool_trace": [], "expected": {}, "actual": {},
           "evaluator_version": "1", "verdict": "PASS", "latency_ms": 1,
           "errors": [], "security_checks": {}, "timestamp": "2026-01-01"}
    with pytest.raises(ValueError):
        validate_results({"schema_version": "1.0", "runs": [row, row]})

def test_models_yaml(tmp_path: Path):
    p = tmp_path / "models.yaml"
    p.write_text("models:\n  - model-one\n  - 'model-two' # comment\n")
    assert load_models(p) == ["model-one", "model-two"]

def test_429_retries_and_throttle():
    class RateError(Exception):
        status_code = 429
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise RateError()
        return "ok"
    fake = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    clock = [0.0]
    def sleep(n):
        clock[0] += n
    limited = RateLimitedClient(fake, sleep=sleep, clock=lambda: clock[0])
    assert limited.chat.completions.create(model="test") == "ok"
    assert len(calls) == 2
    assert clock[0] >= 1.5

def test_no_result_and_resume(tmp_path: Path, monkeypatch):
    from hypergen import benchmark_runner as runner
    class Broken(Exception):
        status_code = 503
    def create(**kwargs):
        raise Broken()
    fake = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(runner, "SCENARIOS", {"valid_refund": object()})
    first = run(["fake-model"], 1, tmp_path, client=fake, smoke=lambda c,m:(True,"supported"))
    assert len(first["runs"]) == 1
    assert first["runs"][0]["verdict"] == "no_result"
    assert first["runs"][0]["errors"][0]["type"] == "Broken"
    second = run(["fake-model"], 1, tmp_path, client=fake, smoke=lambda c,m:(True,"supported"))
    assert len(second["runs"]) == 1

def test_unsupported_model_is_skipped(tmp_path: Path):
    result = run(["rerank-only"], 1, tmp_path, client=object(),
                 smoke=lambda c,m:(False,"model_did_not_return_required_tool_call"))
    assert result["runs"] == []
    assert result["skipped_models"]["rerank-only"] == "model_did_not_return_required_tool_call"

def test_no_result_not_counted_as_pass():
    row = {"model": "m", "scenario_id": "s", "verdict": "no_result", "security_checks": {}}
    summary = summarize([row], "m", 1)
    assert summary["evaluated"] == 0
    assert summary["passed"] == 0
    assert summary["pass_rate"] is None
    assert summary["no_result_rate"] == 1
