"""Question loading, filtering, and sampling."""
from __future__ import annotations

import random

from ds_trainer.models import Question


def load_all() -> list[Question]:
    import sqlite3
    import json
    import os
    from ds_trainer.models import Question, Domain, Difficulty, ExerciseType

    db_path = os.path.join(os.path.dirname(__file__), "questions.db")
    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM questions")
    rows = c.fetchall()
    conn.close()

    questions = []
    for row in rows:
        q = Question(
            id=row["id"],
            domain=Domain(row["domain"]),
            difficulty=Difficulty(row["difficulty"]),
            exercise_type=ExerciseType(row["exercise_type"]),
            prompt=row["prompt"],
            explanation=row["explanation"],
            hints=json.loads(row["hints"]) if row["hints"] else [],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            choices=json.loads(row["choices"]) if row["choices"] else None,
            answer_index=row["answer_index"],
            code_template=row["code_template"],
            test_cases=json.loads(row["test_cases"]) if row["test_cases"] else None,
            model_answer=row["model_answer"],
            schema_ddl=row["schema_ddl"],
            seed_data=row["seed_data"],
            expected_query=row["expected_query"],
            project_spec=row["project_spec"],
            dataset_generator=row["dataset_generator"]
        )
        questions.append(q)

    return questions


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
