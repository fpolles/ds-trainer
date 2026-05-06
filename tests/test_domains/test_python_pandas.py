"""Smoke tests for the Python/Pandas question bank."""
from __future__ import annotations

from ds_trainer.domains.python_pandas import QUESTIONS
from ds_trainer.models import Domain, ExerciseType


def test_question_count():
    assert len(QUESTIONS) >= 10


def test_all_questions_valid():
    for q in QUESTIONS:
        assert q.domain == Domain.PYTHON


def test_fill_in_code_have_test_cases_or_model_answer():
    for q in QUESTIONS:
        if q.exercise_type == ExerciseType.FILL_IN_CODE:
            assert q.test_cases or q.model_answer, f"{q.id} has no evaluation path"


def test_model_answers_evaluate():
    """Model answers for FILL_IN_CODE questions with test_cases should pass evaluation."""
    from ds_trainer.evaluators import eval_code
    from ds_trainer.runner import _inject_pandas_needed

    for q in QUESTIONS:
        if q.exercise_type == ExerciseType.FILL_IN_CODE and q.test_cases and q.model_answer:
            inject = _inject_pandas_needed(q)
            passed, detail = eval_code(q.model_answer, q.test_cases, inject_pandas=inject)
            assert passed, f"{q.id} model answer failed: {detail}"
