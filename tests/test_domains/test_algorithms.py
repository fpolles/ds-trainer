"""Smoke tests for the algorithms question bank."""
from __future__ import annotations

from ds_trainer.domains.algorithms import QUESTIONS
from ds_trainer.evaluators import eval_code
from ds_trainer.models import Domain, ExerciseType


def test_question_count():
    assert len(QUESTIONS) >= 8


def test_all_questions_valid():
    for q in QUESTIONS:
        assert q.domain == Domain.ALGORITHMS


def test_model_answers_pass_test_cases():
    for q in QUESTIONS:
        if q.exercise_type == ExerciseType.FILL_IN_CODE and q.test_cases and q.model_answer:
            passed, detail = eval_code(q.model_answer, q.test_cases)
            assert passed, f"{q.id} model answer failed: {detail}"
