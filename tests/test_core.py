from fastapi.testclient import TestClient
from app import bkt
from app.main import app
from app.problems import BY_ID
from app.runner import run_submission

GOOD = {"two-sum": "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i\n",
        "fibonacci": "def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n"}
SLOW_FIB = "def fib(n):\n    return n if n < 2 else fib(n-1) + fib(n-2)\n"

def test_bkt_rises_on_success_and_falls_on_failure():
    p = 0.3
    for _ in range(5):
        p2 = bkt.update(p, 1.0); assert p2 > p; p = p2
    assert bkt.update(0.5, 0.0) < bkt.update(0.5, 1.0)
    assert 0 < bkt.update(0.01, 0.0) < 1

def test_bkt_converges_for_consistent_learner():
    p = 0.3
    for _ in range(10): p = bkt.update(p, 1.0)
    assert p > 0.95

def test_correct_solutions_pass():
    for pid, code in GOOD.items():
        assert run_submission(BY_ID[pid], code)["all_passed"], pid

def test_wrong_solution_fails():
    r = run_submission(BY_ID["two-sum"], "def two_sum(nums, target):\n    return [0, 0]\n")
    assert not r["all_passed"] and r["passed"] == 0

def test_inefficient_solution_times_out():
    r = run_submission(BY_ID["fibonacci"], SLOW_FIB)
    assert r["timed_out"] and 0 < r["passed"] < r["total"]

def test_infinite_loop_is_killed():
    r = run_submission(BY_ID["fibonacci"], "def fib(n):\n    while True: pass\n")
    assert r["timed_out"] and r["passed"] == 0

def test_dangerous_code_blocked():
    for bad in ["import os\ndef fib(n):\n    return 0\n", "def fib(n):\n    return open('x').read()\n"]:
        assert "Blocked" in run_submission(BY_ID["fibonacci"], bad)["error"]

def test_hidden_tests_not_leaked():
    d = run_submission(BY_ID["two-sum"], GOOD["two-sum"])["details"]
    assert "args" in d[0] and "args" not in d[-1]

def test_api_end_to_end():
    c = TestClient(app)
    c.delete("/api/learner/t1")
    r = c.post("/api/submit", json={"learner_id": "t1", "problem_id": "two-sum", "code": GOOD["two-sum"]}).json()
    assert r["run"]["all_passed"] and r["profile"]["mastery"]["hashing"] > 0.3
    assert "two-sum" in r["profile"]["solved"] and r["profile"]["next"]["problem_id"] != "two-sum"
    assert c.get("/api/problems").status_code == 200

def test_homepage_served():
    r = TestClient(app).get("/")
    assert r.status_code == 200 and "Skill Engine" in r.text
