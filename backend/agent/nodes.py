from .llm import llm,llm2
from ..tools.code_executor import execute_python_code
from ..tools.test_executor import execute_tests
from datetime import datetime
import re
import os
import sys
import tempfile
import subprocess



def extract_text(content) -> str:
    if isinstance(content, str):
        return content.strip()
    elif isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(text)
        return "\n".join(parts).strip()
    return str(content).strip() if content is not None else ""


def clean_python_code(content) -> str:
    text = extract_text(content)
    if not text:
        return ""
    # Extract code inside ```python ... ``` or ``` ... ```
    pattern = r"```(?:python)?\s*\n?(.*?)\n?```"
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return max(matches, key=len).strip()
    return text.strip()


def create_event(
    node: str,
    status: str,
    message: str,
):
    return {
        "node": node,
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }
def planner_node(state):

    task = state["task"]

    prompt = f"""
You are a software engineering planner.

Analyze the following coding task:

{task}

Create a short step-by-step implementation plan.

Return only the numbered plan.
"""

    response = llm.invoke(prompt)

    content = response.content

    # Handle string response
    if isinstance(content, str):
        plan = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

    # Handle list response
    elif isinstance(content, list):
        plan = []

        for item in content:
            if isinstance(item, str):
                plan.append(item.strip())

            elif isinstance(item, dict):
                text = item.get("text")

                if text:
                    plan.append(text.strip())

    else:
        raise TypeError(
            f"Unexpected response.content type: {type(content)}"
        )

    return {
    "plan": plan,

    "events": [
        create_event(
            "planner",
            "completed",
            "Planning completed successfully."
        )
    ]
}
def coder_node(state):

    task = state["task"]
    plan = state["plan"]

    prompt = f"""
You are an expert Python developer.

User task:
{task}

Implementation plan:
{plan}

Write the complete Python implementation.

Requirements:
- Write clean Python code
- Follow the implementation plan
- Handle reasonable edge cases
- Do not explain the code
- Return ONLY Python code
- Do not use markdown code fences
"""

    response = llm.invoke(prompt)

    generated_code = clean_python_code(response.content)

    return {
    "generated_code": generated_code,

    "events": [
        create_event(
            "coder",
            "completed",
            "Code generation completed."
        )
    ]
}


