from dataclasses import dataclass
from typing import Any


@dataclass
class EvaluationResult:
    task_completed: bool
    tests_passed: bool
    has_code: bool
    has_test_code: bool
    has_review: bool
    has_final_report: bool
    retry_count: int
    score: float


def evaluate_agent_result(
    result: dict[str, Any]
) -> EvaluationResult:

    generated_code = result.get(
        "generated_code",
        ""
    )

    test_code = result.get(
        "test_code",
        ""
    )

    test_result = result.get(
        "test_result",
        ""
    )

    review = result.get(
        "review",
        ""
    )

    final_report = result.get(
        "final_report",
        ""
    )

    retry_count = result.get(
        "retry_count",
        0
    )


    # -----------------------------------------
    # Individual checks
    # -----------------------------------------

    has_code = bool(
        generated_code.strip()
    )

    has_test_code = bool(
        test_code.strip()
    )

    tests_passed = (
        "TESTS PASSED"
        in test_result.upper()
    )

    has_review = bool(
        review.strip()
    )

    has_final_report = bool(
        final_report.strip()
    )

    task_completed = (
        has_code
        and has_test_code
        and tests_passed
        and has_review
        and has_final_report
    )


    # -----------------------------------------
    # Score
    # -----------------------------------------

    score = 0.0

    if has_code:
        score += 20

    if has_test_code:
        score += 20

    if tests_passed:
        score += 25

    if has_review:
        score += 15

    if has_final_report:
        score += 20


    return EvaluationResult(
        task_completed=task_completed,
        tests_passed=tests_passed,
        has_code=has_code,
        has_test_code=has_test_code,
        has_review=has_review,
        has_final_report=has_final_report,
        retry_count=retry_count,
        score=score,
    )