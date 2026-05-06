from ds_trainer.models import Difficulty, Domain, ExerciseType, Question

QUESTIONS: list[Question] = [
    # ── Easy ──────────────────────────────────────────────────────────────
    Question(
        id="prob_e_001",
        domain=Domain.PROBABILITY,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "A bag contains 3 red balls and 2 blue balls. You draw one at random. "
            "What is the probability of drawing a red ball?"
        ),
        choices=[
            "2/5",
            "3/5",
            "1/2",
            "3/2",
        ],
        answer_index=1,
        explanation=(
            "There are 3 red balls out of 5 total. P(red) = 3/5 = 0.6. "
            "3/2 > 1 so it cannot be a probability."
        ),
        hints=["Count favourable outcomes over total outcomes."],
        tags=["probability", "basics"],
    ),
    Question(
        id="prob_e_002",
        domain=Domain.PROBABILITY,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "A fair coin is flipped twice. What is the probability of getting heads both times?"
        ),
        choices=[
            "1/2",
            "1/3",
            "1/4",
            "3/4",
        ],
        answer_index=2,
        explanation=(
            "The flips are independent: P(HH) = P(H) × P(H) = 1/2 × 1/2 = 1/4. "
            "The sample space is {HH, HT, TH, TT} — 4 equally likely outcomes, only 1 is HH."
        ),
        hints=["Multiply the probabilities of independent events."],
        tags=["probability", "independence"],
    ),
    Question(
        id="prob_e_003",
        domain=Domain.PROBABILITY,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "A fair six-sided die is rolled once. What is the probability of NOT rolling a 1?"
        ),
        choices=[
            "5/6",
            "1/6",
            "4/6",
            "1/2",
        ],
        answer_index=0,
        explanation=(
            "P(not 1) = 1 − P(1) = 1 − 1/6 = 5/6. "
            "The five favourable outcomes are {2, 3, 4, 5, 6}."
        ),
        hints=["Use the complement rule: P(not A) = 1 − P(A)."],
        tags=["probability", "complement"],
    ),
    # ── Medium ─────────────────────────────────────────────────────────────
    Question(
        id="prob_m_001",
        domain=Domain.PROBABILITY,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "A disease affects 1% of the population. A diagnostic test has 99% sensitivity "
            "(correctly identifies 99% of sick people) and 99% specificity (correctly identifies "
            "99% of healthy people). A randomly chosen person tests positive. "
            "What is the approximate probability they actually have the disease?"
        ),
        choices=[
            "~1%",
            "~50%",
            "~99%",
            "~90%",
        ],
        answer_index=1,
        explanation=(
            "Apply Bayes' theorem. P(D) = 0.01, P(+|D) = 0.99, P(+|no D) = 0.01.\n"
            "P(+) = P(+|D)·P(D) + P(+|no D)·P(no D)\n"
            "     = 0.99×0.01 + 0.01×0.99 = 0.0099 + 0.0099 = 0.0198\n"
            "P(D|+) = P(+|D)·P(D) / P(+) = 0.0099 / 0.0198 ≈ 50%\n\n"
            "Despite 99% accuracy, only ~50% of positives are true positives because the disease "
            "is rare. Healthy people vastly outnumber sick people, so even a 1% false-positive rate "
            "generates as many false alarms as true positives. This is the base-rate fallacy."
        ),
        hints=[
            "Use Bayes' theorem: P(D|+) = P(+|D)·P(D) / P(+).",
            "P(+) has two components: true positives and false positives.",
            "With 1% prevalence, healthy people outnumber sick people 99:1.",
        ],
        tags=["probability", "bayes", "base-rate"],
    ),
    Question(
        id="prob_m_002",
        domain=Domain.PROBABILITY,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "You pay $1 to roll a fair six-sided die. You win $5 if you roll a 6, "
            "and nothing otherwise. What is your expected profit per game?"
        ),
        choices=[
            "+$0.17",
            "−$0.17",
            "+$0.83",
            "$0 (fair game)",
        ],
        answer_index=1,
        explanation=(
            "E[winnings] = 5 × (1/6) + 0 × (5/6) = 5/6 ≈ $0.833\n"
            "E[profit] = E[winnings] − cost = 5/6 − 1 = −1/6 ≈ −$0.167\n\n"
            "You lose about 17 cents per game on average — negative expected value for the player. "
            "This is how casinos design games."
        ),
        hints=[
            "E[X] = Σ x · P(x) for all outcomes.",
            "Don't forget to subtract the $1 entry cost.",
        ],
        tags=["probability", "expected-value"],
    ),
    Question(
        id="prob_m_003",
        domain=Domain.PROBABILITY,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "P(A) = 0.3, P(B) = 0.4, and P(A ∩ B) = 0.12. Are events A and B independent?"
        ),
        choices=[
            "No — P(A ∩ B) ≠ 0, so they must be dependent",
            "Yes — P(A ∩ B) = P(A) · P(B)",
            "Cannot be determined without more information",
            "No — independent events can never co-occur",
        ],
        answer_index=1,
        explanation=(
            "Two events are independent iff P(A ∩ B) = P(A) · P(B).\n"
            "P(A) · P(B) = 0.3 × 0.4 = 0.12 = P(A ∩ B). ✓\n\n"
            "Independence does NOT mean mutual exclusivity. Mutually exclusive events "
            "(P(A ∩ B) = 0) are actually dependent unless one has probability 0."
        ),
        hints=["The definition of independence: P(A ∩ B) = P(A) · P(B)."],
        tags=["probability", "independence"],
    ),
    Question(
        id="prob_m_004",
        domain=Domain.PROBABILITY,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "Explain the Monty Hall problem. You pick door 1; the host opens door 3 revealing a goat. "
            "Should you switch to door 2 or stay with door 1? Justify your answer."
        ),
        model_answer=(
            "You should switch. Switching wins 2/3 of the time; staying wins only 1/3.\n\n"
            "Why:\n"
            "- At the start: P(car behind door 1) = 1/3, P(car behind doors 2 or 3) = 2/3.\n"
            "- The host always opens a losing door he knows is a goat. His action is not random — "
            "it transfers all 2/3 probability onto the one remaining unchosen door.\n"
            "- After the reveal: P(car behind door 2) = 2/3, P(car behind door 1) = 1/3.\n\n"
            "Why people get it wrong:\n"
            "They assume 2 doors remaining means 50/50. But the host's informed choice carries "
            "information that updates the probabilities asymmetrically.\n\n"
            "Simulation check: over 10,000 games, switchers win ~6,667 times (~67%)."
        ),
        explanation=(
            "The host's non-random door reveal concentrates the 2/3 probability onto the "
            "unchosen door. Switching doubles your win rate from 1/3 to 2/3."
        ),
        hints=[
            "What were the probabilities before the host acted?",
            "The host never opens your door, and never reveals the car.",
        ],
        tags=["probability", "conditional-probability", "monty-hall"],
    ),
    # ── Hard ───────────────────────────────────────────────────────────────
    Question(
        id="prob_h_001",
        domain=Domain.PROBABILITY,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "What is the expected number of fair coin flips required to get two heads in a row (HH)? "
            "Derive the answer using a system of equations."
        ),
        model_answer=(
            "Answer: 6 flips.\n\n"
            "Define two states:\n"
            "  E  = expected flips to reach HH from the start (no useful prior flip)\n"
            "  Eₕ = expected additional flips when the last flip was H\n\n"
            "From state E:\n"
            "  - Heads (prob 1/2) → move to state Eₕ\n"
            "  - Tails (prob 1/2) → back to state E\n"
            "  E = 1 + (1/2)·Eₕ + (1/2)·E\n\n"
            "From state Eₕ:\n"
            "  - Heads (prob 1/2) → done (0 more flips)\n"
            "  - Tails (prob 1/2) → back to state E\n"
            "  Eₕ = 1 + (1/2)·0 + (1/2)·E\n\n"
            "Solving:\n"
            "  From the E equation: (1/2)·E = 1 + (1/2)·Eₕ  →  E = 2 + Eₕ\n"
            "  Substituting Eₕ = 1 + (1/2)·E:\n"
            "    E = 2 + 1 + (1/2)·E = 3 + (1/2)·E\n"
            "    (1/2)·E = 3  →  E = 6"
        ),
        explanation=(
            "Model as a Markov chain with states {start, one-H, done}. "
            "Solve the two-equation linear system to get E = 6."
        ),
        hints=[
            "Define states based on the current run of heads.",
            "Write one equation per state: E[flips] = 1 + weighted sum of next states.",
            "You get two equations in two unknowns.",
        ],
        tags=["probability", "expected-value", "markov-chain"],
    ),
    Question(
        id="prob_h_002",
        domain=Domain.PROBABILITY,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "In a room of 23 people, what is the approximate probability that at least two people "
            "share a birthday? (Assume 365 days, uniform distribution, no leap years.)"
        ),
        choices=[
            "~10%",
            "~30%",
            "~50%",
            "~75%",
        ],
        answer_index=2,
        explanation=(
            "Compute via the complement: P(no shared birthday among 23 people).\n"
            "P(no match) = (365/365) × (364/365) × … × (343/365) ≈ 0.493\n"
            "P(at least one match) = 1 − 0.493 ≈ 50.7%\n\n"
            "Poisson approximation: expected matching pairs = C(23,2)/365 = 253/365 ≈ 0.693.\n"
            "P(≥1 match) ≈ 1 − e⁻⁰·⁶⁹³ ≈ 50%.\n\n"
            "The result surprises most people. The key: you're counting pairs (253 of them), "
            "not individuals. You only need one pair to match."
        ),
        hints=[
            "Calculate P(no shared birthday) first, then take the complement.",
            "How many pairs of people exist in a group of 23?",
        ],
        tags=["probability", "birthday-problem", "combinatorics"],
    ),
    Question(
        id="prob_h_003",
        domain=Domain.PROBABILITY,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "State the law of total expectation. Then apply it: a company has two customer segments — "
            "60% are 'casual' (average spend $20) and 40% are 'premium' (average spend $80). "
            "What is the expected spend of a randomly chosen customer?"
        ),
        model_answer=(
            "Law of total expectation:\n"
            "  E[X] = Σₛ E[X | Y=s] · P(Y=s)\n"
            "The overall expectation equals the weighted average of conditional expectations, "
            "weighted by the probability of each condition.\n\n"
            "Applying it:\n"
            "  E[spend] = E[spend | casual] · P(casual) + E[spend | premium] · P(premium)\n"
            "           = 20 × 0.6 + 80 × 0.4\n"
            "           = 12 + 32 = $44\n\n"
            "Why it matters for data science:\n"
            "  - Segment-level metrics roll up to global metrics via this law.\n"
            "  - Simpson's paradox occurs when segment weights shift and the naive "
            "    aggregate becomes misleading.\n"
            "  - Used in hierarchical/mixed-effects models and in deriving the "
            "    bias-variance decomposition."
        ),
        explanation=(
            "E[X] = Σ E[X|Y=y]·P(Y=y). Here: 20×0.6 + 80×0.4 = $44. "
            "Underlies segment rollups and is why Simpson's paradox occurs."
        ),
        hints=[
            "Break E[spend] into conditional expectations, one per segment.",
            "Weight each by the probability of that segment.",
        ],
        tags=["probability", "total-expectation", "law-of-expectation"],
    ),
]
