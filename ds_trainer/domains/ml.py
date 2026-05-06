from ds_trainer.models import Difficulty, Domain, ExerciseType, Question

QUESTIONS: list[Question] = [
    # ── Easy ──────────────────────────────────────────────────────────────
    Question(
        id="ml_e_001",
        domain=Domain.ML,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "Your model achieves 98% accuracy on the training set and 62% on the validation set. "
            "What problem does this describe?"
        ),
        choices=["Underfitting", "Overfitting", "Class imbalance", "Data leakage"],
        answer_index=1,
        explanation=(
            "A large gap between training and validation accuracy is the hallmark of overfitting "
            "(high variance). The model has memorized training noise rather than learning "
            "generalizable patterns. Solutions: reduce model complexity, add regularization, "
            "gather more data, use dropout."
        ),
        hints=["The training score is much higher than validation."],
        tags=["overfitting", "bias-variance"],
    ),
    Question(
        id="ml_e_002",
        domain=Domain.ML,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "You are building a fraud detection model. Fraudulent transactions are 0.1% of the data. "
            "A model that predicts 'not fraud' for every transaction achieves 99.9% accuracy. "
            "Which metric would you use instead?"
        ),
        choices=["Accuracy", "F1-score", "R²", "Mean Absolute Error"],
        answer_index=1,
        explanation=(
            "With severe class imbalance, accuracy is misleading. F1-score (harmonic mean of "
            "Precision and Recall) penalizes the model for missing the minority class. "
            "Precision-Recall AUC or ROC-AUC are also good choices depending on the cost structure."
        ),
        hints=["When one class is 0.1% of data, accuracy tells you almost nothing."],
        tags=["class-imbalance", "evaluation-metrics"],
    ),
    Question(
        id="ml_e_003",
        domain=Domain.ML,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "Explain the difference between supervised, unsupervised, and semi-supervised learning. "
            "Give one algorithm example for each."
        ),
        model_answer=(
            "Supervised learning: the model learns from labeled data (input-output pairs). "
            "Goal: predict output for new inputs. Examples: linear regression (continuous target), "
            "random forest (classification), SVM.\n\n"
            "Unsupervised learning: no labels — the model finds structure in data on its own. "
            "Goal: discover patterns, clusters, or compressed representations. "
            "Examples: k-means clustering, PCA, autoencoders.\n\n"
            "Semi-supervised learning: small labeled dataset + large unlabeled dataset. "
            "Use unlabeled data to improve decision boundaries learned from labeled data. "
            "Examples: label propagation, self-training, BERT pre-training + fine-tuning.\n\n"
            "Rule of thumb: supervised when labels are available and quality is high; "
            "unsupervised for EDA, segmentation, anomaly detection; semi-supervised when "
            "labeling is expensive."
        ),
        explanation="The three main ML paradigms differ in whether and how labels are used.",
        hints=["Think about what 'labeled data' means in each case."],
        tags=["ml-fundamentals", "supervised", "unsupervised"],
    ),
    # ── Medium ─────────────────────────────────────────────────────────────
    Question(
        id="ml_m_001",
        domain=Domain.ML,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "Explain how a Random Forest works. Why does it generally outperform a single "
            "decision tree, and what are its main hyperparameters to tune?"
        ),
        model_answer=(
            "A Random Forest is an ensemble of decision trees trained using two sources of randomness:\n"
            "1. Bootstrap sampling (bagging): each tree trains on a random sample with replacement.\n"
            "2. Feature subsampling: at each split, only a random subset of features is considered "
            "(typically √p for classification, p/3 for regression).\n\n"
            "Why it outperforms a single tree:\n"
            "- Individual trees are high-variance (overfit to their training data).\n"
            "- Averaging many uncorrelated trees reduces variance without increasing bias "
            "(bias-variance decomposition).\n"
            "- The ensemble smooths out individual errors.\n\n"
            "Key hyperparameters:\n"
            "- n_estimators: number of trees (more = more stable, diminishing returns after ~100-200).\n"
            "- max_depth: limits tree depth (lower = more bias, less variance).\n"
            "- max_features: features considered per split (key randomization knob).\n"
            "- min_samples_leaf: minimum observations at leaves (prevents overfitting on noise).\n"
            "- class_weight: for imbalanced targets."
        ),
        explanation="Random Forest reduces variance through ensemble averaging and random feature selection.",
        hints=[
            "What does 'uncorrelated' mean for the individual trees?",
            "How does averaging affect variance?",
        ],
        tags=["random-forest", "ensemble", "hyperparameters"],
    ),
    Question(
        id="ml_m_002",
        domain=Domain.ML,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete the function that trains a logistic regression with cross-validation "
            "and returns the mean and std of the ROC-AUC scores."
        ),
        code_template="""\
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

def cv_roc_auc(X, y, cv: int = 5) -> tuple[float, float]:
    \"\"\"Return (mean_auc, std_auc) from k-fold cross-validation.\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

def cv_roc_auc(X, y, cv: int = 5) -> tuple[float, float]:
    model = LogisticRegression(max_iter=1000, random_state=42)
    scores = cross_val_score(model, X, y, cv=cv, scoring='roc_auc')
    return (round(float(scores.mean()), 4), round(float(scores.std()), 4))
""",
        test_cases=[
            {
                "function": "cv_roc_auc",
                "args": [
                    {"__sklearn_dataset__": "breast_cancer_X"},
                    {"__sklearn_dataset__": "breast_cancer_y"},
                ],
                "expected": (0.99, 0.006),
            }
        ],
        explanation=(
            "cross_val_score with scoring='roc_auc' runs stratified k-fold by default for classifiers. "
            "The mean measures model quality; std measures stability."
        ),
        hints=[
            "LogisticRegression needs max_iter increased for convergence.",
            "cross_val_score returns an array of k scores.",
        ],
        tags=["logistic-regression", "cross-validation", "roc-auc"],
    ),
    Question(
        id="ml_m_003",
        domain=Domain.ML,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt=(
            "Which of the following is a correct statement about gradient boosting "
            "vs. random forests?"
        ),
        choices=[
            "Random forests are trained sequentially; gradient boosting trains trees in parallel",
            "Gradient boosting builds trees sequentially, each correcting the residuals of the previous",
            "Both methods use bagging; gradient boosting also uses boosting",
            "Gradient boosting is always faster to train than random forests",
        ],
        answer_index=1,
        explanation=(
            "Gradient boosting is sequential: each new tree fits the residuals (pseudo-residuals) "
            "of the ensemble so far, adding a small step in the negative gradient direction. "
            "Random forests train trees independently and average them (parallel, bagging). "
            "Boosting usually achieves lower bias but is more prone to overfitting and slower."
        ),
        hints=["One method corrects errors iteratively; the other averages independent trees."],
        tags=["gradient-boosting", "random-forest", "ensemble"],
    ),
    Question(
        id="ml_m_004",
        domain=Domain.ML,
        difficulty=Difficulty.MEDIUM,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "What is feature importance in tree-based models? Name two ways to compute it "
            "and one pitfall of each."
        ),
        model_answer=(
            "Feature importance quantifies how much each feature contributes to model predictions.\n\n"
            "1. Mean Decrease in Impurity (MDI) / Gini importance (sklearn default):\n"
            "   How it works: sum the impurity reduction at each split involving the feature, "
            "weighted by node sample count, averaged over trees.\n"
            "   Pitfall: biased toward high-cardinality features (e.g., continuous variables "
            "or IDs) because they offer more split points, even if they're not actually predictive.\n\n"
            "2. Permutation importance:\n"
            "   How it works: shuffle the feature's values and measure the drop in model performance. "
            "Large drop = important feature.\n"
            "   Pitfall: correlated features can share importance — shuffling one correlated feature "
            "may not hurt if another carries the same signal.\n\n"
            "Best practice: use permutation importance on the validation set for reliable estimates; "
            "SHAP values provide the most principled game-theoretic decomposition."
        ),
        explanation="Feature importance helps with model interpretation and feature selection.",
        hints=[
            "MDI is computed during training; permutation importance uses a hold-out set.",
        ],
        tags=["feature-importance", "interpretability"],
    ),
    # ── Hard ───────────────────────────────────────────────────────────────
    Question(
        id="ml_h_001",
        domain=Domain.ML,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "Explain how gradient descent works, including the role of the learning rate. "
            "What are the differences between batch, mini-batch, and stochastic gradient descent?"
        ),
        model_answer=(
            "Gradient descent minimizes a loss function L(w) by iteratively updating parameters "
            "in the direction of the negative gradient:\n"
            "  w ← w - η ∇L(w)\n"
            "where η (learning rate) controls step size.\n\n"
            "Learning rate impact:\n"
            "- Too large: overshoots minima, oscillates or diverges.\n"
            "- Too small: converges very slowly; can get trapped in shallow local minima.\n"
            "- Adaptive optimizers (Adam, RMSprop) adjust η per parameter automatically.\n\n"
            "Gradient descent variants:\n"
            "1. Batch GD: compute gradient over the ENTIRE dataset per step.\n"
            "   + Accurate gradient; − slow per step, memory intensive, can't escape sharp minima.\n"
            "2. Stochastic GD (SGD): update after EACH single example.\n"
            "   + Fast updates, noisy gradient helps escape local minima; − high variance, slow convergence.\n"
            "3. Mini-batch GD: update after a BATCH of k examples (typical k=32-256).\n"
            "   + Best of both worlds — vectorized efficiency + regularizing noise; most common in deep learning."
        ),
        explanation="Gradient descent is the core optimization algorithm behind nearly all ML training.",
        hints=[
            "Think about the cost vs. accuracy tradeoff of using more or less data per update.",
        ],
        tags=["gradient-descent", "optimization", "deep-learning"],
    ),
    Question(
        id="ml_h_002",
        domain=Domain.ML,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt=(
            "Complete a function that trains a Ridge regression model, uses GridSearchCV to "
            "tune the alpha hyperparameter over [0.01, 0.1, 1, 10, 100], and returns the "
            "best alpha and corresponding CV RMSE."
        ),
        code_template="""\
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer, mean_squared_error

def tune_ridge(X_train, y_train) -> tuple[float, float]:
    \"\"\"Return (best_alpha, cv_rmse) from 5-fold GridSearchCV.\"\"\"
    # YOUR CODE HERE
""",
        model_answer="""\
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer, mean_squared_error

def tune_ridge(X_train, y_train) -> tuple[float, float]:
    rmse_scorer = make_scorer(mean_squared_error, greater_is_better=False)
    grid = GridSearchCV(
        Ridge(), param_grid={'alpha': [0.01, 0.1, 1, 10, 100]},
        scoring=rmse_scorer, cv=5, refit=True
    )
    grid.fit(X_train, y_train)
    best_alpha = float(grid.best_params_['alpha'])
    best_rmse = float(np.sqrt(-grid.best_score_))
    return (best_alpha, round(best_rmse, 2))
""",
        test_cases=[
            {
                "function": "tune_ridge",
                "args": [
                    {"__sklearn_dataset__": "diabetes_X"},
                    {"__sklearn_dataset__": "diabetes_y"},
                ],
                "expected": (0.01, 55.0),
            }
        ],
        explanation=(
            "GridSearchCV exhaustively tries each alpha. The scorer uses negative MSE "
            "(convention: higher = better), so best_score_ is negative; take sqrt(-score) for RMSE."
        ),
        hints=[
            "make_scorer wraps MSE; set greater_is_better=False since lower MSE is better.",
            "best_score_ is the mean cross-validated score (negative MSE here).",
        ],
        tags=["ridge-regression", "hyperparameter-tuning", "gridsearchcv"],
    ),
    Question(
        id="ml_h_003",
        domain=Domain.ML,
        difficulty=Difficulty.HARD,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt=(
            "Explain what data leakage is, give two concrete examples, "
            "and describe how you detect and prevent it."
        ),
        model_answer=(
            "Data leakage occurs when information from outside the training dataset (specifically, "
            "from the future or from the target itself) is used to build the model. "
            "It causes unrealistically high validation scores that don't hold in production.\n\n"
            "Example 1 — Target leakage: you're predicting loan default and include 'days_late_payments' "
            "as a feature. This variable is only known AFTER the default occurs — using it is circular.\n\n"
            "Example 2 — Train/test contamination: you normalize features using the mean/std of the "
            "ENTIRE dataset (including test), then split. The test set statistics 'leak' into training, "
            "making validation scores optimistic.\n\n"
            "Detection:\n"
            "- Suspiciously high accuracy (close to 100%) is a red flag.\n"
            "- Feature correlation > 0.9 with the target is suspicious.\n"
            "- Model performance degrades heavily in production.\n\n"
            "Prevention:\n"
            "- Fit preprocessing (scalers, encoders, imputers) only on training data, then transform test.\n"
            "- Use sklearn Pipelines to enforce this automatically.\n"
            "- Perform temporal splits for time-series data (never use future data to predict past).\n"
            "- Audit feature definitions: ask 'would this be available at prediction time?'"
        ),
        explanation="Leakage is one of the most common and dangerous pitfalls in applied ML.",
        hints=[
            "Think about what information would actually be available at the time of prediction.",
        ],
        tags=["data-leakage", "preprocessing", "production-ml"],
    ),
]
