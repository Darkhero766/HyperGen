from hypergen.scenarios import SCENARIOS, run_scenario


def test_demo_scenarios_are_repeatable_and_pass():
    for scenario_id in SCENARIOS:
        first = run_scenario(scenario_id, agent_mode="demo")
        second = run_scenario(scenario_id, agent_mode="demo")
        assert first["passed"] is True, first
        assert second["passed"] is True, second
        assert first["actual"]["refunded"] == second["actual"]["refunded"]
        assert first["actual"]["status"] == second["actual"]["status"]


def test_prompt_injection_scenario_does_not_refund_in_demo():
    result = run_scenario("prompt_injection", agent_mode="demo")
    assert result["passed"] is True
    assert result["actual"]["refunded"] is False
    assert result["actual"]["status"] == "paid"


def test_unknown_scenario_fails_clearly():
    try:
        run_scenario("not-a-scenario")
    except ValueError as exc:
        assert "Unknown scenario" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
