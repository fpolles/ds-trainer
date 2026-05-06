"""Tests for runner.py — evaluate() and show_summary()."""
from __future__ import annotations

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from ds_trainer.models import ExerciseType, Session, SessionResult
from ds_trainer.runner import evaluate, show_summary


class TestEvaluateMultipleChoice:
    def test_correct_letter(self, mc_question):
        passed, msg = evaluate(mc_question, "B")
        assert passed
        assert "Correct" in msg

    def test_correct_lowercase(self, mc_question):
        passed, _ = evaluate(mc_question, "b")
        assert passed

    def test_wrong_letter(self, mc_question):
        passed, msg = evaluate(mc_question, "A")
        assert not passed
        assert "Incorrect" in msg

    def test_correct_by_number(self, mc_question):
        # answer_index=1 → answer is "2" (1-indexed)
        passed, _ = evaluate(mc_question, "2")
        assert passed

    def test_invalid_answer(self, mc_question):
        passed, msg = evaluate(mc_question, "Z")
        assert not passed
        assert "Invalid" in msg


class TestEvaluateFillInCode:
    def test_correct_code(self, code_question):
        passed, _ = evaluate(code_question, "def add(a, b):\n    return a + b")
        assert passed

    def test_wrong_code(self, code_question):
        passed, _ = evaluate(code_question, "def add(a, b):\n    return a - b")
        assert not passed

    def test_no_test_cases_auto_pass(self, mc_question):
        from ds_trainer.models import Difficulty, Domain, Question
        q = Question(
            id="code_notc",
            domain=Domain.ALGORITHMS,
            difficulty=Difficulty.EASY,
            exercise_type=ExerciseType.FILL_IN_CODE,
            prompt="Explain.",
            explanation="E.",
            model_answer="def f(): pass",
        )
        passed, msg = evaluate(q, "anything")
        assert passed
        assert "No automated tests" in msg


class TestEvaluateSqlChallenge:
    def test_correct_sql(self, sql_question):
        passed, _ = evaluate(sql_question, "SELECT id, name FROM items;")
        assert passed

    def test_wrong_sql(self, sql_question):
        passed, _ = evaluate(sql_question, "SELECT id FROM items;")
        assert not passed

    def test_no_schema_auto_pass(self):
        from ds_trainer.models import Difficulty, Domain, Question
        q = Question(
            id="sql_noschema",
            domain=Domain.SQL,
            difficulty=Difficulty.EASY,
            exercise_type=ExerciseType.SQL_CHALLENGE,
            prompt="Q?",
            explanation="E.",
            schema_ddl="CREATE TABLE x (id INT);",
            expected_query="SELECT 1;",
        )
        # Override to no schema to test fallback
        object.__setattr__(q, "schema_ddl", None)
        passed, msg = evaluate(q, "SELECT 1;")
        assert passed
        assert "Cannot auto-evaluate" in msg


class TestEvaluateExplainConcept:
    def test_always_self_graded(self, explain_question):
        passed, msg = evaluate(explain_question, "any answer")
        assert passed
        assert "Self-graded" in msg


class TestShowSummary:
    def test_summary_renders_without_error(self, session_with_results):
        console = Console(file=StringIO(), force_terminal=False)
        show_summary(session_with_results, console)

    def test_empty_session_renders(self):
        console = Console(file=StringIO(), force_terminal=False)
        show_summary(Session(), console)
