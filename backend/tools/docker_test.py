import subprocess
import tempfile
import os


def test_docker():

    temp_dir = tempfile.mkdtemp()

    try:

        file_path = os.path.join(
            temp_dir,
            "hello.py"
        )

        with open(
            file_path,
            "w"
        ) as file:

            file.write(
                "print('Hello from Docker')"
            )

        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{temp_dir}:/workspace",
                "-w",
                "/workspace",
                "python:3.12-slim",
                "python",
                "hello.py"
            ],
            capture_output=True,
            text=True
        )

        print("STDOUT:")
        print(result.stdout)

        print("STDERR:")
        print(result.stderr)

        print(
            "RETURN CODE:",
            result.returncode
        )

    finally:

        try:

            os.remove(file_path)
            os.rmdir(temp_dir)

        except Exception:
            pass


if __name__ == "__main__":
    test_docker()