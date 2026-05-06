from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Domain(str, Enum):
    SQL = "sql"
    PYTHON = "python"
    STATISTICS = "statistics"
    ML = "ml"
    ALGORITHMS = "algorithms"
    CASE_STUDIES = "case_studies"
    PROBABILITY = "probability"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ExerciseType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_CODE = "fill_in_code"
    EXPLAIN_CONCEPT = "explain_concept"
    SQL_CHALLENGE = "sql_challenge"
    TAKE_HOME = "take_home"


@dataclass
class Question:
    id: str
    domain: Domain
    difficulty: Difficulty
    exercise_type: ExerciseType
    prompt: str
    explanation: str
    hints: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    # MULTIPLE_CHOICE
    choices: Optional[list[str]] = None
    answer_index: Optional[int] = None

    # FILL_IN_CODE
    code_template: Optional[str] = None
    test_cases: Optional[list[dict]] = None
    model_answer: Optional[str] = None

    # SQL_CHALLENGE
    schema_ddl: Optional[str] = None
    seed_data: Optional[str] = None
    expected_query: Optional[str] = None

    # TAKE_HOME
    project_spec: Optional[str] = None
    dataset_generator: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Question.id is required")
        match self.exercise_type:
            case ExerciseType.MULTIPLE_CHOICE:
                assert self.choices and self.answer_index is not None, (
                    f"{self.id}: MULTIPLE_CHOICE requires choices and answer_index"
                )
                assert 0 <= self.answer_index < len(self.choices), (
                    f"{self.id}: answer_index out of range"
                )
            case ExerciseType.SQL_CHALLENGE:
                assert self.schema_ddl and self.expected_query, (
                    f"{self.id}: SQL_CHALLENGE requires schema_ddl and expected_query"
                )
            case ExerciseType.FILL_IN_CODE:
                assert self.test_cases or self.model_answer, (
                    f"{self.id}: FILL_IN_CODE requires test_cases or model_answer"
                )
            case ExerciseType.TAKE_HOME:
                assert self.project_spec and self.dataset_generator, (
                    f"{self.id}: TAKE_HOME requires project_spec and dataset_generator"
                )
            case ExerciseType.EXPLAIN_CONCEPT:
                assert self.model_answer, (
                    f"{self.id}: EXPLAIN_CONCEPT requires model_answer"
                )


@dataclass
class SessionResult:
    question_id: str
    correct: bool
    hints_used: int
    time_seconds: float
    user_answer: str


@dataclass
class Session:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    started_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    results: list[SessionResult] = field(default_factory=list)

    @property
    def score(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.correct for r in self.results) / len(self.results)

    @property
    def correct_count(self) -> int:
        return sum(r.correct for r in self.results)

    def by_domain(self) -> dict[str, list[SessionResult]]:
        groups: dict[str, list[SessionResult]] = {}
        for r in self.results:
            domain = r.question_id.split("_")[0]
            groups.setdefault(domain, []).append(r)
        return groups
