from typing import List

from fastapi import Depends, FastAPI, HTTPException

# Add CORS middleware to allow frontend to call backend
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, get_db

# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CORS (Cross-Origin Resource Sharing) ---
# This is crucial for allowing your Next.js frontend (running on localhost:3000)
# to make requests to your FastAPI backend (running on localhost:8000).

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# --- API Endpoints ---


@app.get("/")
def read_root():
    return {"message": "Welcome to the Quiz API"}


@app.get("/questions/", response_model=List[schemas.Question])
def read_questions(db: Session = Depends(get_db)):
    """
    Fetches all questions for the quiz.
    The response model ensures the correct answers are not sent to the client.
    """
    questions = crud.get_questions(db)
    return questions


@app.post("/submit/", response_model=schemas.QuizResult)
def submit_quiz(submission: schemas.AnswerPayload, db: Session = Depends(get_db)):
    """
    Receives user answers, calculates the score, and returns the detailed results.
    """
    results = crud.calculate_score(db, user_answers=submission)
    if results is None:
        raise HTTPException(status_code=400, detail="Error calculating score.")
    return results
