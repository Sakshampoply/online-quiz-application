import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory to the path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backend.crud as crud
import backend.models as models
import backend.schemas as schemas
import backend.seed as seed

# Create a test database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    models.Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        models.Base.metadata.drop_all(bind=engine)


class TestCRUD:
    """Test CRUD operations for the quiz application."""

    def test_get_questions_empty_db(self, db_session):
        """Test getting questions from an empty database."""
        questions = crud.get_questions(db_session)
        assert questions == []

    def test_get_questions_with_data(self, db_session):
        """Test getting questions with seeded data."""
        # Create a sample question with choices
        question = models.Question(text="What is Python?")
        db_session.add(question)
        db_session.flush()

        choice1 = models.Choice(
            text="A programming language", is_correct=True, question_id=question.id
        )
        choice2 = models.Choice(
            text="A snake", is_correct=False, question_id=question.id
        )
        db_session.add(choice1)
        db_session.add(choice2)
        db_session.commit()

        questions = crud.get_questions(db_session)
        assert len(questions) == 1
        assert questions[0].text == "What is Python?"
        assert len(questions[0].choices) == 2

    def test_calculate_score_all_correct(self, db_session):
        """Test calculating score when all answers are correct."""
        # Create test data
        question1 = models.Question(text="Question 1")
        question2 = models.Question(text="Question 2")
        db_session.add_all([question1, question2])
        db_session.flush()

        # Add choices for question 1
        choice1_correct = models.Choice(
            text="Correct 1", is_correct=True, question_id=question1.id
        )
        choice1_wrong = models.Choice(
            text="Wrong 1", is_correct=False, question_id=question1.id
        )

        # Add choices for question 2
        choice2_correct = models.Choice(
            text="Correct 2", is_correct=True, question_id=question2.id
        )
        choice2_wrong = models.Choice(
            text="Wrong 2", is_correct=False, question_id=question2.id
        )

        db_session.add_all(
            [choice1_correct, choice1_wrong, choice2_correct, choice2_wrong]
        )
        db_session.commit()

        # Create user answers (all correct)
        user_answers = schemas.AnswerPayload(
            answers=[
                schemas.UserAnswer(
                    question_id=question1.id, choice_id=choice1_correct.id
                ),
                schemas.UserAnswer(
                    question_id=question2.id, choice_id=choice2_correct.id
                ),
            ]
        )

        result = crud.calculate_score(db_session, user_answers)
        assert result.score == 2
        assert result.total == 2
        assert len(result.results) == 2
        assert all(r.is_correct for r in result.results)

    def test_calculate_score_all_wrong(self, db_session):
        """Test calculating score when all answers are wrong."""
        # Create test data
        question1 = models.Question(text="Question 1")
        db_session.add(question1)
        db_session.flush()

        choice1_correct = models.Choice(
            text="Correct 1", is_correct=True, question_id=question1.id
        )
        choice1_wrong = models.Choice(
            text="Wrong 1", is_correct=False, question_id=question1.id
        )
        db_session.add_all([choice1_correct, choice1_wrong])
        db_session.commit()

        # Create user answers (wrong answer)
        user_answers = schemas.AnswerPayload(
            answers=[
                schemas.UserAnswer(question_id=question1.id, choice_id=choice1_wrong.id)
            ]
        )

        result = crud.calculate_score(db_session, user_answers)
        assert result.score == 0
        assert result.total == 1
        assert len(result.results) == 1
        assert not result.results[0].is_correct

    def test_calculate_score_partial_answers(self, db_session):
        """Test calculating score when some questions are unanswered."""
        # Create test data
        question1 = models.Question(text="Question 1")
        question2 = models.Question(text="Question 2")
        db_session.add_all([question1, question2])
        db_session.flush()

        choice1_correct = models.Choice(
            text="Correct 1", is_correct=True, question_id=question1.id
        )
        choice2_correct = models.Choice(
            text="Correct 2", is_correct=True, question_id=question2.id
        )
        db_session.add_all([choice1_correct, choice2_correct])
        db_session.commit()

        # Answer only one question
        user_answers = schemas.AnswerPayload(
            answers=[
                schemas.UserAnswer(
                    question_id=question1.id, choice_id=choice1_correct.id
                )
            ]
        )

        result = crud.calculate_score(db_session, user_answers)
        assert result.score == 1
        assert result.total == 2
        assert len(result.results) == 2

        # Check that unanswered question shows "Unanswered"
        unanswered_result = next(
            r for r in result.results if r.question_id == question2.id
        )
        assert unanswered_result.user_answer_text == "Unanswered"
        assert not unanswered_result.is_correct


