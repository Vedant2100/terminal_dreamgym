import json
import subprocess
import sys
from pathlib import Path


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "cli.py", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_empty_input():
    result = run_cli("--input", "")
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_json_flag_returns_valid_json():
    result = run_cli("--input", "hello_v4", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"result": "HELLO_V4"}


def test_missing_file_error_is_clear(tmp_path: Path):
    missing = tmp_path / "missing.txt"
    result = run_cli("--file", str(missing))
    assert result.returncode != 0
    assert "missing file" in result.stderr.lower()
    assert "traceback" not in result.stderr.lower()


def test_invalid_input_returns_nonzero():
    result = run_cli("--input", "!bad_v4")
    assert result.returncode != 0
    assert "invalid input" in result.stderr.lower()


def test_json_error_is_valid_and_nonzero():
    result = run_cli("--input", "!bad_v4", "--json")
    assert result.returncode != 0
    assert json.loads(result.stdout)["error"] == "invalid input"
