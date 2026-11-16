# HyperGen: synthetic agent action benchmark

**Status: unpublished / unverified. No live multi-model benchmark data has been produced by this document.**

## Methodology
The eight existing synthetic-store cases are the baseline. Each run starts with fresh in-memory state and an independent Python refund policy. Tool calls, evaluator checks and expected/actual state are recorded. Model IDs are taken from NVIDIA's hosted API and must pass a real tool-call smoke test before inclusion.

Each model/scenario/seed combination is executed once, with a configurable number of repetitions. The runner enforces at most 40 requests/minute across each model client, backs off on HTTP 429, persists each result for resume, and records exhausted or failed requests as `no_result`, never PASS.

## Results

| Model | Evaluated | Pass rate | Wilson 95% | no_result rate |
|---|---:|---:|---|---:|
| Pending verified runs | — | — | — | — |

See generated `results/RESULTS.md` and `results/results.json` after a real run. These files are **not** evidence until independently reviewed.

## Metrics and interpretation
Pass rate is PASS / (PASS + FAIL); `no_result` is reported separately. Wilson 95% confidence intervals describe sampling uncertainty, not security guarantees. `pass_power_k` counts scenarios passing all k repetitions; `consistent_scenarios` counts scenarios with identical verdicts across k runs. Violation counts are evaluator check failures grouped by check name, not a comprehensive vulnerability taxonomy.

## Limitations
- Synthetic refund/store domain only; not production or general agent security.
- Model behavior may be nondeterministic even with temperature zero.
- Current evaluator checks have finite coverage; a blocked forbidden attempt can still be scored as a failure.
- Seeds label repetitions; the hosted API may not honor a seed, so seed is **not** a determinism guarantee.
- Token cost, independent false-positive/negative estimates and cross-provider comparisons are not measured here.
- Runner does not currently capture partial tool traces on provider exceptions.
- No real external customer data or production systems should be used.
- Results must be reviewed before publication to the website.
