import os
from pathlib import Path
from collections import defaultdict
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from . import bkt, feedback
from .problems import BY_ID, PROBLEMS, SKILLS, public_view
from .runner import run_submission

app = FastAPI(title="Cynbit Studio Skill Engine", version="0.1.0")
INDEX = Path(__file__).parent / "static" / "index.html"  # absolute path: works from any folder
STORE = defaultdict(lambda: {"mastery": bkt.new_mastery(), "history": [], "solved": set()})

class Submission(BaseModel):
    learner_id: str = Field(min_length=1, max_length=40)
    problem_id: str
    code: str = Field(max_length=5000)

def _profile(lid: str) -> dict:
    s = STORE[lid]
    m = {k: round(v, 3) for k, v in s["mastery"].items()}
    return {"learner_id": lid, "mastery": m, "role_fit": bkt.role_fit(s["mastery"]),
            "solved": sorted(s["solved"]), "history": s["history"][-20:],
            "next": bkt.recommend(s["mastery"], s["solved"])}

@app.get("/", include_in_schema=False)
def index():
    if not INDEX.exists():
        raise HTTPException(500, f"Frontend file missing. Expected at: {INDEX}")
    return FileResponse(INDEX)

@app.get("/api/health")
def health():
    return {"ok": True, "llm_enabled": bool(os.getenv("GEMINI_API_KEY")), "skills": SKILLS}

@app.get("/api/problems")
def problems():
    return [public_view(p) for p in PROBLEMS]

@app.get("/api/problems/{pid}")
def problem(pid: str):
    if pid not in BY_ID:
        raise HTTPException(404, "Unknown problem")
    return public_view(BY_ID[pid])

@app.get("/api/learner/{lid}")
def learner(lid: str):
    return _profile(lid)

@app.delete("/api/learner/{lid}")
def reset(lid: str):
    STORE.pop(lid, None)
    return _profile(lid)

@app.post("/api/submit")
def submit(sub: Submission):  # sync def -> runs in threadpool, so the subprocess never blocks the event loop
    p = BY_ID.get(sub.problem_id)
    if not p:
        raise HTTPException(404, "Unknown problem")
    run = run_submission(p, sub.code)
    fb = feedback.review(p, sub.code, run)
    st = STORE[sub.learner_id]
    before = dict(st["mastery"])
    for sk in p["skills"]:
        st["mastery"][sk] = bkt.update(st["mastery"][sk], run["pass_rate"])
    if run["all_passed"]:
        st["solved"].add(p["id"])
    st["history"].append({"problem": p["id"], "passed": run["passed"], "total": run["total"]})
    prof = _profile(sub.learner_id)
    prof["delta"] = {k: round(st["mastery"][k] - before[k], 3) for k in p["skills"]}
    return {"run": run, "feedback": fb.model_dump() if fb else None,
            "mentor_flag": feedback.mentor_flag(run, fb), "profile": prof}
