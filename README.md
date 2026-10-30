# Cynbit Studio Skill Engine

**Live Demo:** https://cynbit-studio-skill-engine-1.onrender.com/

Adaptive code-evaluation and skill-tracking engine for Cynbit Studio (coding practice, AI code evaluation, career prep, job matching).

**Flow:** student code -> sandboxed test run -> Gemini rubric review -> Bayesian Knowledge Tracing updates per-skill mastery
-> next-problem recommendation + role-fit score -> mentor flag when AI and tests disagree (human-in-the-loop).

## Run (Windows, easiest)
Double-click `run_app.bat`. It creates the venv, installs, asks for your key, starts the server and opens the browser.

## Run (manual)
    python -m venv .venv && .venv\Scripts\activate      (Mac/Linux: source .venv/bin/activate)
    pip install -r requirements.txt
    copy .env.example .env     (add GEMINI_API_KEY; app still works without it, minus AI feedback)
    uvicorn app.main:app --reload
    open http://127.0.0.1:8000  (API docs at /docs)
    pytest -q

## Known limitations
Subprocess + rlimits + denylist is a demo-grade sandbox; production needs container isolation. State is in-memory.
