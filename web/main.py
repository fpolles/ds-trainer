from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import sys
import os
import json

# Add parent to path to import ds_trainer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ds_trainer.registry import load_all, filter_questions, sample_questions
from ds_trainer.models import Question, ExerciseType
from ds_trainer.evaluators import eval_code, eval_sql

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

def get_questions_dict():
    return {q.id: q for q in load_all()}

class StartRequest(BaseModel):
    domain: str = "all"
    difficulty: str = "all"
    exercise_type: str = "all"
    count: int = 5

class EvaluateRequest(BaseModel):
    question_id: str
    user_answer: str

class ResetRequest(BaseModel):
    confirm: bool = False

class AddQuestionRequest(BaseModel):
    id: str | None = None
    domain: str
    difficulty: str
    exercise_type: str
    prompt: str
    explanation: str = ""
    hints: list[str] = []
    tags: list[str] = []
    choices: list[str] | None = None
    answer_index: int | None = None
    code_template: str | None = None
    test_cases: list[dict] | None = None
    model_answer: str | None = None
    schema_ddl: str | None = None
    seed_data: str | None = None
    expected_query: str | None = None
    project_spec: str | None = None
    dataset_generator: str | None = None

@app.get("/api/config")
def get_config():
    questions = get_questions_dict()
    domains = list(set(q.domain.value for q in questions.values()))
    difficulties = list(set(q.difficulty.value for q in questions.values()))
    types = list(set(q.exercise_type.value for q in questions.values()))
    
    # ensure "all" is available
    return {
        "domains": ["all"] + sorted(domains),
        "difficulties": ["all"] + sorted(difficulties),
        "types": ["all"] + sorted(types)
    }

@app.post("/api/start")
def start_session(req: StartRequest):
    questions = get_questions_dict()
    qs = filter_questions(list(questions.values()), req.domain, req.difficulty, req.exercise_type)
    sampled = sample_questions(qs, req.count, shuffle=True)
    
    # Strip answers for the client
    client_qs = []
    for q in sampled:
        # Create a dict that can be safely serialized
        q_dict = {
            "id": q.id,
            "domain": q.domain.value,
            "difficulty": q.difficulty.value,
            "exercise_type": q.exercise_type.value,
            "prompt": q.prompt,
            "hints": q.hints,
            "tags": q.tags,
            "choices": q.choices,
            "code_template": q.code_template,
            "schema_ddl": q.schema_ddl,
            "seed_data": q.seed_data,
            "project_spec": q.project_spec
        }
        client_qs.append(q_dict)
        
    return {"questions": client_qs}

