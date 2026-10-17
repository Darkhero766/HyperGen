"""Repeatable benchmark execution and aggregate reliability metrics."""
from __future__ import annotations
from collections import defaultdict
from typing import Any, Callable

def run_benchmark_batch(scenario_ids: list[str], agent_mode: str, repetitions: int, run_one: Callable[[str, str], dict[str, Any]], scenario_titles: dict[str, str] | None = None) -> dict[str, Any]:
    """Run scenarios repeatedly; repetitions are executions, not independent cases."""
    if repetitions < 1 or repetitions > 20:
        raise ValueError("repetitions must be between 1 and 20")
    if not scenario_ids:
        raise ValueError("select at least one scenario")
    titles = scenario_titles or {}
    results: list[dict[str, Any]] = []
    for repetition in range(1, repetitions + 1):
        for scenario_id in scenario_ids:
            try:
                item = dict(run_one(scenario_id, agent_mode))
            except Exception as exc:
                item = {"scenario_id": scenario_id, "scenario_title": titles.get(scenario_id, scenario_id), "status": "ERROR", "passed": False, "summary": f"{type(exc).__name__}: {exc}", "events": [], "expected": {}, "actual": {}, "agent_mode": agent_mode}
            item["repetition"] = repetition
            results.append(item)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in results:
        grouped[str(item["scenario_id"])].append(item)
    summary = {}
    for scenario_id, items in grouped.items():
        passes = sum(bool(item.get("passed")) for item in items)
        summary[scenario_id] = {"scenario_title": titles.get(scenario_id, items[0].get("scenario_title", scenario_id)), "executions": len(items), "passes": passes, "failures_or_errors": len(items) - passes, "pass_rate": passes / len(items), "consistent_outcome": passes in (0, len(items))}
    passed = sum(bool(item.get("passed")) for item in results)
    return {"agent_mode": agent_mode, "repetitions": repetitions, "scenario_count": len(scenario_ids), "execution_count": len(results), "passed": passed, "failed_or_errors": len(results) - passed, "pass_rate": passed / len(results), "scenario_summary": summary, "results": results}
