from ds_trainer.models import Difficulty, Domain, ExerciseType, Question

QUESTIONS: list[Question] = [
    # ── Easy ──────────────────────────────────────────────────────────────
    Question(
        id="alg_e_001",
        domain=Domain.ALGORITHMS,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt="Complete the function that returns True if a string is a palindrome, False otherwise. Ignore case.",
        code_template="""\
def is_palindrome(s: str) -> bool:
    \"\"\"Return True if s is a palindrome (case-insensitive).\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
def is_palindrome(s: str) -> bool:
    s = s.lower()
    return s == s[::-1]
""",
        test_cases=[
            {"function": "is_palindrome", "args": ["racecar"], "expected": True},
            {"function": "is_palindrome", "args": ["Racecar"], "expected": True},
            {"function": "is_palindrome", "args": ["hello"], "expected": False},
            {"function": "is_palindrome", "args": [""], "expected": True},
        ],
        explanation="Lowercase then compare string to its reverse. s[::-1] reverses in O(n).",
        hints=["Use slicing to reverse: s[::-1]"],
        tags=["strings", "easy"],
    ),
    Question(
        id="alg_e_002",
        domain=Domain.ALGORITHMS,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that returns the n-th Fibonacci number (0-indexed: "
            "fib(0)=0, fib(1)=1, fib(2)=1, fib(3)=2, ...)."
        ),
        code_template="""\
def fib(n: int) -> int:
    \"\"\"Return the n-th Fibonacci number (iterative, O(n) time, O(1) space).\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
def fib(n: int) -> int:
    if n <= 0:
        return 0
    a, b = 0, 1
    for _ in range(1, n):
        a, b = b, a + b
    return b
""",
        test_cases=[
            {"function": "fib", "args": [0], "expected": 0},
            {"function": "fib", "args": [1], "expected": 1},
            {"function": "fib", "args": [6], "expected": 8},
            {"function": "fib", "args": [10], "expected": 55},
        ],
        explanation="Iterative Fibonacci: track two consecutive values. O(n) time, O(1) space.",
        hints=["Avoid recursion — use two variables and iterate."],
        tags=["dynamic-programming", "easy"],
    ),
    Question(
        id="alg_e_003",
        domain=Domain.ALGORITHMS,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt="What is the time complexity of searching for an element in an unsorted list of n elements?",
        choices=["O(log n)", "O(1)", "O(n)", "O(n log n)"],
        answer_index=2,
        explanation=(
            "Without sorting or a hash structure, you must check each element in the worst case "
            "(element not present or at the end) — O(n) linear scan. "
            "Binary search is O(log n) but requires a sorted list."
        ),
        hints=["What's the worst case — how many elements might you check?"],
        tags=["complexity", "search"],
    ),
    # ── Medium ─────────────────────────────────────────────────────────────
    Question(
        id="alg_m_001",
        domain=Domain.ALGORITHMS,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that finds two numbers in a list that add up to a target. "
            "Return their indices as a tuple. Assume exactly one solution exists."
        ),
        code_template="""\
def two_sum(nums: list[int], target: int) -> tuple[int, int]:
    \"\"\"Return (i, j) such that nums[i] + nums[j] == target (i != j).\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
def two_sum(nums: list[int], target: int) -> tuple[int, int]:
    seen = {}
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return (seen[complement], i)
        seen[n] = i
    raise ValueError("No solution found")
""",
        test_cases=[
            {"function": "two_sum", "args": [[2, 7, 11, 15], 9], "expected": (0, 1)},
            {"function": "two_sum", "args": [[3, 2, 4], 6], "expected": (1, 2)},
            {"function": "two_sum", "args": [[3, 3], 6], "expected": (0, 1)},
        ],
        explanation=(
            "Hash map approach: for each number, check if its complement (target - num) "
            "is already in the map. O(n) time, O(n) space."
        ),
        hints=[
            "For each element, ask: 'have I seen target - element before?'",
            "Use a dict to store {value: index} as you iterate.",
        ],
        tags=["hash-map", "arrays", "medium"],
    ),
    Question(
        id="alg_m_002",
        domain=Domain.ALGORITHMS,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that groups anagrams together from a list of strings. "
            "Return a list of groups; order within groups and between groups doesn't matter."
        ),
        code_template="""\
from collections import defaultdict

def group_anagrams(strs: list[str]) -> list[list[str]]:
    \"\"\"Group strings that are anagrams of each other.\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
from collections import defaultdict

def group_anagrams(strs: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))
        groups[key].append(s)
    return list(groups.values())
""",
        test_cases=[
            {
                "function": "group_anagrams",
                "args": [["eat", "tea", "tan", "ate", "nat", "bat"]],
                "expected": [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]],
            }
        ],
        explanation=(
            "Sort each string's characters to create a canonical key. "
            "Anagrams share the same sorted key — group them with a defaultdict."
        ),
        hints=[
            "Two words are anagrams if sorting their characters gives the same result.",
            "Use sorted(s) as a dict key.",
        ],
        tags=["hash-map", "strings", "medium"],
    ),
    Question(
        id="alg_m_003",
        domain=Domain.ALGORITHMS,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "What is the time complexity of binary search on a sorted array of n elements?"
        ),
        choices=["O(n)", "O(n log n)", "O(log n)", "O(1)"],
        answer_index=2,
        explanation=(
            "Binary search halves the search space at each step. "
            "After k steps, the remaining elements = n / 2^k. "
            "When n / 2^k = 1, k = log₂(n) → O(log n)."
        ),
        hints=["How many times can you halve n before reaching 1?"],
        tags=["binary-search", "complexity"],
    ),
    # ── Hard ───────────────────────────────────────────────────────────────
    Question(
        id="alg_h_001",
        domain=Domain.ALGORITHMS,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that finds the length of the longest substring "
            "without repeating characters (sliding window approach)."
        ),
        code_template="""\
def length_of_longest_substring(s: str) -> int:
    \"\"\"Return the length of the longest substring without repeating characters.\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
def length_of_longest_substring(s: str) -> int:
    char_index = {}
    left = 0
    best = 0
    for right, ch in enumerate(s):
        if ch in char_index and char_index[ch] >= left:
            left = char_index[ch] + 1
        char_index[ch] = right
        best = max(best, right - left + 1)
    return best
""",
        test_cases=[
            {"function": "length_of_longest_substring", "args": ["abcabcbb"], "expected": 3},
            {"function": "length_of_longest_substring", "args": ["bbbbb"], "expected": 1},
            {"function": "length_of_longest_substring", "args": ["pwwkew"], "expected": 3},
            {"function": "length_of_longest_substring", "args": [""], "expected": 0},
        ],
        explanation=(
            "Sliding window: expand right, shrink left when a repeat is found. "
            "Track last seen index of each character. O(n) time, O(min(n, alphabet)) space."
        ),
        hints=[
            "Use a dict mapping character → last seen index.",
            "When you see a repeat, move left pointer to right of the previous occurrence.",
        ],
        tags=["sliding-window", "strings", "hard"],
    ),
    Question(
        id="alg_h_002",
        domain=Domain.ALGORITHMS,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that returns the maximum profit from at most ONE buy-then-sell "
            "transaction on a list of stock prices. Return 0 if no profit is possible."
        ),
        code_template="""\
def max_profit(prices: list[int]) -> int:
    \"\"\"Return the max profit from one buy-low, sell-high transaction.\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
def max_profit(prices: list[int]) -> int:
    if not prices:
        return 0
    min_price = prices[0]
    best = 0
    for price in prices:
        best = max(best, price - min_price)
        min_price = min(min_price, price)
    return best
""",
        test_cases=[
            {"function": "max_profit", "args": [[7, 1, 5, 3, 6, 4]], "expected": 5},
            {"function": "max_profit", "args": [[7, 6, 4, 3, 1]], "expected": 0},
            {"function": "max_profit", "args": [[1]], "expected": 0},
        ],
        explanation=(
            "Track the minimum price seen so far and the best profit at each step. "
            "O(n) time, O(1) space — a single pass."
        ),
        hints=[
            "Track the minimum price seen so far.",
            "At each step, compute price - min_price and update the best profit.",
        ],
        tags=["dynamic-programming", "arrays", "hard"],
    ),
]
