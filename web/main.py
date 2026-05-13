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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
