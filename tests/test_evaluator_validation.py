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
    assert report["passed_target"] is True

def test_each_seeded_violation_is_detected_individually():
    report = run_evaluator_self_test()
    assert all(item["detected"] for item in report["violations"])

def test_each_safe_control_has_no_false_positive():
    report = run_evaluator_self_test()
    assert all(not item["false_positive"] for item in report["safe_controls"])
