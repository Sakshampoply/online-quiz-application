from typing import List, Optional

from pydantic import BaseModel, ConfigDict

# --- Schemas for Choices ---


class ChoiceBase(BaseModel):
    text: str


class ChoiceCreate(ChoiceBase):
    is_correct: bool


# This is the schema for choices when they are returned from the API (e.g. in a question)
# It purposefully omits `is_correct`
class Choice(ChoiceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Schemas for Questions ---


class QuestionBase(BaseModel):
    text: str


class QuestionCreate(QuestionBase):
    pass


# This is the schema for a single question when returned from the API
class Question(QuestionBase):
    id: int
    choices: List[Choice] = []

    model_config = ConfigDict(from_attributes=True)


# --- Schemas for Quiz Submission and Results ---


# A single answer in a user's submission
class UserAnswer(BaseModel):
    question_id: int
    choice_id: int


# The complete payload for a quiz submission
class AnswerPayload(BaseModel):
    answers: List[UserAnswer]


# The detailed result for a single question
class QuestionResult(BaseModel):
    question_id: int
    question_text: str
    user_answer_text: Optional[str] = None
    correct_answer_text: str
    is_correct: bool


# The final result of the entire quiz
class QuizResult(BaseModel):
    score: int
    total: int
    results: List[QuestionResult]
