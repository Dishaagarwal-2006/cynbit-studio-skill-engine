"""Bayesian Knowledge Tracing (Corbett & Anderson, 1995) + recommender + role fit.
Hidden state per skill: P(learned). Each submission updates it using slip/guess/learn rates.
Partial credit: posterior is a pass-rate-weighted blend of the 'correct' and 'incorrect' posteriors."""
from dataclasses import dataclass
from .problems import PROBLEMS, ROLES, SKILLS

@dataclass(frozen=True)
class BKTParams:
    p_init: float = 0.30
    p_learn: float = 0.15
    p_slip: float = 0.10
    p_guess: float = 0.20

DEFAULT = BKTParams()

def update(p: float, pass_rate: float, prm: BKTParams = DEFAULT) -> float:
    s, g = prm.p_slip, prm.p_guess
    post_correct = p * (1 - s) / (p * (1 - s) + (1 - p) * g)
    post_wrong = p * s / (p * s + (1 - p) * (1 - g))
    post = pass_rate * post_correct + (1 - pass_rate) * post_wrong
    return post + (1 - post) * prm.p_learn

def new_mastery() -> dict:
    return {s: DEFAULT.p_init for s in SKILLS}

def role_fit(mastery: dict) -> dict:
    out = {}
    for role, w in ROLES.items():
        out[role] = round(100 * sum(w[s] * mastery[s] for s in w) / sum(w.values()), 1)
    return out

def recommend(mastery: dict, solved: set):
    """Pick the unsolved problem that targets weak skills at a difficulty matching current mastery."""
    pool = [p for p in PROBLEMS if p["id"] not in solved] or PROBLEMS
    avg = sum(mastery.values()) / len(mastery)
    target = 1 + round(2 * avg)
    def score(p):
        need = sum(1 - mastery[s] for s in p["skills"]) / len(p["skills"])
        return need - 0.3 * abs(p["difficulty"] - target)
    best = max(pool, key=score)
    weakest = min(best["skills"], key=lambda s: mastery[s])
    return {"problem_id": best["id"], "title": best["title"], "reason": f"Targets your weakest related skill: {weakest} ({mastery[weakest]:.0%} mastery)."}
