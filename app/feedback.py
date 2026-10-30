"""Gemini rubric review. Degrades gracefully (returns None) if no API key / API error."""
import json, os
from functools import lru_cache
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

class Rubric(BaseModel):
    correctness: int = Field(description="1-5")
    efficiency: int = Field(description="1-5")
    readability: int = Field(description="1-5")
    edge_cases: int = Field(description="1-5")

class Feedback(BaseModel):
    summary: str
    strengths: List[str]
    improvements: List[str]
    time_complexity: str
    hint: str = Field(description="One nudge toward the fix. Never a full solution.")
    rubric: Rubric

SYSTEM = ("You are a kind, rigorous coding mentor inside Cynbit Studio. Judge the student's code using the problem, "
          "the code and the test results. Be specific and brief. NEVER write the full solution; give hints. "
          "Score honestly on 1-5; do not inflate scores when tests fail.")

@lru_cache(maxsize=1)
def _client():
    """Keep ONE long-lived client. A temporary Client gets garbage-collected and closes its HTTP session."""
    from google import genai
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def review(problem: dict, code: str, run: dict) -> Optional[Feedback]:
    if not os.getenv("GEMINI_API_KEY"):
        return None
    try:
        from google.genai import types
        fails = [d for d in run["details"] if d["visible"] and not d["ok"]]
        prompt = (f"Problem: {problem['title']}\n{problem['statement']}\n\nStudent code:\n```python\n{code}\n```\n\n"
                  f"Tests passed: {run['passed']}/{run['total']} (hidden tests included). Timed out: {run['timed_out']}. "
                  f"Error: {run['error']}\nFailing visible tests: {json.dumps(fails)[:800]}")
        res = _client().models.generate_content(
            model=MODEL, contents=prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM, temperature=0.2,
                                               response_mime_type="application/json", response_schema=Feedback))
        return res.parsed or Feedback(**json.loads(res.text))
    except Exception as e:  # never let the LLM break a submission
        print("feedback error:", e)
        return None

def mentor_flag(run: dict, fb: Optional[Feedback]) -> Optional[str]:
    """Human-in-the-loop: flag disagreement between objective tests and the AI judge."""
    if not fb:
        return None
    if fb.rubric.correctness >= 4 and run["pass_rate"] < 0.5:
        return "AI judged the code as correct but most tests failed. Needs mentor review."
    if fb.rubric.correctness <= 2 and run["all_passed"]:
        return "All tests passed but AI judged correctness low. Needs mentor review."
    return None