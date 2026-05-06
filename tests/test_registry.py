"""Tests for registry.py — load_all, filter_questions, sample_questions."""
from __future__ import annotations

import pytest

from ds_trainer.registry import filter_questions, load_all, sample_questions, stats_table


@pytest.fixture(scope="module")
def all_questions():
    return load_all()


class TestLoadAll:
    def test_minimum_question_count(self, all_questions):
        assert len(all_questions) >= 59

    def test_all_questions_have_ids(self, all_questions):
        ids = [q.id for q in all_questions]
        assert len(ids) == len(set(ids)), "Duplicate question IDs found"

    def test_domains_represented(self, all_questions):
        domains = {q.domain.value for q in all_questions}
        assert domains == {"sql", "python", "statistics", "ml", "algorithms", "case_studies"}

    def test_all_difficulties_represented(self, all_questions):
        difficulties = {q.difficulty.value for q in all_questions}
        assert difficulties == {"easy", "medium", "hard"}


class TestFilterQuestions:
    def test_filter_by_domain(self, all_questions):
        sql_qs = filter_questions(all_questions, domain="sql")
        assert all(q.domain.value == "sql" for q in sql_qs)
        assert len(sql_qs) >= 1

    def test_filter_by_difficulty(self, all_questions):
        easy_qs = filter_questions(all_questions, difficulty="easy")
        assert all(q.difficulty.value == "easy" for q in easy_qs)

    def test_filter_by_type(self, all_questions):
        mc_qs = filter_questions(all_questions, exercise_type="multiple_choice")
        assert all(q.exercise_type.value == "multiple_choice" for q in mc_qs)

    def test_all_filters_combined(self, all_questions):
        result = filter_questions(all_questions, domain="sql", difficulty="easy", exercise_type="multiple_choice")
        for q in result:
            assert q.domain.value == "sql"
            assert q.difficulty.value == "easy"
            assert q.exercise_type.value == "multiple_choice"

    def test_no_match_returns_empty(self, all_questions):
        result = filter_questions(all_questions, domain="sql", difficulty="easy", exercise_type="take_home")
        assert result == []

    def test_all_default_returns_everything(self, all_questions):
        result = filter_questions(all_questions)
        assert len(result) == len(all_questions)


class TestSampleQuestions:
    def test_respects_count(self, all_questions):
        sample = sample_questions(all_questions, count=3)
        assert len(sample) == 3

    def test_count_exceeds_pool(self, all_questions):
        subset = all_questions[:2]
        sample = sample_questions(subset, count=100)
        assert len(sample) == 2

    def test_no_shuffle_returns_first_n(self, all_questions):
        sample = sample_questions(all_questions, count=3, shuffle=False)
        assert sample == all_questions[:3]

    def test_empty_input(self):
        assert sample_questions([], count=5) == []


class TestStatsTable:
    def test_structure(self, all_questions):
        tbl = stats_table(all_questions)
        for domain, counts in tbl.items():
            assert isinstance(domain, str)
            for diff, cnt in counts.items():
                assert isinstance(cnt, int)
                assert cnt >= 0

    def test_totals_match(self, all_questions):
        tbl = stats_table(all_questions)
        total = sum(c for d in tbl.values() for c in d.values())
        assert total == len(all_questions)
