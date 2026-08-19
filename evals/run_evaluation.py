from backend.agent.graph import graph

from evals.evaluator import (
    evaluate_agent_result
)

from evals.test_cases import TEST_CASES


def run_evaluations():

    results = []

    for case in TEST_CASES:

        print()
        print("=" * 60)
        print(
            f"Running: {case['id']}"
        )
        print("=" * 60)

        initial_state = {

            "task": case["task"],

            "plan": [],

            "current_step": 0,

            "generated_code": "",

            "test_code": "",

            "execution_result": "",

            "test_result": "",

            "review": "",

            "status": "started",

            "error": "",

            "retry_count": 0,

            "final_report": "",
        }


        result = graph.invoke(
            initial_state
        )


        evaluation = evaluate_agent_result(
            result
        )


        print(
            f"Score: {evaluation.score}/100"
        )

        print(
            f"Tests passed: "
            f"{evaluation.tests_passed}"
        )

        print(
            f"Retries: "
            f"{evaluation.retry_count}"
        )

        print(
            f"Completed: "
            f"{evaluation.task_completed}"
        )


        results.append({

            "id": case["id"],

            "score": evaluation.score,

            "tests_passed":
                evaluation.tests_passed,

            "retry_count":
                evaluation.retry_count,

            "completed":
                evaluation.task_completed,
        })


    return results


if __name__ == "__main__":

    results = run_evaluations()
    total = len(results)

    completed = sum(
    r["completed"]
    for r in results
)

    tests_passed = sum(
    r["tests_passed"]
    for r in results
)

    average_score = (
    sum(r["score"] for r in results)
    / total
    if total
    else 0
)

    average_retries = (
    sum(r["retry_count"] for r in results)
    / total
    if total
    else 0
)


    print()
    print("=" * 60)
    print("AGENT METRICS")
    print("=" * 60)

    print(
    f"Task completion rate: "
    f"{completed / total * 100:.1f}%"
)

    print(
    f"Test pass rate: "
    f"{tests_passed / total * 100:.1f}%"
)

    print(
    f"Average score: "
    f"{average_score:.1f}/100"
)

    print(
    f"Average retries: "
    f"{average_retries:.2f}"
)
    print()
    print("=" * 60)
    print("FINAL EVALUATION")
    print("=" * 60)

    for result in results:

        print(
            f"{result['id']:15} "
            f"{result['score']:5.1f}/100 "
            f"completed={result['completed']}"
        )