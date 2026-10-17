from hypergen.evaluator_validation import run_evaluator_self_test

def test_evaluator_self_test_detects_every_seeded_violation_and_no_safe_controls():
    report = run_evaluator_self_test()
    assert report["seeded_violation_count"] == 5
    assert report["detected_violations"] == 5
    assert report["missed_violations"] == 0
    assert report["detection_rate"] == 1.0
    assert report["safe_control_count"] == 3
    assert report["false_positives"] == 0
    assert report["false_positive_rate"] == 0.0
    assert report["mutation_count"] == 7
    assert report["mutations_detected"] == 7
    assert report["mutations_missed"] == 0
    assert report["mutation_detection_rate"] == 1.0
    assert report["passed_target"] is True

def test_each_seeded_violation_is_detected_individually():
    report = run_evaluator_self_test()
    assert all(item["detected"] for item in report["violations"])

def test_each_safe_control_has_no_false_positive():
    report = run_evaluator_self_test()
    assert all(not item["false_positive"] for item in report["safe_controls"])


def test_each_mutated_violation_is_detected():
    report = run_evaluator_self_test()
    assert all(item["detected"] for item in report["mutations"])


def test_mutation_suite_includes_expected_cases():
    report = run_evaluator_self_test()
    case_ids = {item["case_id"] for item in report["mutations"]}
    assert "refund_claim_case_variant" in case_ids
    assert "customer_id_nested_tool_result" in case_ids
    assert "wrong_order_read_variant" in case_ids
