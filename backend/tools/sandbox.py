import subprocess
import tempfile
from pathlib import Path


class SandboxResult:
    def __init__(
        self,
        stdout: str,
        stderr: str,
        return_code: int,
        timed_out: bool = False,
    ):
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.timed_out = timed_out


def run_python_sandbox(
    code: str,
    timeout: int = 10,
) -> SandboxResult:

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_path = Path(temp_dir)

        code_file = temp_path / "main.py"

        code_file.write_text(
            code,
            encoding="utf-8",
        )

        command = [
            "docker",
            "run",
            "--rm",

            # No network access
            "--network",
            "none",

            # Resource limits
            "--memory",
            "128m",

            "--cpus",
            "0.5",

            "--pids-limit",
            "64",

            # Read-only container
            "--read-only",

            # Temporary filesystem
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=16m",

            # Mount only the generated file
            "-v",
            f"{code_file}:/app/main.py:ro",

            # Working directory
            "-w",
            "/app",

            "python:3.12-slim",

            "python",
            "/app/main.py",
        ]

        try:

            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return SandboxResult(
                stdout=process.stdout,
                stderr=process.stderr,
                return_code=process.returncode,
            )

        except subprocess.TimeoutExpired as exc:

            return SandboxResult(
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                return_code=-1,
                timed_out=True,
            )