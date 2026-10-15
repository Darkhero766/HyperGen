# HyperGen — Agent Reliability Lab

HyperGen is an early MVP for testing AI-agent behavior in a controlled, stateful simulated environment.

## What is in this MVP

- Synthetic online store with isolated state per test
- Deterministic demo agent, so the project works without model API keys
- Optional OpenAI model-backed decision evaluation (recommendation-only)\n- Bounded OpenAI tool-using agent mode with synthetic-store tools and a five-round tool-call limit
- Three scenarios: eligible refund, expired refund window, malicious order note
- Tool-level refund policy enforcement independent of model instructions
- Ground-truth verification against actual simulated state
- Streamlit dashboard with run evidence and JSON exports
- Unit tests, Dockerfile, and environment-variable example

**Prototype disclaimer:** This is not a production security product. Passing these scenarios does not prove general AI safety. The simulated store is not connected to real payment systems.

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
streamlit run app.py
```

The default mode is a deterministic demo and requires no API key.

## Optional model-backed evaluation

Set these environment variables before launching:

```bash
export HYPERGEN_AGENT_MODE=openai
export OPENAI_API_KEY=your_key
export OPENAI_MODEL=gpt-4.1-mini
streamlit run app.py
```

PowerShell:

```powershell
$env:HYPERGEN_AGENT_MODE="openai"
$env:OPENAI_API_KEY="your_key"
$env:OPENAI_MODEL="gpt-4.1-mini"
streamlit run app.py
```

Model-backed `openai` mode asks a model to recommend a decision and does not execute it. The `openai_tools` mode lets the model call only the in-memory synthetic-store tools (`get_order` and `issue_refund`), with a five-round tool-call limit. Refund eligibility is checked by Python independently of model instructions. This is an experimental sandbox, not a production security boundary: do not connect real payment systems, production accounts, customer secrets, or sensitive real data.\n\nTo use tool mode, set `HYPERGEN_AGENT_MODE=openai_tools` and `OPENAI_API_KEY`, then launch the app. You can also select `openai_tools` from the dashboard.

## Run tests

```bash
pytest -q
```

## Docker

```bash
docker build -t hypergen .
docker run --rm -p 8501:8501 hypergen
```

## Current scenarios

1. `valid_refund`: refund an eligible synthetic order.
2. `ineligible_refund`: reject an order outside the refund window.
3. `prompt_injection`: ignore malicious instructions embedded in an untrusted order note.

## Next engineering milestones

1. Add a documented adapter for external agents.
2. Add stronger isolation and explicit capability boundaries.
3. Add versioned scenarios and reproducible run records.
4. Benchmark repeatability, false positives, runtime, and task success.
5. Export evidence-rich reports suitable for design-partner review.
6. Conduct independent security review before testing customer systems.
