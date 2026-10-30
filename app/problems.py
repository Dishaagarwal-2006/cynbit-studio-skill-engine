"""Problem bank. Each problem lists the skills it exercises (used by the BKT model)."""

def _t(args, expected):
    return {"args": args, "expected": expected}

SKILLS = ["arrays", "strings", "hashing", "stacks", "recursion", "sorting", "dp"]

PROBLEMS = [
    {"id": "two-sum", "title": "Two Sum", "difficulty": 1, "skills": ["arrays", "hashing"], "fn": "two_sum",
     "statement": "Given a list of ints `nums` and an int `target`, return the indices [i, j] (i < j) of the two numbers that add up to `target`. Exactly one solution exists.",
     "starter": "def two_sum(nums, target):\n    pass\n",
     "tests": [_t([[2, 7, 11, 15], 9], [0, 1]), _t([[3, 2, 4], 6], [1, 2]), _t([[3, 3], 6], [0, 1]),
               _t([[-1, -2, -3, -4, -5], -8], [2, 4]), _t([list(range(20000)), 39997], [19998, 19999])]},
    {"id": "reverse-words", "title": "Reverse Words", "difficulty": 1, "skills": ["strings"], "fn": "reverse_words",
     "statement": "Return the words of string `s` in reverse order, separated by a single space. Ignore extra spaces.",
     "starter": "def reverse_words(s):\n    pass\n",
     "tests": [_t(["the sky is blue"], "blue is sky the"), _t(["  hello   world "], "world hello"),
               _t(["a"], "a"), _t([""], ""), _t(["one two  three"], "three two one")]},
    {"id": "valid-parentheses", "title": "Valid Parentheses", "difficulty": 2, "skills": ["stacks", "strings"], "fn": "is_valid",
     "statement": "Given a string of brackets ()[]{}, return True if every bracket is closed in the correct order, else False.",
     "starter": "def is_valid(s):\n    pass\n",
     "tests": [_t(["()"], True), _t(["()[]{}"], True), _t(["(]"], False), _t(["([)]"], False),
               _t(["{[]}"], True), _t([""], True), _t(["(("], False), _t(["]"], False)]},
    {"id": "fibonacci", "title": "Fibonacci", "difficulty": 2, "skills": ["recursion", "dp"], "fn": "fib",
     "statement": "Return the n-th Fibonacci number (fib(0)=0, fib(1)=1). Your solution must handle n up to 40 quickly.",
     "starter": "def fib(n):\n    pass\n",
     "tests": [_t([0], 0), _t([1], 1), _t([10], 55), _t([30], 832040), _t([40], 102334155)]},
    {"id": "merge-sorted", "title": "Merge Sorted Lists", "difficulty": 2, "skills": ["arrays", "sorting"], "fn": "merge",
     "statement": "Merge two sorted lists `a` and `b` into one sorted list without using sort() on the result.",
     "starter": "def merge(a, b):\n    pass\n",
     "tests": [_t([[1, 3, 5], [2, 4, 6]], [1, 2, 3, 4, 5, 6]), _t([[], [1]], [1]), _t([[1, 1], [1]], [1, 1, 1]),
               _t([[-5, 0], [-3, 2, 9]], [-5, -3, 0, 2, 9]), _t([list(range(0, 20000, 2)), list(range(1, 20000, 2))], list(range(20000)))]},
    {"id": "max-subarray", "title": "Maximum Subarray", "difficulty": 3, "skills": ["arrays", "dp"], "fn": "max_subarray",
     "statement": "Return the largest sum of any contiguous, non-empty sub-list of `nums`.",
     "starter": "def max_subarray(nums):\n    pass\n",
     "tests": [_t([[-2, 1, -3, 4, -1, 2, 1, -5, 4]], 6), _t([[1]], 1), _t([[5, 4, -1, 7, 8]], 23),
               _t([[-3, -2, -1]], -1), _t([[1, -1] * 10000 + [5]], 5)]},
]

ROLES = {
    "Backend Intern": {"arrays": 1, "hashing": 1.5, "strings": 1, "stacks": 0.5, "recursion": 1, "sorting": 1, "dp": 1},
    "Data Intern": {"arrays": 1.5, "strings": 1, "hashing": 1, "stacks": 0.3, "recursion": 0.5, "sorting": 1.5, "dp": 0.7},
}

BY_ID = {p["id"]: p for p in PROBLEMS}
VISIBLE_TESTS = 2

def public_view(p):
    return {k: p[k] for k in ("id", "title", "difficulty", "skills", "statement", "starter")} | {
        "examples": p["tests"][:VISIBLE_TESTS]}
