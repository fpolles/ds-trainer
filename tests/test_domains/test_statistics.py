"""Smoke tests for the statistics question bank."""
from __future__ import annotations

from ds_trainer.domains.statistics import QUESTIONS
from ds_trainer.models import Domain, ExerciseType


def test_question_count():
    assert len(QUESTIONS) >= 10


def test_all_questions_valid():
    for q in QUESTIONS:
        assert q.domain == Domain.STATISTICS


def test_explain_concepts_have_model_answer():
    for q in QUESTIONS:
        if q.exercise_type == ExerciseType.EXPLAIN_CONCEPT:
            assert q.model_answer, f"{q.id} EXPLAIN_CONCEPT missing model_answer"


def test_take_home_questions_have_generator():
    for q in QUESTIONS:
        if q.exercise_type == ExerciseType.TAKE_HOME:
            assert q.dataset_generator, f"{q.id} TAKE_HOME missing dataset_generator"
            assert q.project_spec, f"{q.id} TAKE_HOME missing project_spec"
