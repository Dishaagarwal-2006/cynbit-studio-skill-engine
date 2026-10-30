"""Runs submitted code against a problem's tests in a separate, time-limited process.
NOTE: a denylist + subprocess + rlimits is defence-in-depth for a demo, NOT a full sandbox.
Production would use containers (gVisor/Firecracker) with no network."""
import json, os, re, subprocess, sys, tempfile, time
from .problems import VISIBLE_TESTS

TIMEOUT_S = 6
BLOCKED = re.compile(
    r"\b(import|from)\s+(os|sys|subprocess|socket|shutil|pathlib|ctypes|requests|urllib|http|importlib|builtins|multiprocessing|threading)\b"
    r"|__import__|\bopen\s*\(|\beval\s*\(|\bexec\s*\(|\bcompile\s*\(|__builtins__|__subclasses__|__globals__|\binput\s*\(")

HARNESS = r'''
import sys, json, os
real = sys.stdout
sys.stdout = open(os.devnull, "w")
def emit(d):
    real.write(json.dumps(d) + "\n"); real.flush()
payload = json.loads(sys.stdin.read())
ns = {}
try:
    exec(compile(payload["code"], "<submission>", "exec"), ns)
    fn = ns[payload["fn"]]
except BaseException as e:
    emit({"i": -1, "error": type(e).__name__ + ": " + str(e)[:150]}); sys.exit(0)
for i, t in enumerate(payload["tests"]):
    try:
        out = json.loads(json.dumps(fn(*t["args"])))
        emit({"i": i, "ok": out == t["expected"], "got": repr(out)[:80]})
    except BaseException as e:
        emit({"i": i, "ok": False, "got": (type(e).__name__ + ": " + str(e))[:80]})
'''

def _limits():
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
        resource.setrlimit(resource.RLIMIT_CPU, (TIMEOUT_S + 1, TIMEOUT_S + 1))
    except Exception:
        pass

def run_submission(problem: dict, code: str) -> dict:
    tests, total = problem["tests"], len(problem["tests"])
    if BLOCKED.search(code):
        return _result(problem, [], total, error="Blocked: your code uses a restricted import/builtin.")
    payload = json.dumps({"code": code, "fn": problem["fn"], "tests": tests})
    env = {"PATH": os.environ.get("PATH", ""), "SYSTEMROOT": os.environ.get("SYSTEMROOT", "")}
    kwargs = {"preexec_fn": _limits} if os.name == "posix" else {}
    start, timed_out, stdout = time.time(), False, ""
    with tempfile.TemporaryDirectory() as tmp:
        try:
            proc = subprocess.run([sys.executable, "-I", "-c", HARNESS], input=payload, capture_output=True,
                                  text=True, timeout=TIMEOUT_S, cwd=tmp, env=env, **kwargs)
            stdout = proc.stdout
        except subprocess.TimeoutExpired as e:
            timed_out = True
            stdout = (e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout) or ""
    lines = [json.loads(l) for l in stdout.splitlines() if l.startswith("{")]
    err = next((l["error"] for l in lines if l.get("i") == -1), None)
    res = _result(problem, [l for l in lines if l.get("i", -1) >= 0], total, error=err, timed_out=timed_out)
    res["runtime_ms"] = int((time.time() - start) * 1000)
    return res

def _result(problem, lines, total, error=None, timed_out=False):
    by_i = {l["i"]: l for l in lines}
    details = []
    for i in range(total):
        l = by_i.get(i)
        d = {"i": i, "ok": bool(l and l["ok"]), "visible": i < VISIBLE_TESTS,
             "got": l["got"] if l else ("timeout" if timed_out else "not run")}
        if i < VISIBLE_TESTS:
            d["args"], d["expected"] = problem["tests"][i]["args"], problem["tests"][i]["expected"]
        else:
            d.pop("got")
        details.append(d)
    passed = sum(d["ok"] for d in details)
    return {"passed": passed, "total": total, "pass_rate": passed / total, "all_passed": passed == total,
            "timed_out": timed_out, "error": error, "details": details, "runtime_ms": 0}
