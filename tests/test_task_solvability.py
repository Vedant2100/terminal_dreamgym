"""Every task must be solvable by an honest edit of the editable source files.

For each template we apply a reference fix (written by hand, never shown to the
agent) and require the whole suite to pass. This caught three dependency tests
whose expected strings were never updated for the _v2.._v5 variants (and the
Ada/Grace names in _v1), which made those tasks unsolvable without hard-coding.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

PYTHON_APP = '''import re


def normalize_email(email: str) -> str:
    return email.strip().lower()


def parse_price(value: str) -> float:
    return float(value.replace("$", "").replace(",", "").strip())


def parse_sku(value: str) -> str:
    return value


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
'''

CONFIG_APP = '''import json
import os
from pathlib import Path


class MissingRequiredConfig(RuntimeError):
    pass


def load_settings(path="config.json", env=None):
    env = os.environ if env is None else env
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    token = env.get("API_KEY") or (data.get("auth") or {}).get("token") or data.get("api_key")
    if not token:
        raise MissingRequiredConfig("api key is required")
    return {
        "timeout": int(data.get("request_timeout", data.get("timeout"))),
        "api_key": token,
        "region": data.get("region", "us-east-1"),
    }
'''

CLI_APP = '''import argparse
import json
import sys
from pathlib import Path


def process_input(text: str) -> str:
    if text.startswith("!"):
        raise ValueError("invalid input")
    return text.upper()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="")
    parser.add_argument("--file")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if args.file:
        try:
            data = Path(args.file).read_text(encoding="utf-8")
        except FileNotFoundError:
            print("error: missing file", file=sys.stderr)
            return 2
    else:
        data = args.input
    if data == "":
        return 0
    try:
        result = process_input(data)
    except ValueError as exc:
        if args.as_json:
            print(json.dumps({"error": str(exc)}))
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"result": result}) if args.as_json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

DEPENDENCY_APP = '''from package import format_order, format_user, parse_result


def render_user(name: str, email: str) -> str:
    return format_user({"name": name, "email": email})


def render_user_list(users):
    return [format_user(user) for user in users]


def render_order(order_id: str, total: float) -> str:
    return format_order({"id": order_id, "total": total})


def get_result_value(result):
    return parse_result(result["data"])
'''

REFERENCE = {
    "python_test_failure": ("app.py", PYTHON_APP),
    "config_env_failure": ("app.py", CONFIG_APP),
    "cli_edge_case": ("cli.py", CLI_APP),
    "dependency_mismatch": ("app.py", DEPENDENCY_APP),
}

TEMPLATES = sorted({task["template_dir"] for task in json.loads((ROOT / "data/tasks.json").read_text())})


@pytest.mark.parametrize("template", TEMPLATES)
def test_reference_fix_passes_whole_suite(template, tmp_path):
    family = Path(template).name.rsplit("_v", 1)[0]
    filename, source = REFERENCE[family]
    work = tmp_path / "repo"
    shutil.copytree(ROOT / template, work, ignore=shutil.ignore_patterns("__pycache__", "expected_fix.patch"))
    (work / filename).write_text(source, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=work, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout[-2000:]
