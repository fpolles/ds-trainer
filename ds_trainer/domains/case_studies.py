from ds_trainer.models import Difficulty, Domain, ExerciseType, Question

QUESTIONS: list[Question] = [
    # ── Easy ──────────────────────────────────────────────────────────────
    Question(
        id="cs_e_001",
        domain=Domain.CASE_STUDIES,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "A product manager asks you to define the 'North Star Metric' for a ride-sharing app. "
            "Which metric best captures long-term business health?"
        ),
        choices=[
            "Number of app downloads",
            "Completed rides per week",
            "Average driver rating",
            "Marketing spend efficiency (CAC)",
        ],
        answer_index=1,
        explanation=(
            "The North Star Metric captures the core value delivered. For a ride-sharing app, "
            "completed rides per week directly measures the primary value exchange (connecting "
            "riders and drivers). Downloads are vanity metrics; CAC is financial, not product."
        ),
        hints=["Which metric best represents value delivered to both sides of the marketplace?"],
        tags=["product-metrics", "north-star"],
    ),
    Question(
        id="cs_e_002",
        domain=Domain.CASE_STUDIES,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "A company wants to measure the impact of a new onboarding flow on user retention. "
            "Briefly describe the steps you would take to design and analyze this experiment."
        ),
        model_answer=(
            "Step 1 — Define metrics: primary metric (e.g., 7-day retention), guardrail metrics "
            "(signup completion rate, support tickets).\n\n"
            "Step 2 — Determine sample size: use a power calculation based on baseline retention, "
            "minimum detectable effect (e.g., +5%), α=0.05, power=0.80.\n\n"
            "Step 3 — Randomize: randomly assign new users to control (old flow) or treatment "
            "(new flow). Ensure assignment is at the user level.\n\n"
            "Step 4 — Run the experiment: let it run until the pre-calculated sample size is "
            "reached — don't peek and stop early.\n\n"
            "Step 5 — Analyze: run a two-sample test on 7-day retention rates. Check guardrail "
            "metrics. Segment by device, country if needed.\n\n"
            "Step 6 — Decide: ship if primary metric improves significantly, guardrails hold, "
            "and the effect is practically meaningful."
        ),
        explanation="A/B test design requires pre-specification of metrics, sample size, and stopping criteria.",
        hints=["Think about the full lifecycle: design → run → analyze → decide."],
        tags=["ab-testing", "experimental-design", "retention"],
    ),
    Question(
        id="cs_e_003",
        domain=Domain.CASE_STUDIES,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "You notice that DAU (Daily Active Users) dropped 15% yesterday. "
            "What is the FIRST thing you should check?"
        ),
        choices=[
            "Run a regression model to identify the causal factor",
            "Check for data pipeline or logging issues before assuming a real product change",
            "Alert the product team immediately that there is a crisis",
            "Compare to last week's numbers only",
        ],
        answer_index=1,
        explanation=(
            "Always rule out instrumentation/logging failures first. A data pipeline bug, "
            "timezone error, or tracking code issue can produce false metric drops. "
            "Only after confirming data quality should you investigate product/business causes."
        ),
        hints=["Is the drop real, or could it be a measurement artifact?"],
        tags=["metric-debugging", "data-quality"],
    ),
    # ── Medium ─────────────────────────────────────────────────────────────
    Question(
        id="cs_m_001",
        domain=Domain.CASE_STUDIES,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "Instagram's Stories feature shows a 20% decrease in friend acceptance rate "
            "after a new notification system was launched. How would you investigate "
            "whether the notification system caused this drop?"
        ),
        model_answer=(
            "Framework: rule out spurious causes → isolate causality → quantify impact.\n\n"
            "1. Data quality check: verify the acceptance rate metric itself. Any logging changes "
            "coinciding with the launch? Is the denominator (invitations sent) stable?\n\n"
            "2. Timing correlation: plot acceptance rate vs. launch date. Sudden drop at launch "
            "is consistent with causality (though not proof).\n\n"
            "3. Segmentation: does the drop affect all users or specific segments "
            "(mobile vs. desktop, notification permission granted vs. denied)? "
            "Users who can't see the notifications should be unaffected — this is a natural control.\n\n"
            "4. Notification analysis: look at notification open rates, acceptance rate conditional "
            "on opening vs. ignoring the notification.\n\n"
            "5. User surveys / qualitative: were notifications spammy? Did they arrive at bad times?\n\n"
            "6. If possible, run a holdback experiment: turn notifications off for a random subset "
            "and see if their acceptance rate recovers.\n\n"
            "Conclusion: if acceptance rate is lower only for users who received the new notifications, "
            "and recovers when notifications are disabled, causality is strongly supported."
        ),
        explanation="Metric investigations require ruling out instrumentation issues before attributing causality.",
        hints=[
            "Who acts as a natural control group (users unaffected by the change)?",
            "Does the drop happen at exactly the launch date?",
        ],
        tags=["metric-debugging", "causal-inference", "product-analytics"],
    ),
    Question(
        id="cs_m_002",
        domain=Domain.CASE_STUDIES,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "A food delivery app wants to predict customer churn. "
            "Walk through your end-to-end approach: from defining churn to deploying a model."
        ),
        model_answer=(
            "Step 1 — Define churn: business definition is critical. E.g., 'no order in 30 days' "
            "(for a weekly-use app) or '90 days' (monthly). Align with stakeholders.\n\n"
            "Step 2 — Label data: create a binary target variable. Snapshot at prediction time "
            "— avoid using future data (leakage).\n\n"
            "Step 3 — Feature engineering: recency (days since last order), frequency "
            "(orders per month), monetary value (avg order size), app engagement (sessions), "
            "support contacts, discount usage, delivery ratings.\n\n"
            "Step 4 — Model selection: start with logistic regression (interpretable baseline), "
            "then gradient boosting (XGBoost/LightGBM) for performance. "
            "Use time-based train/test split — not random — to prevent leakage.\n\n"
            "Step 5 — Evaluation: precision-recall curve and F1 (churn is often imbalanced). "
            "Business metric: cost of false negative (lost customer) vs. false positive (wasted retention offer).\n\n"
            "Step 6 — Deployment: score customers weekly, trigger retention campaigns for high-risk users. "
            "Monitor feature drift and model calibration. Retrain periodically."
        ),
        explanation="Churn prediction is a full ML lifecycle problem requiring careful definition, features, and evaluation.",
        hints=[
            "How do you define 'churned' — what's the time window?",
            "Why is a time-based train/test split critical here?",
        ],
        tags=["churn-prediction", "ml-lifecycle", "feature-engineering"],
    ),
    Question(
        id="cs_m_003",
        domain=Domain.CASE_STUDIES,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "You're building a recommendation system for an e-commerce site. "
            "The cold start problem means you have no interaction data for new users. "
            "What is the best initial approach?"
        ),
        choices=[
            "Train a collaborative filtering model on new users with empty history",
            "Use content-based recommendations based on item features and demographics",
            "Show no recommendations until the user has 10+ purchases",
            "Use the site-wide most popular items as a fallback",
        ],
        answer_index=3,
        explanation=(
            "For cold-start users, showing globally popular items is the simplest and often "
            "most effective baseline — it leverages collective wisdom without needing user history. "
            "Content-based (option B) is also valid but requires user feature data. "
            "Collaborative filtering (option A) fails without interaction history."
        ),
        hints=["What can you recommend when you know nothing about the user's preferences?"],
        tags=["recommendation-systems", "cold-start"],
    ),
    # ── Hard ───────────────────────────────────────────────────────────────
    Question(
        id="cs_h_001",
        domain=Domain.CASE_STUDIES,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "Airbnb wants to increase successful bookings in a specific city where demand is high "
            "but booking conversion is low. Describe a data-driven investigation and "
            "experiment you would run."
        ),
        model_answer=(
            "Phase 1 — Diagnose the funnel:\n"
            "Map the booking funnel: search → listing view → contact host → booking request → "
            "acceptance → completed stay. Measure conversion rate at each step. "
            "Identify the biggest drop-off. Is it listing views → request, or request → acceptance?\n\n"
            "Phase 2 — Segment and hypothesize:\n"
            "- Compare converting vs. non-converting users: price sensitivity, listing features, "
            "availability patterns, host response time, review count.\n"
            "- Identify whether supply (listings) or demand (searchers) is the bottleneck.\n\n"
            "Phase 3 — Form hypotheses and test:\n"
            "Hypothesis 1: hosts with <5 reviews have lower acceptance → test host onboarding incentives.\n"
            "Hypothesis 2: slow host response drives abandonment → test response time SLA reminders.\n"
            "Hypothesis 3: price mismatch → test dynamic pricing suggestions for hosts.\n\n"
            "Experiment design: randomize at the host level (for supply-side interventions) "
            "or user level (for demand-side). Primary metric: booking conversion rate in the city. "
            "Run for 4+ weeks for seasonal stability.\n\n"
            "Success criteria: statistically significant lift in conversion with no degradation in "
            "host satisfaction or review scores."
        ),
        explanation="Funnel analysis + segmentation reveals where to intervene; experiments confirm causality.",
        hints=[
            "Start with funnel analysis — where exactly do users drop off?",
            "Is this a supply or demand problem?",
        ],
        tags=["case-study", "funnel-analysis", "marketplace"],
    ),
    Question(
        id="cs_h_002",
        domain=Domain.CASE_STUDIES,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.TAKE_HOME,
        prompt=(
            "You are given a dataset of customer transactions for an online retailer. "
            "Build an RFM (Recency, Frequency, Monetary) segmentation model."
        ),
        project_spec=(
            "# Take-Home: RFM Customer Segmentation\n\n"
            "## Business Question\n"
            "Segment customers into meaningful groups based on their purchase behavior "
            "to enable targeted marketing campaigns.\n\n"
            "## Dataset\n"
            "Columns: customer_id, order_date, order_value\n"
            "Reference date for recency: 2024-04-01\n\n"
            "## Tasks\n"
            "1. Compute RFM metrics per customer:\n"
            "   - Recency: days since last purchase (lower = better)\n"
            "   - Frequency: number of purchases\n"
            "   - Monetary: total spend\n\n"
            "2. Score each metric 1-5 using quintiles (5 = best).\n\n"
            "3. Create segments based on RFM scores:\n"
            "   - Champions (R≥4, F≥4, M≥4)\n"
            "   - At Risk (R≤2, F≥3)\n"
            "   - Lost (R=1, F≤2)\n"
            "   - Others\n\n"
            "4. Visualize: bar chart of segment sizes and average order value per segment.\n\n"
            "5. Write a business recommendation: which segment to prioritize and why?\n\n"
            "## Deliverable\n"
            "A Jupyter notebook or Python script with analysis + 3-sentence recommendation."
        ),
        dataset_generator="rfm_transactions",
        explanation=(
            "RFM segmentation is a classic data science task used in CRM and marketing analytics. "
            "It requires feature engineering, binning/scoring, and business interpretation."
        ),
        hints=[
            "Use pd.qcut for quintile scoring.",
            "pd.Timestamp('2024-04-01') - df['order_date'] gives timedelta for recency.",
        ],
        tags=["rfm", "customer-segmentation", "take-home"],
    ),
    Question(
        id="cs_h_003",
        domain=Domain.CASE_STUDIES,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "Twitter wants to assess the effectiveness of its ad product. "
            "Design an experiment to measure whether Twitter ads increase brand purchase intent. "
            "Address measurement challenges specific to advertising experiments."
        ),
        model_answer=(
            "Challenge: users who see ads are self-selected (they were targeted) — "
            "simple before/after or ad-viewers vs. non-viewers comparisons are biased.\n\n"
            "Design — Ghost Ad / Holdout Experiment:\n"
            "1. Take the target audience pool.\n"
            "2. Randomly assign ~80% to see the real ad (treatment), ~20% to see a 'ghost' ad "
            "(same targeting, but ad slot shows an unrelated PSA instead).\n"
            "3. Both groups are in the auction, eliminating selection bias.\n\n"
            "Metrics:\n"
            "- Primary: brand lift survey (purchase intent, aided awareness) — shown to random "
            "samples from each group after exposure.\n"
            "- Secondary: click-through rate, website visits, in-store visits (if available).\n\n"
            "Measurement challenges:\n"
            "- Attribution window: how long after exposure to measure purchase intent? "
            "Choose 7-day and 30-day windows.\n"
            "- Spillover/contamination: users may see the ad on other platforms; "
            "interpret results as incremental lift above baseline exposure.\n"
            "- Survey response bias: survey takers are not representative of all ad viewers.\n\n"
            "Analysis: compare brand lift survey scores between treatment and control. "
            "Report absolute and relative lift with confidence intervals."
        ),
        explanation="Ad effectiveness measurement requires controlled holdout groups and brand lift surveys to address selection bias.",
        hints=[
            "Why can't you just compare people who clicked vs. didn't click?",
            "What is a 'ghost ad' and why does it control for selection bias?",
        ],
        tags=["advertising", "experimental-design", "causal-inference"],
    ),
]
