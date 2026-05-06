"""Smoke tests for the SQL question bank."""
from __future__ import annotations

import pytest

from ds_trainer.domains.sql import QUESTIONS
from ds_trainer.models import Domain, ExerciseType


def test_question_count():
    assert len(QUESTIONS) >= 12


def test_all_questions_valid():
    for q in QUESTIONS:
        assert q.domain == Domain.SQL


def test_difficulty_distribution():
    by_diff = {}
    for q in QUESTIONS:
        by_diff.setdefault(q.difficulty.value, 0)
        by_diff[q.difficulty.value] += 1
    assert by_diff.get("easy", 0) >= 1
    assert by_diff.get("medium", 0) >= 1
    assert by_diff.get("hard", 0) >= 1


def test_sql_challenges_have_schema():
    for q in QUESTIONS:
        if q.exercise_type == ExerciseType.SQL_CHALLENGE:
            assert q.schema_ddl, f"{q.id} missing schema_ddl"
            assert q.expected_query, f"{q.id} missing expected_query"


def test_sql_challenges_execute():
    """All expected_query values should run without error."""
    import sqlite3
    for q in QUESTIONS:
        if q.exercise_type == ExerciseType.SQL_CHALLENGE and q.schema_ddl and q.expected_query:
            conn = sqlite3.connect(":memory:")
            conn.executescript(q.schema_ddl + "\n" + (q.seed_data or ""))
            try:
                conn.execute(q.expected_query).fetchall()
            except sqlite3.Error as e:
                pytest.fail(f"{q.id}: expected_query failed: {e}")
            finally:
                conn.close()
