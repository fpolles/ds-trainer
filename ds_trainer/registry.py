"""Question loading, filtering, and sampling."""
from __future__ import annotations

import random

from ds_trainer.models import Question


def load_all() -> list[Question]:
    from ds_trainer.domains import (
        algorithms,
        case_studies,
        ml,
        probability,
        python_pandas,
        sql,
        statistics,
    )
    return (
        sql.QUESTIONS
        + python_pandas.QUESTIONS
        + statistics.QUESTIONS
        + ml.QUESTIONS
        + algorithms.QUESTIONS
        + case_studies.QUESTIONS
        + probability.QUESTIONS
    )


def filter_questions(
    questions: list[Question],
    domain: str = "all",
    difficulty: str = "all",
    exercise_type: str = "all",
) -> list[Question]:
    return [
        q for q in questions
        if (domain == "all" or q.domain.value == domain)
        and (difficulty == "all" or q.difficulty.value == difficulty)
        and (exercise_type == "all" or q.exercise_type.value == exercise_type)
    ]


def sample_questions(
    questions: list[Question],
    count: int,
    shuffle: bool = True,
) -> list[Question]:
    if not questions:
        return []
    if shuffle:
        return random.sample(questions, min(count, len(questions)))
    return questions[:count]


def stats_table(questions: list[Question]) -> dict[str, dict[str, int]]:
    """Return {domain: {difficulty: count}} for display."""
    table: dict[str, dict[str, int]] = {}
    for q in questions:
        domain = q.domain.value
        diff = q.difficulty.value
        table.setdefault(domain, {}).setdefault(diff, 0)
        table[domain][diff] += 1
    return table