def executor_node(state):
    code = state.get("generated_code", "")
    test_code = state.get("test_code", "")

    if not code:
        return {
            "execution_result": "No code generated.",
            "error": "generated_code is empty",
        }

    if not test_code:
        return {
            "execution_result": "No test code generated.",
            "error": "test_code is empty",
        }

    try:
        with tempfile.TemporaryDirectory() as temp_dir:

            solution_path = os.path.join(
                temp_dir,
                "solution.py"
            )

            test_path = os.path.join(
                temp_dir,
                "test_solution.py"
            )

            # Write generated solution
            with open(
                solution_path,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(code)

            # Write generated tests
            with open(
                test_path,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(test_code)

            # Execute tests
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    "test_solution.py",
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=15,
            )

            execution_result = (
                f"STDOUT:\n{result.stdout}\n\n"
                f"STDERR:\n{result.stderr}\n\n"
                f"RETURN CODE: {result.returncode}"
            )

            return {
                "execution_result": execution_result,
                "error": "",
            }

    except subprocess.TimeoutExpired:
        return {
            "execution_result": "",
            "error": "Code execution timed out after 15 seconds.",
        }

    except Exception as e:
        return {
            "execution_result": "",
            "error": str(e),
        }
def debugger_node(state):

    task = state["task"]
    generated_code = state["generated_code"]
    error = state["error"]
    execution_result = state["execution_result"]
    test_result = state["test_result"]
    retry_count = state["retry_count"]

    prompt = f"""
You are an expert Python debugging agent.

User task:
{task}

Current code:
{generated_code}

Execution result:
{execution_result}

Test result:
{test_result}

Error:
{error}

Fix the code so that the tests pass.

Requirements:
- Fix the actual problem
- Preserve the original task
- Return ONLY corrected Python code
- Do not use markdown code fences
- Do not explain anything
"""

    response = llm2.invoke(prompt)

    fixed_code = clean_python_code(response.content)

    return {
        "generated_code": fixed_code,
        "retry_count": retry_count + 1,
        "status": "debugged"
    }
def execution_router(state):

    status = state["status"]
    retry_count = state["retry_count"]

    if status == "tests_passed":
        return "success"

    if retry_count >= 3:
        return "max_retries"

    return "debug"
def test_generator_node(state):

    task = state["task"]
    generated_code = state["generated_code"]

    prompt = f"""
You are an expert Python test engineer.

User task:
{task}

Generated Python code:
{generated_code}

Create comprehensive unit tests for the GENERATED CODE.

IMPORTANT:
- Do NOT rewrite or copy the generated function.
- The generated code will be saved as `solution.py`.
- Your test file will be saved as `test_solution.py`.
- Import the required functions/classes from `solution.py`.
- Use Python unittest.
- Test normal cases.
- Test edge cases.
- Test invalid inputs when appropriate.
- Return ONLY executable Python test code.
- Do not use markdown code fences.

Example:

import unittest
from solution import function_name

class TestFunction(unittest.TestCase):

    def test_basic_case(self):
        self.assertEqual(function_name(...), ...)

if __name__ == "__main__":
    unittest.main()
"""

    response = llm.invoke(prompt)

    test_code = clean_python_code(response.content)

    return {
        "test_code": test_code,
        "events": [
            create_event(
                "test_generator",
                "completed",
                "Unit tests generated."
            )
        ]
    }


def tester_node(state):

    generated_code = state["generated_code"]
    test_code = state["test_code"]

    result = execute_tests(
        generated_code,
        test_code
    )

    if result["success"]:

        output_text = result['stdout'] if result['stdout'].strip() else result['stderr']
        test_result = (
            f"TESTS PASSED\n\n"
            f"{output_text}"
        )

        return {
            "test_result": test_result,
            "error": "",
            "status": "tests_passed",
            "events": [
                create_event(
                    "tester",
                    "completed",
                    "Tests passed successfully."
                )
            ]
        }

    else:

        test_result = (
            f"TESTS FAILED\n\n"
            f"STDOUT:\n"
            f"{result['stdout']}\n\n"
            f"STDERR:\n"
            f"{result['stderr']}"
        )

        return {
            "test_result": test_result,
            "status": "tests_failed",
            "error": result["stderr"] or result["stdout"],
            "events": [
                create_event(
                    "tester",
                    "completed",
                    "Test execution failed."
                )
            ]
        }
def reviewer_node(state):

    task = state["task"]
    generated_code = state["generated_code"]
    test_code = state["test_code"]
    test_result = state["test_result"]
    retry_count = state["retry_count"]

    prompt = f"""
You are a senior software engineer reviewing an AI-generated solution.

USER TASK:
{task}

GENERATED CODE:
{generated_code}

TEST CODE:
{test_code}

TEST RESULT:
{test_result}

RETRY COUNT:
{retry_count}

Review the solution.

Evaluate:

1. Correctness
2. Code quality
3. Edge-case handling
4. Test coverage
5. Whether the solution satisfies the original task

Return a concise professional review.
"""

    response = llm2.invoke(prompt)

    content = response.content

    if isinstance(content, str):
        review = content.strip()

    elif isinstance(content, list):

        parts = []

        for item in content:

            if isinstance(item, str):
                parts.append(item)

            elif isinstance(item, dict):

                text = item.get("text")

                if text:
                    parts.append(text)

        review = "\n".join(parts).strip()

    else:

        raise TypeError(
            f"Unexpected response.content type: {type(content)}"
        )

    return {
    "review": review,

    "events": [
        create_event(
            "reviewer",
            "completed",
            "Code review completed."
        )
    ]
}
def final_report_node(state):
    task = state.get("task", "")
    plan = state.get("plan", [])
    generated_code = state.get("generated_code", "")
    test_code = state.get("test_code", "")
    test_result = state.get("test_result", "")
    review = state.get("review", "")
    retry_count = state.get("retry_count", 0)

    plan_text = "\n".join(plan) if isinstance(plan, (list, tuple)) else str(plan)

    final_report = f"""# Autonomous Coding Agent Report

## Task
{task}

## Implementation Plan
{plan_text}

## Generated Code
```python
{generated_code}
```

## Test Code
```python
{test_code}
```

## Test Result
{test_result}

## Review
{review}

## Retry Count
{retry_count}
"""

    return {
        "final_report": final_report,
        "status": "completed",
        "events": [
            create_event(
                "final_report",
                "completed",
                "Final report generated."
            )
        ]
    }


def critic_node(state):

    review = state.get(
        "review",
        ""
    )

    test_result = state.get(
        "test_result",
        ""
    )

    generated_code = state.get(
        "generated_code",
        ""
    )

    prompt = f"""
You are a senior software engineering critic.

Evaluate the following AI-generated solution.

TASK:
{state.get("task", "")}

CODE:
{generated_code}

TEST RESULT:
{test_result}

CODE REVIEW:
{review}

Determine whether the solution is production-ready.

Return exactly this format:

DECISION: APPROVED
SCORE: 0-100
REASON: <short explanation>

OR:

DECISION: REJECTED
SCORE: 0-100
REASON: <short explanation>
"""

    response = llm.invoke(prompt)

    critic_result = extract_text(response.content)

    score = 0.0

    for line in critic_result.splitlines():

        if line.startswith("SCORE:"):

            try:
                score = float(
                    line.split(
                        ":",
                        1
                    )[1].strip()
                )
            except ValueError:
                score = 0.0

    return {
        "critic_result": critic_result,
        "quality_score": score,
        "events": [
            create_event(
                "critic",
                "completed",
                "Quality evaluation completed."
            )
        ]
    }


def reflection_node(state):

    critic_result = state.get(
        "critic_result",
        ""
    )

    generated_code = state.get(
        "generated_code",
        ""
    )

    review = state.get(
        "review",
        ""
    )

    prompt = f"""
You are an autonomous software engineer.

The previous implementation was rejected.

TASK:
{state.get("task", "")}

CURRENT CODE:
{generated_code}

REVIEW:
{review}

CRITIC:
{critic_result}

Analyze what went wrong.

Create a concise correction plan.

Return:

PROBLEM:
<what is wrong>

CHANGES:
1. ...
2. ...
3. ...

NEW APPROACH:
<how the implementation should be improved>
"""

    response = llm.invoke(prompt)

    reflection_text = extract_text(response.content)

    return {
        "reflection": reflection_text,
        "retry_count": state.get("retry_count", 0) + 1,
        "events": [
            create_event(
                "reflection",
                "completed",
                "Agent identified improvements."
            )
        ]
    }


def critic_router(state):

    critic_result = extract_text(state.get(
        "critic_result",
        ""
    ))

    retry_count = state.get(
        "retry_count",
        0
    )

    if retry_count >= 3:
        return "approved"

    if "DECISION: APPROVED" in critic_result:
        return "approved"

    if "DECISION: REJECTED" in critic_result:
        return "reflect"

    return "approved"
