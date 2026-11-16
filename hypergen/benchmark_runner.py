"""Reproducible, synthetic-only NVIDIA tool benchmark. No API key is serialized."""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import agent
from .scenarios import SCENARIOS, run_scenario

SCHEMA_VERSION = "1.0"
EVALUATOR_VERSION = "0.1.0"
MODEL_CONFIG = Path(__file__).resolve().parent.parent / "models.yaml"


def load_models(path: Path = MODEL_CONFIG) -> list[str]:
    """Minimal YAML subset: a models: list of NVIDIA model ID strings."""
    lines = path.read_text(encoding="utf-8").splitlines()
    models: list[str] = []
    inside = False
    for line in lines:
        stripped = line.split("#", 1)[0].strip()
        if stripped == "models:":
            inside = True
        elif stripped.startswith("- ") and inside:
            model = stripped[2:].strip().strip("'\"")
            if model:
                models.append(model)
        elif stripped and not stripped.startswith("#"):
            inside = False
    return models


def wilson(passes: int, total: int) -> list[float] | None:
    if not total:
        return None
    z = 1.959963984540054
    p = passes / total
    denom = 1 + z*z/total
    center = (p + z*z/(2*total)) / denom
    half = z*math.sqrt((p*(1-p)+z*z/(4*total))/total) / denom
    return [round(max(0, center-half), 6), round(min(1, center+half), 6)]


def summarize(rows: list[dict[str, Any]], model: str, k: int) -> dict[str, Any]:
    subset = [r for r in rows if r["model"] == model]
    valid = [r for r in subset if r["verdict"] in ("PASS", "FAIL")]
    passed = sum(r["verdict"] == "PASS" for r in valid)
    counts = Counter(key for r in valid for key, ok in r["security_checks"].items() if not ok)
    by_case: dict[str, list[str]] = {}
    for row in subset:
        by_case.setdefault(row["scenario_id"], []).append(row["verdict"])
    complete = [v for v in by_case.values() if len(v) == k]
    consistent = sum(len(set(v)) == 1 for v in complete)
    pass_k = sum(all(x == "PASS" for x in v) for v in complete)
    return {
        "model": model, "attempted": len(subset), "evaluated": len(valid),
        "passed": passed, "pass_rate": round(passed/len(valid)*100, 4) if valid else None,
        "wilson_95": wilson(passed, len(valid)),
        "no_result_rate": round(sum(r["verdict"] == "no_result" for r in subset)/len(subset), 6) if subset else None,
        "consistent_scenarios": consistent, "complete_scenarios": len(complete),
        "pass_power_k": pass_k, "k": k,
        "violations_by_category": dict(sorted(counts.items())),
    }


def validate_results(payload: dict[str, Any]) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION or not isinstance(payload.get("runs"), list):
        raise ValueError("Invalid benchmark results envelope")
    required = {"run_id", "scenario_id", "scenario_version", "model", "seed",
                "tool_trace", "expected", "actual", "evaluator_version", "verdict",
                "latency_ms", "errors", "security_checks", "timestamp"}
    seen = set()
    for row in payload["runs"]:
        if not isinstance(row, dict) or not required.issubset(row):
            raise ValueError("Missing required benchmark run fields")
        if row["verdict"] not in ("PASS", "FAIL", "no_result"):
            raise ValueError("Invalid verdict")
        key = (row["model"], row["scenario_id"], row["seed"])
        if key in seen:
            raise ValueError("Duplicate model/scenario/seed")
        seen.add(key)
        if row["verdict"] == "no_result" and row["errors"] == []:
            raise ValueError("no_result must include an error")
        if not isinstance(row["tool_trace"], list) or not isinstance(row["security_checks"], dict):
            raise ValueError("Invalid trace or checks")


class RateLimitedClient:
    """Throttles every request, including retries, and preserves tool-call semantics."""
    def __init__(self, client: Any, rpm: int = 40, retries: int = 4, sleep=time.sleep, clock=time.monotonic):
        self.client = client
        self.rpm = rpm
        self.retries = retries
        self.sleep = sleep
        self.clock = clock
        self.last_request: float | None = None
        self.chat = type("Chat", (), {})()
        self.chat.completions = type("Completions", (), {})()
        self.chat.completions.create = self.create

    def create(self, **kwargs: Any) -> Any:
        for attempt in range(self.retries + 1):
            now = self.clock()
            if self.last_request is not None:
                self.sleep(max(0.0, 60/self.rpm - (now-self.last_request)))
            self.last_request = self.clock()
            try:
                return self.client.chat.completions.create(**kwargs)
            except Exception as exc:
                if getattr(exc, "status_code", None) != 429 or attempt == self.retries:
                    raise
                self.sleep(min(60, 2**attempt + random.random()))
        raise AssertionError("unreachable")


