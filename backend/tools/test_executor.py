import os
import subprocess
import sys
import tempfile


DOCKER_IMAGE = "python:3.12-slim"


def execute_tests(
    generated_code: str,
    test_code: str,
    timeout: int = 10
) -> dict:

    temp_dir = tempfile.mkdtemp()

    source_file = os.path.join(
        temp_dir,
        "solution.py"
    )

    test_file = os.path.join(
        temp_dir,
        "test_solution.py"
    )

    try:

        # -----------------------------------------
        # Write generated solution
        # -----------------------------------------

        with open(
            source_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(generated_code)


        # -----------------------------------------
        # Write generated tests
        # -----------------------------------------

        with open(
            test_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(test_code)


        # -----------------------------------------
        # Docker command
        # -----------------------------------------

        command = [
            "docker",
            "run",
            "--rm",

            # Disable network
            "--network",
            "none",

            # Limit memory
            "--memory",
            "256m",

            # Limit CPU
            "--cpus",
            "1",

            # Mount temporary directory
            "-v",
            f"{temp_dir}:/workspace",

            # Working directory
            "-w",
            "/workspace",

            DOCKER_IMAGE,

            "python",

            "-m",
            "unittest",

            "discover",

            "-s",
            "/workspace",

            "-p",
            "test_*.py",
        ]


        # -----------------------------------------
        # Execute Docker container
        # -----------------------------------------

        result = subprocess.run(
            command,
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
            "stderr": "Docker execution timed out.",
            "return_code": -1
        }


    except FileNotFoundError:

        return {
            "success": False,
            "stdout": "",
            "stderr": (
                "Docker was not found. "
                "Make sure Docker Desktop is installed "
                "and running."
            ),
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

        # -----------------------------------------
        # Cleanup
        # -----------------------------------------

        try:

            for filename in os.listdir(temp_dir):

                file_path = os.path.join(
                    temp_dir,
                    filename
                )

                os.remove(file_path)

            os.rmdir(temp_dir)

        except Exception:
            pass