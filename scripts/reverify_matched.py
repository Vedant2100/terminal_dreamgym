"""Usage: python scripts/reverify_matched.py [runs/matched_eval.jsonl]  (run from the repo root)

Independently re-score every run from its saved sandbox: rerun the target
command and the whole suite, recompute strict success, compare with the record."""
import json, shlex, subprocess, sys, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
tasks = {t["id"]: t for t in json.load(open("data/tasks.json"))}
recs = [json.loads(l) for l in open(sys.argv[1] if len(sys.argv) > 1 else "runs/matched_eval.jsonl")]
def run(cmd, cwd):
    args = shlex.split(cmd); args = [sys.executable, "-m", "pytest", *args[1:], "-p", "no:cacheprovider"]
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=60)
def outcomes(cwd):
    r = run("pytest -q -rA", cwd); o = {}
    for line in r.stdout.splitlines():
        m = re.match(r"^(PASSED|FAILED|ERROR) (\S+::\S+)", line)
        if m: o[m.group(2)] = m.group(1)
    return o
def check(r):
    d = Path(r["run_dir"])
    if not d.exists(): return ("missing", r)
    t = tasks[r["task_id"]]
    score = run(t["score_command"], d).returncode == 0
    tpl = outcomes(t["template_dir"]); now = outcomes(d)
    regress = [k for k, v in tpl.items() if v == "PASSED" and now.get(k) != "PASSED"]
    strict = score and not regress
    return ("ok" if strict == r["success"] and score == r["score_passed"] else "MISMATCH", r, strict, score, regress)
with ThreadPoolExecutor(16) as ex: res = list(ex.map(check, recs))
from collections import Counter
print(Counter(x[0] for x in res))
for x in res:
    if x[0] != "ok": print(x[0], x[1]["condition"], x[1]["task_id"], x[1]["success"], x[1:][1:] if len(x) > 2 else "")
