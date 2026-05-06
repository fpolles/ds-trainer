"""Tests for models.py — Question validation and Session behaviour."""
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


class TestQuestionValidation:
    def test_mc_valid(self, mc_question):
        assert mc_question.id == "test_mc_001"

    def test_mc_missing_choices_raises(self):
        with pytest.raises(AssertionError):
            Question(
                id="bad_mc",
                domain=Domain.ML,
                difficulty=Difficulty.EASY,
                exercise_type=ExerciseType.MULTIPLE_CHOICE,
                prompt="Q?",
                explanation="E.",
                answer_index=0,
            )

    def test_mc_answer_index_out_of_range_raises(self):
        with pytest.raises(AssertionError):
            Question(
                id="bad_mc2",
                domain=Domain.ML,
                difficulty=Difficulty.EASY,
                exercise_type=ExerciseType.MULTIPLE_CHOICE,
                prompt="Q?",
                explanation="E.",
                choices=["A", "B"],
                answer_index=5,
            )

    def test_sql_challenge_missing_schema_raises(self):
        with pytest.raises(AssertionError):
            Question(
                id="bad_sql",
                domain=Domain.SQL,
                difficulty=Difficulty.EASY,
                exercise_type=ExerciseType.SQL_CHALLENGE,
                prompt="Q?",
                explanation="E.",
                expected_query="SELECT 1;",
            )

    def test_fill_in_code_needs_test_cases_or_model_answer(self):
        with pytest.raises(AssertionError):
            Question(
                id="bad_code",
                domain=Domain.ALGORITHMS,
                difficulty=Difficulty.EASY,
                exercise_type=ExerciseType.FILL_IN_CODE,
                prompt="Write something.",
                explanation="E.",
            )

    def test_fill_in_code_model_answer_only_is_valid(self):
        q = Question(
            id="code_ma",
            domain=Domain.ALGORITHMS,
            difficulty=Difficulty.EASY,
            exercise_type=ExerciseType.FILL_IN_CODE,
            prompt="Write something.",
            explanation="E.",
            model_answer="def f(): pass",
        )
        assert q.model_answer == "def f(): pass"

    def test_explain_concept_requires_model_answer(self):
        with pytest.raises(AssertionError):
            Question(
                id="bad_exp",
                domain=Domain.STATISTICS,
                difficulty=Difficulty.EASY,
                exercise_type=ExerciseType.EXPLAIN_CONCEPT,
                prompt="Explain X.",
                explanation="E.",
            )

    def test_take_home_requires_project_spec_and_generator(self):
        with pytest.raises(AssertionError):
            Question(
                id="bad_th",
                domain=Domain.CASE_STUDIES,
                difficulty=Difficulty.HARD,
                exercise_type=ExerciseType.TAKE_HOME,
                prompt="Build a model.",
                explanation="E.",
            )

    def test_empty_id_raises(self):
        with pytest.raises(ValueError):
            Question(
                id="",
                domain=Domain.SQL,
                difficulty=Difficulty.EASY,
                exercise_type=ExerciseType.EXPLAIN_CONCEPT,
                prompt="Q?",
                explanation="E.",
                model_answer="A.",
            )


class TestSession:
    def test_empty_session_score_zero(self):
        s = Session()
        assert s.score == 0.0
        assert s.correct_count == 0

    def test_score_calculation(self, session_with_results):
        assert session_with_results.correct_count == 2
        assert abs(session_with_results.score - 2 / 3) < 1e-9

    def test_by_domain_groups_correctly(self, session_with_results):
        grouped = session_with_results.by_domain()
        assert "sql" in grouped
        assert "py" in grouped
        assert len(grouped["sql"]) == 2
        assert len(grouped["py"]) == 1

    def test_session_id_is_hex(self):
        s = Session()
        assert len(s.id) == 8
        int(s.id, 16)  # must be valid hex
