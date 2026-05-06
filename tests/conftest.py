"""Shared pytest fixtures."""
from __future__ import annotations

import pytest

from ds_trainer.models import (
    Difficulty,
    Domain,
    ExerciseType,
    Question,
    Session,
    SessionResult,
)


@pytest.fixture()
def mc_question() -> Question:
    return Question(
        id="test_mc_001",
        domain=Domain.ML,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        prompt="Which metric is best for imbalanced classes?",
        explanation="F1 balances precision and recall.",
        choices=["Accuracy", "F1-score", "MSE", "R²"],
        answer_index=1,
        model_answer="F1-score",
    )


@pytest.fixture()
def code_question() -> Question:
    return Question(
        id="test_code_001",
        domain=Domain.ALGORITHMS,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.FILL_IN_CODE,
        prompt="Write a function add(a, b) that returns a + b.",
        explanation="Basic addition.",
        test_cases=[{"function": "add", "args": [2, 3], "expected": 5}],
        model_answer="def add(a, b):\n    return a + b",
    )


@pytest.fixture()
def sql_question() -> Question:
    return Question(
        id="test_sql_001",
        domain=Domain.SQL,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.SQL_CHALLENGE,
        prompt="Select all rows from the items table.",
        explanation="Basic SELECT.",
        schema_ddl="CREATE TABLE items (id INTEGER, name TEXT);",
        seed_data="INSERT INTO items VALUES (1, 'apple'), (2, 'banana');",
        expected_query="SELECT id, name FROM items;",
    )


@pytest.fixture()
def explain_question() -> Question:
    return Question(
        id="test_exp_001",
        domain=Domain.STATISTICS,
        difficulty=Difficulty.EASY,
        exercise_type=ExerciseType.EXPLAIN_CONCEPT,
        prompt="What is a p-value?",
        explanation="A p-value is the probability of observing results at least as extreme as the data given H0 is true.",
        model_answer="The probability of observing results at least as extreme as the data, assuming H0 is true.",
    )


@pytest.fixture()
def session_with_results() -> Session:
    s = Session()
    s.results = [
        SessionResult(question_id="sql_e_001", correct=True, hints_used=0, time_seconds=12.0, user_answer="A"),
        SessionResult(question_id="sql_m_001", correct=False, hints_used=1, time_seconds=30.0, user_answer="B"),
        SessionResult(question_id="py_e_001", correct=True, hints_used=0, time_seconds=20.0, user_answer="C"),
    ]
    return s
