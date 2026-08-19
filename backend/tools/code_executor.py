import subprocess
import sys
import tempfile
import os


def execute_python_code(code: str, timeout: int = 10) -> dict:

    temp_file = None

    try:

        # Create temporary Python file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as file:

            file.write(code)
            temp_file = file.name

        # Execute the generated Python file
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "stdout": "",
            "stderr": "Execution timed out.",
            "return_code": -1
        }

    except Exception as e:

        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "return_code": -1
        }

    finally:

        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)