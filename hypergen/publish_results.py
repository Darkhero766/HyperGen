"""Explicit review-gated synchronization of benchmark summaries to the website."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .benchmark_runner import validate_results

def publish(source: Path, web: Path, *, reviewed: bool = False) -> dict:
    if not reviewed:
        raise ValueError("Publishing requires explicit --reviewed acknowledgement")
    data = json.loads(source.read_text(encoding="utf-8"))
    validate_results(data)
    rows = []
    for s in data.get("summary", []):
        if not s["evaluated"] or s["pass_rate"] is None:
            continue
        if not isinstance(s["pass_rate"], (int, float)) or not 0 <= s["pass_rate"] <= 100:
            raise ValueError("Invalid pass rate")
        rows.append({"model": s["model"], "pass_rate": s["pass_rate"],
                     "evidence_url": "https://github.com/Darkhero766/HyperGen/blob/main/results/results.json"})
    payload = {"schema_version": "1.0", "status": "reviewed", "runs": rows}
    for path in [web / "data" / "results.json", web / "public" / "data" / "results.json"]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=Path("results/results.json"))
    p.add_argument("--web", type=Path, default=Path("web"))
    p.add_argument("--reviewed", action="store_true", help="I reviewed model IDs, traces and failures")
    args = p.parse_args()
    publish(args.source, args.web, reviewed=args.reviewed)

if __name__ == "__main__":
    main()
