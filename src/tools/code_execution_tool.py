import os
import subprocess
import sys
import tempfile
from pathlib import Path

from langchain_core.tools import tool


EXECUTION_TIMEOUT_SECONDS = 10
MAX_CODE_LENGTH = 20_000
MAX_OUTPUT_LENGTH = 10_000


def _validate_code(code: str) -> None:
    if not code or not code.strip():
        raise ValueError("Code cannot be empty.")

    if len(code) > MAX_CODE_LENGTH:
        raise ValueError(
            f"Code exceeds the maximum limit of {MAX_CODE_LENGTH} characters."
        )


def _execute_python_code(code: str) -> tuple[int, str, str]:
    with tempfile.TemporaryDirectory(prefix="agentforge_exec_") as temp_dir:
        temp_path = Path(temp_dir)
        script_path = temp_path / "main.py"

        script_path.write_text(
            code,
            encoding="utf-8",
        )

        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONIOENCODING": "utf-8",
        }

        process = subprocess.run(
            [
                sys.executable,
                "-I",
                str(script_path),
            ],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT_SECONDS,
            env=env,
        )

        return (
            process.returncode,
            process.stdout,
            process.stderr,
        )


@tool
def code_execution_tool(code: str) -> str:
    """
    Execute Python code in a temporary isolated subprocess
    and return its output.
    """

    try:
        _validate_code(code)

        return_code, stdout, stderr = _execute_python_code(code)

        stdout = stdout.strip()
        stderr = stderr.strip()

        if len(stdout) > MAX_OUTPUT_LENGTH:
            stdout = (
                stdout[:MAX_OUTPUT_LENGTH]
                + "\n[Output truncated]"
            )

        if len(stderr) > MAX_OUTPUT_LENGTH:
            stderr = (
                stderr[:MAX_OUTPUT_LENGTH]
                + "\n[Error output truncated]"
            )

        if return_code == 0:
            if not stdout:
                return "Code executed successfully with no output."

            return (
                "Code executed successfully.\n"
                f"Output:\n{stdout}"
            )

        return (
            "Code execution failed.\n"
            f"Exit code: {return_code}\n"
            f"Error:\n{stderr or 'Unknown execution error.'}"
        )

    except subprocess.TimeoutExpired:
        return (
            "Code execution failed: "
            f"execution exceeded {EXECUTION_TIMEOUT_SECONDS} seconds."
        )

    except ValueError as exc:
        return f"Code validation failed: {str(exc)}"

    except Exception as exc:
        return f"Code execution error: {str(exc)}"
    