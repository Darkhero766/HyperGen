# Changelog

All notable project changes are recorded here. This early project does not yet follow formal release/versioning practices.

## 2026-10-17

### Added
- `docs/GO_TO_MARKET.md`: initial customer segments, discovery questions, pricing hypotheses, outreach, and validation milestones.
- `docs/BENCHMARK_STRATEGY.md`: benchmark design, proposed scenario matrix, dimensions, metrics, and release gates.
- `docs/INITIAL_TARGET_ACCOUNTS.md`: prospect hypotheses based on public product descriptions; no buying intent is implied.
- `docs/prospect_tracker.csv`: initial prospect tracker template.

### Changed
- Updated README to describe all eight currently registered scenarios instead of the stale three-scenario list.
- Updated README roadmap to prioritize evaluator validation, repeatability, and customer discovery before broad adapter work.

### Pending validation
- Pull request #1 proposes restricting synthetic-store reads and writes to the scenario's declared target order, plus evaluator checks and unit tests for out-of-scope tool attempts.
- The new code and tests have not yet been run in the user's Codespace. Do not treat the PR as verified or merge it until `python -m pytest -q` passes.
