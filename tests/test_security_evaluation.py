from hypergen.scenarios import run_scenario
from hypergen.world import fresh_store, get_order


def test_order_read_minimizes_sensitive_fields():
    state = fresh_store("privacy")
    result = get_order(state, "ORD-100")

    assert result["ok"] is True
    assert "customer_id" not in result["order"]
    assert "CUS-100" not in str(result["order"])


def test_demo_report_includes_security_checks():
    result = run_scenario("prompt_injection", agent_mode="demo")

    assert result["passed"] is True
    assert result["security_checks"]["no_customer_id_in_final_response"] is True
    assert result["security_checks"]["no_customer_id_in_tool_output"] is True
    assert result["security_checks"]["no_refund_tool_attempt_in_read_only_scenario"] is True
