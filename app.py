from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import streamlit as st
from dotenv import load_dotenv

from hypergen.scenarios import SCENARIOS, run_scenario

load_dotenv()
st.set_page_config(page_title="HyperGen | Agent Reliability Lab", page_icon="🛡️", layout="wide")

if "run_history" not in st.session_state:
    st.session_state.run_history = []

st.title("🛡️ HyperGen")
st.subheader("Agent Reliability Lab")
st.caption(
    "Test AI-agent behavior in a controlled simulated environment. "
    "This is an early prototype, not a production security guarantee."
)

with st.sidebar:
    st.header("Test configuration")
    default_mode = os.getenv("HYPERGEN_AGENT_MODE", "demo").lower()
    agent_mode = st.selectbox(
        "Agent mode",
        ["demo", "openai"],
        index=0 if default_mode != "openai" else 1,
        help="Demo works without credentials. OpenAI mode requires OPENAI_API_KEY.",
    )
    selected = st.multiselect(
        "Scenarios",
        options=list(SCENARIOS),
        default=list(SCENARIOS),
        format_func=lambda key: SCENARIOS[key].title,
    )
    st.divider()
    st.caption("Synthetic data only. No real payments or production systems are connected.")

a, b, c = st.columns(3)
a.metric("Scenarios available", len(SCENARIOS))
b.metric("Runs this session", len(st.session_state.run_history))
c.metric("Agent mode", agent_mode.upper())

st.markdown(
    """
    **What this prototype does**
    - Creates a fresh simulated store for each scenario.
    - Gives the baseline agent a limited set of store tools.
    - Enforces refund eligibility in Python.
    - Compares observed state with expected outcomes.
    - Exports run evidence as JSON.
    """
)

if st.button("▶ Run selected tests", type="primary", disabled=not selected, use_container_width=True):
    results = []
    with st.spinner("Running scenarios..."):
        for scenario_id in selected:
            try:
                results.append(run_scenario(scenario_id, agent_mode=agent_mode))
            except Exception as exc:
                results.append({
                    "scenario_id": scenario_id,
                    "scenario_title": SCENARIOS[scenario_id].title,
                    "status": "ERROR",
                    "passed": False,
                    "summary": f"{type(exc).__name__}: {exc}",
                    "events": [],
                    "expected": {},
                    "actual": {},
                    "agent_mode": agent_mode,
                })
    record = {
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "agent_mode": agent_mode,
        "results": results,
    }
    st.session_state.run_history.insert(0, record)

if st.session_state.run_history:
    latest = st.session_state.run_history[0]
    results = latest["results"]
    passed = sum(bool(r.get("passed")) for r in results)
    failed = len(results) - passed
    st.divider()
    st.header("Latest run")
    st.caption(f"Run ID: {latest['run_id']} · {latest['created_at']} · Mode: {latest['agent_mode']}")
    x, y, z = st.columns(3)
    x.metric("Tests", len(results))
    y.metric("Passed", passed)
    z.metric("Failed / errors", failed)

    for result in results:
        icon = "✅" if result.get("passed") else ("⚠️" if result.get("status") == "ERROR" else "❌")
        with st.expander(f"{icon} {result.get('scenario_title', result['scenario_id'])} — {result.get('status', 'UNKNOWN')}"):
            st.write(result.get("summary", "No summary."))
            left, right = st.columns(2)
            with left:
                st.markdown("**Expected outcome**")
                st.json(result.get("expected", {}))
            with right:
                st.markdown("**Observed state / decision**")
                st.json(result.get("actual", {}))
            st.markdown("**Execution evidence**")
            if result.get("events"):
                st.dataframe(result["events"], use_container_width=True, hide_index=True)
            else:
                st.info("No execution events were recorded.")
            st.download_button(
                "Download this result (JSON)",
                data=json.dumps(result, indent=2),
                file_name=f"{result['scenario_id']}-result.json",
                mime="application/json",
                key=f"download-{latest['run_id']}-{result['scenario_id']}",
            )

    st.download_button(
        "Download full run report",
        data=json.dumps(latest, indent=2),
        file_name=f"hypergen-run-{latest['run_id']}.json",
        mime="application/json",
    )
    with st.expander("Run history (this browser session only)"):
        for record in st.session_state.run_history:
            st.write(f"{record['run_id']} — {len(record['results'])} scenarios — {record['created_at']}")
else:
    st.info("Choose scenarios in the sidebar and click **Run selected tests** to generate the first report.")

st.divider()
st.caption("HyperGen MVP · Local synthetic data only · Results are scenario-specific and do not certify general AI safety.")
