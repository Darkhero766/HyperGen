# HyperGen — Agent Reliability Lab

HyperGen is an early MVP for testing AI-agent behavior in a controlled, stateful simulated environment.

## What is in this MVP

- Synthetic online store with isolated state per test
- Deterministic demo agent, so the project works without model API keys
- Optional OpenAI model-backed decision evaluation (recommendation-only)
- Bounded OpenAI and NVIDIA OpenAI-compatible tool-using agent modes with synthetic-store tools and a five-round tool-call limit
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
# .venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
streamlit run app.py
```

The default `demo` mode is free of model API charges and requires no API key. It uses deterministic, predefined behavior; it does not measure the capability of a real model. Codespaces itself may have separate usage limits or charges depending on your GitHub account.

## OpenAI modes (optional)

```bash
export HYPERGEN_AGENT_MODE=openai_tools
export OPENAI_API_KEY=your_key
export OPENAI_MODEL=gpt-4.1-mini
streamlit run app.py
```

The `openai` mode asks a model to recommend a decision and does not execute it. The `openai_tools` mode lets the model call only the in-memory synthetic-store tools (`get_order` and `issue_refund`), with a five-round tool-call limit.

## NVIDIA hosted API mode (optional)

Create an NVIDIA API key in the [NVIDIA API Catalog](https://build.nvidia.com/), then add it to your environment or GitHub Codespaces secrets as `NVIDIA_API_KEY`. Do not commit the key to Git.

Set these variables before launching the app:

```bash
export HYPERGEN_AGENT_MODE=nvidia_tools
export NVIDIA_API_KEY=your_key
export NVIDIA_MODEL=nvidia/nemotron-3-super-120b-a12b
# Optional: override the OpenAI-compatible endpoint if the model page specifies a different one
# export NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
streamlit run app.py
```

You can also choose `nvidia_tools` in the dashboard. The default base URL is `https://integrate.api.nvidia.com/v1`; the default model ID is a starting point, not a guarantee that the model or endpoint is enabled for every account. If you select a different model in NVIDIA's catalog, set `NVIDIA_MODEL` to the exact model identifier shown there. Tool/function calling must be supported by the selected hosted model. Check current NVIDIA rate limits and terms; free access is not guaranteed to be unlimited.

## Safety and limitations

Tool calls affect only the synthetic in-memory store. Refund eligibility is checked by Python independently of model instructions. This experimental harness is not a production security boundary: do not connect real payment systems, production accounts, customer secrets, or sensitive real data.

The local policy suite requires no model API key and makes no network calls:

```bash
python -m pytest -q
```

It checks refund authorization, missing orders, duplicate refunds, and the 30-day boundary. These tests validate the simulator's Python policy enforcement; they do not prove that a real AI model will follow instructions.

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