def smoke_test(client: Any, model: str) -> tuple[bool, str]:
    """A real tool-call response is required, not merely an HTTP 200."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Call the ping tool with value ready. Do not answer in text."}],
            tools=[{"type": "function", "function": {"name": "ping", "description": "Tool support check",
                    "parameters": {"type": "object", "properties": {"value": {"type": "string"}},
                                   "required": ["value"]}}}],
            tool_choice="required", temperature=0,
        )
        calls = getattr(response.choices[0].message, "tool_calls", None)
        if not calls or calls[0].function.name != "ping":
            return False, "model_did_not_return_required_tool_call"
        return True, "supported"
    except Exception as exc:
        return False, f"tool_smoke_failed:{type(exc).__name__}:status={getattr(exc, 'status_code', 'unknown')}"


def run(models: list[str], repetitions: int, out: Path, *, client: Any = None,
        smoke=smoke_test) -> dict[str, Any]:
    if repetitions < 1:
        raise ValueError("--runs must be positive")
    out.mkdir(parents=True, exist_ok=True)
    target = out / "results.json"
    payload = json.loads(target.read_text()) if target.exists() else {
        "schema_version": SCHEMA_VERSION, "status": "unverified", "runs": [], "skipped_models": {}}
    validate_results(payload)
    done = {(r["model"], r["scenario_id"], r["seed"]) for r in payload["runs"]}
    for model in models:
        if client is None:
            from openai import OpenAI
            key = os.getenv("NVIDIA_API_KEY")
            if not key:
                raise RuntimeError("NVIDIA_API_KEY is missing (configure an environment secret)")
            raw_client = OpenAI(api_key=key, base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"), max_retries=0)
        else:
            raw_client = client
        limited = RateLimitedClient(raw_client)
        ok, reason = smoke(limited, model)
        if not ok:
            payload["skipped_models"][model] = reason
            persist(payload, target, repetitions)
            continue
        payload["skipped_models"].pop(model, None)
        original = agent._model_config
        try:
            agent._model_config = lambda provider, c=limited, m=model: (c, m)
            for scenario_id in SCENARIOS:
                for seed in range(repetitions):
                    key = (model, scenario_id, seed)
                    if key in done:
                        continue
                    started = time.monotonic()
                    row = {"run_id": str(uuid.uuid4()), "scenario_id": scenario_id,
                           "scenario_version": "0.1.0", "model": model, "seed": seed,
                           "timestamp": datetime.now(timezone.utc).isoformat(),
                           "evaluator_version": EVALUATOR_VERSION, "tool_trace": [],
                           "expected": None, "actual": None, "security_checks": {},
                           "verdict": "no_result", "errors": [], "latency_ms": 0}
                    try:
                        result = run_scenario(scenario_id, agent_mode="nvidia_tools")
                        row.update(tool_trace=result["agent_result"].get("tool_calls", []),
                                   expected=result["expected"], actual=result["actual"],
                                   security_checks=result["security_checks"],
                                   verdict=result["status"])
                    except Exception as exc:
                        # Never persist exception messages: provider errors may contain sensitive request context.
                        row["errors"] = [{"type": type(exc).__name__,
                                          "status_code": getattr(exc, "status_code", None)}]
                    row["latency_ms"] = round((time.monotonic()-started)*1000, 2)
                    payload["runs"].append(row)
                    done.add(key)
                    persist(payload, target, repetitions)
        finally:
            agent._model_config = original
    return payload


def persist(payload: dict[str, Any], target: Path, repetitions: int) -> None:
    validate_results(payload)
    models = sorted({r["model"] for r in payload["runs"]})
    payload["summary"] = [summarize(payload["runs"], m, repetitions) for m in models]
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temp.replace(target)
    report = ["# HyperGen benchmark results", "", "Status: **unverified until independently reviewed**.", "",
              "Runs are synthetic. no_result is not PASS.", "",
              "| Model | PASS / evaluated | Pass rate | Wilson 95% | No result |",
              "|---|---:|---:|---|---:|"]
    for s in payload["summary"]:
        report.append(f"| {s['model']} | {s['passed']} / {s['evaluated']} | {s['pass_rate']} | {s['wilson_95']} | {s['no_result_rate']} |")
    if not models:
        report.append("| No runs yet | — | — | — | — |")
    report += ["", "See results.json for per-run evidence and skipped-model reasons."]
    (target.parent / "RESULTS.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic NVIDIA agent benchmark")
    parser.add_argument("--models", nargs="+", help="NVIDIA model IDs; defaults to models.yaml")
    parser.add_argument("--models-file", type=Path, default=MODEL_CONFIG)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--out", type=Path, default=Path("results"))
    args = parser.parse_args()
    models = args.models or load_models(args.models_file)
    if not models:
        parser.error("No models configured")
    run(models, args.runs, args.out)
    print(f"Benchmark artifacts written to {args.out}. Review before publication.")


if __name__ == "__main__":
    main()
