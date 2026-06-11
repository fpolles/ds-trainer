import sqlite3
import json
import sys
import os

# Add parent to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ds_trainer.domains import (
    algorithms,
    case_studies,
    ml,
    probability,
    python_pandas,
    sql,
    statistics,
)
from ds_trainer.models import Question, Domain, Difficulty, ExerciseType

def main():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ds_trainer", "questions.db")
    questions = (
        sql.QUESTIONS
        + python_pandas.QUESTIONS
        + statistics.QUESTIONS
        + ml.QUESTIONS
        + algorithms.QUESTIONS
        + case_studies.QUESTIONS
        + probability.QUESTIONS
    )
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create table
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            domain TEXT,
            difficulty TEXT,
            exercise_type TEXT,
            prompt TEXT,
            explanation TEXT,
            hints TEXT,
            tags TEXT,
            choices TEXT,
            answer_index INTEGER,
            code_template TEXT,
            test_cases TEXT,
            model_answer TEXT,
            schema_ddl TEXT,
            seed_data TEXT,
            expected_query TEXT,
            project_spec TEXT,
            dataset_generator TEXT
        )
    ''')
    
    # Clear existing data just in case
    c.execute('DELETE FROM questions')
    
    for q in questions:
        c.execute('''
            INSERT INTO questions VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            q.id,
            q.domain.value,
            q.difficulty.value,
            q.exercise_type.value,
            q.prompt,
            q.explanation,
            json.dumps(q.hints) if q.hints else "[]",
            json.dumps(q.tags) if q.tags else "[]",
            json.dumps(q.choices) if q.choices else None,
            q.answer_index,
            q.code_template,
            json.dumps(q.test_cases) if q.test_cases else None,
            q.model_answer,
            q.schema_ddl,
            q.seed_data,
            q.expected_query,
            q.project_spec,
            q.dataset_generator
        ))
        
    conn.commit()
    conn.close()
    print(f"Migrated {len(questions)} questions to {db_path}")

if __name__ == "__main__":
    main()