class TestSchemas:
    """Test Pydantic schemas for validation."""

    def test_choice_base_schema(self):
        """Test ChoiceBase schema validation."""
        choice = schemas.ChoiceBase(text="Test choice")
        assert choice.text == "Test choice"

    def test_choice_create_schema(self):
        """Test ChoiceCreate schema validation."""
        choice = schemas.ChoiceCreate(text="Test choice", is_correct=True)
        assert choice.text == "Test choice"
        assert choice.is_correct is True

    def test_question_create_schema(self):
        """Test QuestionCreate schema validation."""
        question = schemas.QuestionCreate(text="What is 2+2?")
        assert question.text == "What is 2+2?"

    def test_user_answer_schema(self):
        """Test UserAnswer schema validation."""
        answer = schemas.UserAnswer(question_id=1, choice_id=2)
        assert answer.question_id == 1
        assert answer.choice_id == 2

    def test_answer_payload_schema(self):
        """Test AnswerPayload schema validation."""
        payload = schemas.AnswerPayload(
            answers=[
                schemas.UserAnswer(question_id=1, choice_id=2),
                schemas.UserAnswer(question_id=2, choice_id=3),
            ]
        )
        assert len(payload.answers) == 2
        assert payload.answers[0].question_id == 1

    def test_question_result_schema(self):
        """Test QuestionResult schema validation."""
        result = schemas.QuestionResult(
            question_id=1,
            question_text="What is Python?",
            user_answer_text="A programming language",
            correct_answer_text="A programming language",
            is_correct=True,
        )
        assert result.question_id == 1
        assert result.is_correct is True

    def test_quiz_result_schema(self):
        """Test QuizResult schema validation."""
        question_result = schemas.QuestionResult(
            question_id=1,
            question_text="Test",
            user_answer_text="Answer",
            correct_answer_text="Answer",
            is_correct=True,
        )
        quiz_result = schemas.QuizResult(score=1, total=1, results=[question_result])
        assert quiz_result.score == 1
        assert quiz_result.total == 1
        assert len(quiz_result.results) == 1


class TestModels:
    """Test SQLAlchemy models."""

    def test_question_model_creation(self, db_session):
        """Test creating a Question model instance."""
        question = models.Question(text="What is FastAPI?")
        db_session.add(question)
        db_session.commit()

        assert question.id is not None
        assert question.text == "What is FastAPI?"

    def test_choice_model_creation(self, db_session):
        """Test creating a Choice model instance."""
        question = models.Question(text="Test question")
        db_session.add(question)
        db_session.flush()

        choice = models.Choice(
            text="Test choice", is_correct=True, question_id=question.id
        )
        db_session.add(choice)
        db_session.commit()

        assert choice.id is not None
        assert choice.text == "Test choice"
        assert choice.is_correct is True
        assert choice.question_id == question.id

    def test_question_choice_relationship(self, db_session):
        """Test the relationship between Question and Choice models."""
        question = models.Question(text="Test question")
        db_session.add(question)
        db_session.flush()

        choice1 = models.Choice(
            text="Choice 1", is_correct=True, question_id=question.id
        )
        choice2 = models.Choice(
            text="Choice 2", is_correct=False, question_id=question.id
        )
        db_session.add_all([choice1, choice2])
        db_session.commit()

        # Test the relationship
        db_session.refresh(question)
        assert len(question.choices) == 2
        assert choice1 in question.choices
        assert choice2 in question.choices


class TestSeedData:
    """Test the seed functionality."""

    def test_seed_database_creates_questions(self, db_session):
        """Test that seeding creates the expected questions."""
        seed.seed_database(db_session)

        questions = crud.get_questions(db_session)
        assert len(questions) == 5  # Based on the seed data

        # Check first question
        first_question = questions[0]
        assert "web framework" in first_question.text
        assert len(first_question.choices) == 3

        # Check that FastAPI is mentioned in one of the choices
        fastapi_choice = next(
            (choice for choice in first_question.choices if "FastAPI" in choice.text),
            None,
        )
        assert fastapi_choice is not None
        assert fastapi_choice.is_correct

    def test_seed_database_clears_existing_data(self, db_session):
        """Test that seeding clears existing data before adding new data."""
        # Add some initial data
        question = models.Question(text="Initial question")
        db_session.add(question)
        db_session.commit()

        # Verify initial data exists
        initial_questions = crud.get_questions(db_session)
        assert len(initial_questions) == 1

        # Seed the database
        seed.seed_database(db_session)

        # Verify only seeded data exists
        seeded_questions = crud.get_questions(db_session)
        assert len(seeded_questions) == 5
        assert not any(q.text == "Initial question" for q in seeded_questions)
