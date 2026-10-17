from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import streamlit as st
from dotenv import load_dotenv

from hypergen.benchmark import run_benchmark_batch
from hypergen.evaluator_validation import run_evaluator_self_test
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

with st.expander("🧪 Evaluator self-test: seeded violations + safe controls", expanded=False):
    st.write(
        "Checks whether the current evaluator detects known synthetic violations "
        "without flagging curated safe controls. This is a finite self-test, not a "
        "measure of real-world security coverage."
    )
    if st.button("Run evaluator self-test", key="run-evaluator-self-test"):
        self_test = run_evaluator_self_test()
        left, middle, right, extra = st.columns(4)
        left.metric("Seeded violations", f"{self_test['detected_violations']}/{self_test['seeded_violation_count']}")
        middle.metric("Mutation detection", f"{self_test['mutations_detected']}/{self_test['mutation_count']}")
        right.metric("Missed violations", self_test["missed_violations"] + self_test["mutations_missed"])
        extra.metric("Safe-control false positives", f"{self_test['false_positives']}/{self_test['safe_control_count']}")
        if self_test["passed_target"]:
            st.success("All seeded violations detected; no curated safe controls flagged.")
        else:
            st.error("Evaluator self-test target failed. Inspect the case-level results.")
        st.dataframe(
            [
                {"Case": item["case_id"], "Type": "Seeded violation", "Detected / false positive": item["detected"], "Failed checks": ", ".join(item["failed_checks"])}
                for item in self_test["violations"]
            ] + [
                {"Case": item["case_id"], "Type": "Mutation", "Detected / false positive": item["detected"], "Failed checks": ", ".join(item["failed_checks"])}
                for item in self_test["mutations"]
            ] + [
                {"Case": item["case_id"], "Type": "Safe control", "Detected / false positive": item["false_positive"], "Failed checks": ", ".join(item["failed_checks"])}
                for item in self_test["safe_controls"]
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(self_test["scope_note"])

with st.sidebar:
    st.header("Test configuration")
    default_mode = os.getenv("HYPERGEN_AGENT_MODE", "demo").lower()
    modes = ["demo", "openai", "openai_tools", "nvidia_tools"]
    agent_mode = st.selectbox(
        "Agent mode",
        modes,
        index={mode: i for i, mode in enumerate(modes)}.get(default_mode, 0),
        help="Demo needs no key. OpenAI modes require OPENAI_API_KEY. NVIDIA tool mode requires NVIDIA_API_KEY and a hosted NVIDIA model that supports tool calling.",
    )
    selected = st.multiselect(
        "Scenarios",
        options=list(SCENARIOS),
        default=list(SCENARIOS),
        format_func=lambda key: SCENARIOS[key].title,
    )
    repetitions = st.slider("Repetitions per scenario", min_value=1, max_value=5, value=1, help="Repeated model runs may incur additional API costs.")
    st.divider()
    st.caption("Synthetic data only. No real payments or production systems are connected.")

if agent_mode == "demo":
    st.info("Free local mode: deterministic baseline only. No model API calls or API key required.")
elif agent_mode == "openai":
    st.warning("API mode: sends scenario data to OpenAI and may incur API charges. This mode evaluates recommendations only.")
elif agent_mode == "openai_tools":
    st.warning("OpenAI tool mode: API usage may incur charges. Tool calls affect only the synthetic in-memory store.")
else:
    st.warning("NVIDIA tool mode: check NVIDIA model/API limits and terms. Tool calls affect only the synthetic in-memory store.")

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

if st.button("▶ Run selected tests", type="primary", disabled=not selected, width="stretch"):
    with st.spinner(f"Running {len(selected) * repetitions} executions..."):
        batch = run_benchmark_batch(selected, agent_mode, repetitions, run_scenario, {key: value.title for key, value in SCENARIOS.items()})
    record = {"run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"), "created_at": datetime.now(timezone.utc).isoformat(), **batch}
    st.session_state.run_history.insert(0, record)

if st.session_state.run_history:
    latest = st.session_state.run_history[0]
    results = latest["results"]
    passed = latest["passed"]
    failed = latest["failed_or_errors"]
    st.divider()
    st.header("Latest run")
    st.caption(f"Run ID: {latest['run_id']} · {latest['created_at']} · Mode: {latest['agent_mode']}")
    x, y, z = st.columns(3)
    x.metric("Tests", len(results))
    y.metric("Passed", passed)
    z.metric("Failed / errors", failed)

    st.metric("Overall execution pass rate", f"{latest['pass_rate']:.1%}")
    st.markdown("**Per-scenario repeatability**")
    st.dataframe([{"Scenario": item["scenario_title"], "Executions": item["executions"], "Passed": item["passes"], "Failed / errors": item["failures_or_errors"], "Pass rate": f"{item['pass_rate']:.1%}", "Consistent outcome": item["consistent_outcome"]} for item in latest["scenario_summary"].values()], use_container_width=True, hide_index=True)

    for result in results:
        icon = "✅" if result.get("passed") else ("⚠️" if result.get("status") == "ERROR" else "❌")
        with st.expander(f"Run {result.get('repetition', 1)} · {icon} {result.get('scenario_title', result['scenario_id'])} — {result.get('status', 'UNKNOWN')}"):
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
