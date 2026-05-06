from ds_trainer.models import Difficulty, Domain, ExerciseType, Question

QUESTIONS: list[Question] = [
    # ── Easy ──────────────────────────────────────────────────────────────
    Question(
        id="stat_e_001",
        domain=Domain.STATISTICS,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "A dataset has values [1, 2, 3, 4, 100]. Which measure of central tendency "
            "is MOST resistant to the outlier (100)?"
        ),
        choices=["Mean", "Median", "Mode", "Range"],
        answer_index=1,
        explanation=(
            "The median is the middle value when sorted — it is not affected by extreme values. "
            "Mean = 22 (pulled up by 100), median = 3 (unchanged by the outlier's magnitude). "
            "Range and mode are not measures of central tendency."
        ),
        hints=["Which measure depends on actual values vs. just position?"],
        tags=["central-tendency", "outliers"],
    ),
    Question(
        id="stat_e_002",
        domain=Domain.STATISTICS,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "What does a p-value of 0.03 mean in the context of hypothesis testing "
            "with significance level α = 0.05?"
        ),
        choices=[
            "There is a 3% chance the null hypothesis is true",
            "There is a 3% probability of observing data at least as extreme if H₀ is true",
            "The effect size is 97% statistically significant",
            "The null hypothesis is false with 97% certainty",
        ],
        answer_index=1,
        explanation=(
            "The p-value is the probability of obtaining results at least as extreme as the "
            "observed data, assuming H₀ is true. p=0.03 < α=0.05 → reject H₀. "
            "It does NOT tell you the probability that H₀ is true."
        ),
        hints=["p-value is a probability about the data, not about the hypothesis."],
        tags=["hypothesis-testing", "p-value"],
    ),
    Question(
        id="stat_e_003",
        domain=Domain.STATISTICS,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt="Explain the Central Limit Theorem (CLT) in plain English and state its key conditions.",
        model_answer=(
            "The Central Limit Theorem states that the distribution of the SAMPLE MEAN approaches "
            "a normal distribution as the sample size grows, regardless of the population's "
            "original distribution.\n\n"
            "Key conditions:\n"
            "1. Independent samples (observations don't influence each other).\n"
            "2. Identically distributed (same population each time).\n"
            "3. Finite mean and variance in the population.\n"
            "4. Sample size large enough (rule of thumb: n ≥ 30 for most distributions).\n\n"
            "Why it matters: it justifies using normal-distribution tools (z-tests, confidence "
            "intervals) even when the underlying data is not normal, as long as n is sufficient."
        ),
        explanation="CLT underlies most frequentist inference — t-tests, confidence intervals, etc.",
        hints=[
            "Focus on sample means (not individual observations).",
            "What happens as you take larger and larger samples?",
        ],
        tags=["clt", "sampling", "inference"],
    ),
    # ── Medium ─────────────────────────────────────────────────────────────
    Question(
        id="stat_m_001",
        domain=Domain.STATISTICS,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "A company runs an A/B test on a new checkout button color. "
            "After 2 weeks, p=0.04. The CEO wants to ship immediately. "
            "What questions should you ask before concluding the test is successful?"
        ),
        model_answer=(
            "Key questions before calling a winner:\n\n"
            "1. Was the test pre-registered? Were α, power, and minimum detectable effect set "
            "before the experiment started? Post-hoc significance can be inflated.\n"
            "2. Was the sample size reached? Stopping early inflates false positives (peeking problem).\n"
            "3. Is the effect practically significant? Statistical significance ≠ business significance. "
            "What is the actual lift? Is it worth engineering cost?\n"
            "4. Are there novelty effects? A new button color might see initial uplift that fades.\n"
            "5. Were there data quality issues? Segment imbalances, bot traffic, assignment bugs?\n"
            "6. Multiple comparisons: was this one of many tests run? Bonferroni correction needed?\n"
            "7. Are primary and guardrail metrics healthy? Did conversion improve but revenue drop?\n\n"
            "Recommendation: only ship if the pre-defined stopping criterion was met, "
            "the effect is practically meaningful, and guardrail metrics are stable."
        ),
        explanation="A/B test validity requires pre-registration, sufficient sample, and practical significance.",
        hints=[
            "Think about early stopping, effect size, and multiple comparisons.",
        ],
        tags=["ab-testing", "experimental-design"],
    ),
    Question(
        id="stat_m_002",
        domain=Domain.STATISTICS,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that performs a two-sample t-test and returns whether the "
            "difference is significant at α=0.05, along with the p-value."
        ),
        code_template="""\
from scipy import stats

def two_sample_ttest(group_a: list[float], group_b: list[float]) -> tuple[bool, float]:
    \"\"\"Return (is_significant, p_value) for a two-sided t-test at alpha=0.05.\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
from scipy import stats

def two_sample_ttest(group_a: list[float], group_b: list[float]) -> tuple[bool, float]:
    t_stat, p_value = stats.ttest_ind(group_a, group_b)
    return p_value < 0.05, round(p_value, 6)
""",
        test_cases=[
            {
                "function": "two_sample_ttest",
                "args": [[10, 11, 12, 10, 11], [20, 21, 22, 20, 21]],
                "expected": (True, 0.000001),  # p << 0.05
            }
        ],
        explanation="scipy.stats.ttest_ind runs an independent two-sample t-test. p < 0.05 → reject H₀.",
        hints=[
            "Use scipy.stats.ttest_ind for independent samples.",
            "The function returns (t_statistic, p_value).",
        ],
        tags=["hypothesis-testing", "scipy", "t-test"],
    ),
    Question(
        id="stat_m_003",
        domain=Domain.STATISTICS,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "You are testing 20 different features for significance at α=0.05. "
            "Without any correction, what is the expected number of false positives?"
        ),
        choices=["0", "1", "5", "10"],
        answer_index=1,
        explanation=(
            "Expected false positives = number_of_tests × α = 20 × 0.05 = 1. "
            "This is why multiple comparisons corrections (Bonferroni, Benjamini-Hochberg) "
            "are essential — the family-wise error rate grows with the number of tests."
        ),
        hints=["Probability of a single false positive × number of tests."],
        tags=["multiple-comparisons", "hypothesis-testing"],
    ),
    Question(
        id="stat_m_004",
        domain=Domain.STATISTICS,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt="What is the difference between Type I and Type II errors in hypothesis testing?",
        choices=[
            "Type I: rejecting H₀ when it's false; Type II: failing to reject H₀ when it's true",
            "Type I: rejecting H₀ when it's true (false positive); Type II: failing to reject H₀ when it's false (false negative)",
            "Type I: low p-value error; Type II: high p-value error",
            "They are the same — both refer to incorrect rejections of H₀",
        ],
        answer_index=1,
        explanation=(
            "Type I error (α): false positive — you conclude an effect exists when it doesn't. "
            "Type II error (β): false negative — you miss a real effect. "
            "Power = 1 - β = probability of correctly detecting a true effect."
        ),
        hints=["Think about the medical testing analogy: false positive vs. false negative."],
        tags=["hypothesis-testing", "type-errors"],
    ),
    # ── Hard ───────────────────────────────────────────────────────────────
    Question(
        id="stat_h_001",
        domain=Domain.STATISTICS,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "Explain the bias-variance tradeoff. How does it manifest in model selection, "
            "and how do regularization techniques address it?"
        ),
        model_answer=(
            "The total prediction error of a model can be decomposed into:\n"
            "  Error = Bias² + Variance + Irreducible Noise\n\n"
            "Bias: error from incorrect assumptions in the learning algorithm. "
            "High bias → underfitting (model too simple to capture the signal).\n"
            "Variance: sensitivity to fluctuations in training data. "
            "High variance → overfitting (model too complex, memorizes noise).\n\n"
            "Manifestation in model selection:\n"
            "- A linear model on nonlinear data: high bias, low variance.\n"
            "- A deep decision tree on small data: low bias, high variance.\n"
            "- The goal is to find the sweet spot (e.g., via cross-validation).\n\n"
            "Regularization reduces variance by penalizing model complexity:\n"
            "- L2 (Ridge): adds λΣwᵢ² to loss → shrinks weights toward zero, keeps all features.\n"
            "- L1 (Lasso): adds λΣ|wᵢ| → induces sparsity (some weights go exactly to 0).\n"
            "- Dropout (neural nets): randomly zeroes neurons during training, reducing co-adaptation.\n"
            "- Early stopping: halts training before variance grows too large."
        ),
        explanation="Bias-variance is the fundamental tradeoff in supervised learning.",
        hints=[
            "Think about underfitting vs. overfitting.",
            "How does adding a penalty term to the loss function constrain a model?",
        ],
        tags=["bias-variance", "regularization", "ml"],
    ),
    Question(
        id="stat_h_002",
        domain=Domain.STATISTICS,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that bootstraps a 95% confidence interval for the mean "
            "of a sample using 1000 bootstrap iterations."
        ),
        code_template="""\
import numpy as np

def bootstrap_ci(data: list[float], n_iterations: int = 1000, seed: int = 42) -> tuple[float, float]:
    \"\"\"Return (lower_95, upper_95) bootstrap confidence interval for the mean.\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
import numpy as np

def bootstrap_ci(data: list[float], n_iterations: int = 1000, seed: int = 42) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    arr = np.array(data)
    boot_means = [rng.choice(arr, size=len(arr), replace=True).mean() for _ in range(n_iterations)]
    return (float(np.percentile(boot_means, 2.5)), float(np.percentile(boot_means, 97.5)))
""",
        test_cases=[
            {
                "function": "bootstrap_ci",
                "args": [[10, 12, 11, 13, 14, 10, 11, 12, 13, 15]],
                "expected": (10.7, 13.2),  # approximate; checked via isclose with tol
            }
        ],
        explanation=(
            "Bootstrap CI: sample with replacement n_iterations times, compute mean each time, "
            "take the 2.5th and 97.5th percentiles of the bootstrap distribution."
        ),
        hints=[
            "np.random.default_rng(seed).choice(arr, size=len(arr), replace=True) samples with replacement.",
            "np.percentile(boot_means, [2.5, 97.5]) extracts the CI bounds.",
        ],
        tags=["bootstrap", "confidence-interval", "numpy"],
    ),
    Question(
        id="stat_h_003",
        domain=Domain.STATISTICS,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "Explain the difference between correlation and causation. "
            "Give two examples of spurious correlation and describe two methods used to "
            "establish causal relationships."
        ),
        model_answer=(
            "Correlation measures the statistical association between two variables (−1 to +1). "
            "Causation means one variable directly influences the other.\n\n"
            "Correlation ≠ causation because:\n"
            "- Confounding: a third variable causes both (ice cream sales and drowning rates "
            "are correlated — both driven by summer temperature).\n"
            "- Reverse causality: the effect drives the cause.\n"
            "- Coincidence: spurious patterns in finite data.\n\n"
            "Spurious correlation examples:\n"
            "1. Nicolas Cage films per year correlates with pool drownings.\n"
            "2. Per capita cheese consumption correlates with deaths by bedsheet tangling.\n\n"
            "Methods to establish causality:\n"
            "1. Randomized Controlled Experiments (A/B tests): random assignment eliminates "
            "confounders by design — the gold standard.\n"
            "2. Quasi-experimental methods (difference-in-differences, instrumental variables, "
            "regression discontinuity): exploit natural variation when randomization is impossible."
        ),
        explanation="Causal inference requires more than correlation — design or method must control confounders.",
        hints=[
            "What is a confounder? How does randomization eliminate it?",
        ],
        tags=["causation", "correlation", "experimental-design"],
    ),
    # ── Take-home (hard) ───────────────────────────────────────────────────
    Question(
        id="stat_h_004",
        domain=Domain.STATISTICS,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.TAKE_HOME,
        prompt=(
            "A retail company wants to know if a new email campaign increased weekly purchases. "
            "You have transaction data for two groups (treatment/control) over 8 weeks "
            "(4 pre-campaign, 4 post-campaign)."
        ),
        project_spec=(
            "# Take-Home: Email Campaign Analysis\n\n"
            "## Business Question\n"
            "Did the email campaign (weeks 5-8) significantly increase weekly purchases "
            "in the treatment group vs. the control group?\n\n"
            "## Dataset\n"
            "Columns: user_id, week (1-8), group (treatment/control), purchases (int)\n\n"
            "## Tasks\n"
            "1. EDA: Plot purchases over time for each group. Check for pre-period imbalances.\n"
            "2. Difference-in-Differences: compute the DiD estimate manually.\n"
            "   DiD = (treatment_post - treatment_pre) - (control_post - control_pre)\n"
            "3. Statistical test: run a t-test comparing post-period purchases (treatment vs control).\n"
            "4. Visualize: bar chart of mean weekly purchases pre vs. post, by group.\n"
            "5. Write a 3-sentence executive summary with your conclusion.\n\n"
            "## Deliverable\n"
            "A Jupyter notebook (or Python script) with analysis + the executive summary."
        ),
        dataset_generator="email_campaign",
        explanation=(
            "Difference-in-differences is a quasi-experimental method that controls for "
            "pre-existing group differences by using the control group as a counterfactual."
        ),
        hints=[
            "Check parallel trends assumption: do treatment and control move together pre-campaign?",
        ],
        tags=["ab-testing", "difference-in-differences", "take-home"],
    ),
]