@app.post("/api/evaluate")
def evaluate(req: EvaluateRequest):
    questions = get_questions_dict()
    q = questions.get(req.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
        
    correct = False
    message = ""
    
    if q.exercise_type == ExerciseType.MULTIPLE_CHOICE:
        try:
            ans_idx = int(req.user_answer)
            correct = (ans_idx == q.answer_index)
            # Use safe access and provide fallback if answer_index is not set properly
            ans_str = q.choices[q.answer_index] if q.answer_index is not None and q.choices else "Unknown"
            message = "Correct!" if correct else f"Incorrect. The correct answer was: {ans_str}"
        except ValueError:
            message = "Invalid answer format. Please select an option."
            
    elif q.exercise_type == ExerciseType.FILL_IN_CODE:
        if q.test_cases:
            # We inject pandas if domain is python (or all really, but let's base on domain)
            correct, message = eval_code(req.user_answer, q.test_cases, inject_pandas=(q.domain.value == "python"))
        else:
            correct = True
            message = "Self-graded. Compare your answer with the model solution."
            
    elif q.exercise_type == ExerciseType.SQL_CHALLENGE:
        correct, message = eval_sql(req.user_answer, q.expected_query or "", q.schema_ddl or "", q.seed_data or "")
        
    elif q.exercise_type in (ExerciseType.EXPLAIN_CONCEPT, ExerciseType.TAKE_HOME):
        correct = True
        message = "Self-graded. Compare your answer with the model solution."
        
    model_ans = q.model_answer or q.expected_query
    if q.exercise_type == ExerciseType.MULTIPLE_CHOICE and q.answer_index is not None and q.choices:
        model_ans = q.choices[q.answer_index]

    return {
        "correct": correct,
        "message": message,
        "model_answer": model_ans,
        "explanation": q.explanation
    }

@app.post("/api/test_question")
def test_question(req: AddQuestionRequest):
    if not req.prompt:
        return {"success": False, "message": "Prompt is required."}
    
    if req.exercise_type == ExerciseType.MULTIPLE_CHOICE:
        if not req.choices or req.answer_index is None:
            return {"success": False, "message": "Choices and Answer Index required."}
        if req.answer_index < 0 or req.answer_index >= len(req.choices):
            return {"success": False, "message": "Answer Index out of bounds."}
        return {"success": True, "message": "Valid multiple choice question."}
        
    elif req.exercise_type == ExerciseType.FILL_IN_CODE:
        if not req.model_answer:
            return {"success": False, "message": "Model answer is required."}
        if req.test_cases:
            correct, message = eval_code(req.model_answer, req.test_cases, inject_pandas=(req.domain == "python"))
            return {"success": correct, "message": message}
        return {"success": True, "message": "Valid code question (no test cases provided)."}
        
    elif req.exercise_type == ExerciseType.SQL_CHALLENGE:
        if not req.schema_ddl or not req.expected_query:
            return {"success": False, "message": "Schema and Expected Query required."}
        correct, message = eval_sql(req.expected_query, req.expected_query, req.schema_ddl, req.seed_data or "")
        return {"success": correct, "message": f"Query executed successfully. {message}"}
        
    elif req.exercise_type == ExerciseType.EXPLAIN_CONCEPT:
        if not req.model_answer:
            return {"success": False, "message": "Model answer is required."}
        return {"success": True, "message": "Valid concept question."}
        
    elif req.exercise_type == ExerciseType.TAKE_HOME:
        if not req.project_spec or not req.dataset_generator:
            return {"success": False, "message": "Project spec and dataset generator required."}
        return {"success": True, "message": "Valid take-home question."}
    
    return {"success": False, "message": "Unknown exercise type."}

@app.post("/api/add_question")
def add_question(req: AddQuestionRequest):
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ds_trainer", "questions.db")
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        if not req.id:
            domain_prefixes = {
                "sql": "sql",
                "python": "py",
                "statistics": "stat",
                "ml": "ml",
                "algorithms": "alg",
                "case_studies": "case",
                "probability": "prob"
            }
            diff_prefixes = {
                "easy": "e",
                "medium": "m",
                "hard": "h"
            }
            d_pref = domain_prefixes.get(req.domain, "q")
            df_pref = diff_prefixes.get(req.difficulty, "x")
            prefix = f"{d_pref}_{df_pref}_"
            
            c.execute("SELECT id FROM questions WHERE id LIKE ?", (prefix + "%",))
            existing_ids = [row[0] for row in c.fetchall()]
            max_serial = 0
            for eid in existing_ids:
                parts = eid.split('_')
                if len(parts) == 3 and parts[2].isdigit():
                    max_serial = max(max_serial, int(parts[2]))
            req.id = f"{prefix}{max_serial + 1:03d}"
            
        c.execute('''
            INSERT INTO questions VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            req.id, req.domain, req.difficulty, req.exercise_type, req.prompt, req.explanation,
            json.dumps(req.hints), json.dumps(req.tags), json.dumps(req.choices) if req.choices else None,
            req.answer_index, req.code_template, json.dumps(req.test_cases) if req.test_cases else None,
            req.model_answer, req.schema_ddl, req.seed_data, req.expected_query, req.project_spec, req.dataset_generator
        ))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Question added to database!"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/reset_database")
def reset_database(req: ResetRequest):
    if not req.confirm:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Must send {\"confirm\": true} to reset the database.")
    import sqlite3
    from ds_trainer.domains import (
        algorithms, case_studies, ml, probability, python_pandas, sql, statistics
    )
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ds_trainer", "questions.db")
    
    questions = (
        sql.QUESTIONS
        + python_pandas.QUESTIONS
        + statistics.QUESTIONS
        + ml.QUESTIONS
        + algorithms.QUESTIONS
        + case_studies.QUESTIONS
        + probability.QUESTIONS
    )
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM questions')
        
        for q in questions:
            c.execute('''
                INSERT INTO questions VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                q.id, q.domain.value, q.difficulty.value, q.exercise_type.value, q.prompt, q.explanation,
                json.dumps(q.hints) if q.hints else "[]", json.dumps(q.tags) if q.tags else "[]",
                json.dumps(q.choices) if q.choices else None, q.answer_index, q.code_template,
                json.dumps(q.test_cases) if q.test_cases else None, q.model_answer, q.schema_ddl,
                q.seed_data, q.expected_query, q.project_spec, q.dataset_generator
            ))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Successfully restored {len(questions)} core questions."}
    except Exception as e:
        return {"success": False, "message": str(e)}

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
