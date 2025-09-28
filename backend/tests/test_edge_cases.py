import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory to the path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backend.crud as crud
import backend.models as models
import backend.schemas as schemas

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


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_calculate_score_empty_answers(self, db_session):
        """Test calculating score with empty answers payload."""
        # Create a question but provide no answers
        question = models.Question(text="Test question")
        db_session.add(question)
        db_session.flush()

        choice = models.Choice(
            text="Test choice", is_correct=True, question_id=question.id
        )
        db_session.add(choice)
        db_session.commit()

        # Empty answers
        user_answers = schemas.AnswerPayload(answers=[])
        result = crud.calculate_score(db_session, user_answers)

        assert result.score == 0
        assert result.total == 1
        assert len(result.results) == 1
        assert result.results[0].user_answer_text == "Unanswered"
        assert not result.results[0].is_correct

    def test_calculate_score_no_questions(self, db_session):
        """Test calculating score when there are no questions in database."""
        user_answers = schemas.AnswerPayload(answers=[])
        result = crud.calculate_score(db_session, user_answers)

        assert result.score == 0
        assert result.total == 0
        assert len(result.results) == 0

    def test_calculate_score_invalid_choice_id(self, db_session):
        """Test calculating score with an invalid choice ID."""
        question = models.Question(text="Test question")
        db_session.add(question)
        db_session.flush()

        choice = models.Choice(
            text="Test choice", is_correct=True, question_id=question.id
        )
        db_session.add(choice)
        db_session.commit()

        # Use an invalid choice ID (999)
        user_answers = schemas.AnswerPayload(
            answers=[schemas.UserAnswer(question_id=question.id, choice_id=999)]
        )
        result = crud.calculate_score(db_session, user_answers)

        assert result.score == 0
        assert result.total == 1
        assert len(result.results) == 1
        # Should show "Unanswered" when choice ID is invalid
        assert result.results[0].user_answer_text == "Unanswered"
        assert not result.results[0].is_correct

    def test_question_without_correct_choice(self, db_session):
        """Test question that has no correct choice marked."""
        question = models.Question(text="Test question")
        db_session.add(question)
        db_session.flush()

        # All choices are wrong
        choice1 = models.Choice(
            text="Choice 1", is_correct=False, question_id=question.id
        )
        choice2 = models.Choice(
            text="Choice 2", is_correct=False, question_id=question.id
        )
        db_session.add_all([choice1, choice2])
        db_session.commit()

        user_answers = schemas.AnswerPayload(
            answers=[schemas.UserAnswer(question_id=question.id, choice_id=choice1.id)]
        )
        result = crud.calculate_score(db_session, user_answers)

        assert result.score == 0
        assert result.total == 1
        # Since no choice is marked correct, the correct answer text should be empty
        assert result.results[0].correct_answer_text == ""

    def test_question_with_multiple_correct_choices(self, db_session):
        """Test question with multiple choices marked as correct (should take the first one)."""
        question = models.Question(text="Test question")
        db_session.add(question)
        db_session.flush()

        choice1 = models.Choice(
            text="Choice 1", is_correct=True, question_id=question.id
        )
        choice2 = models.Choice(
            text="Choice 2", is_correct=True, question_id=question.id
        )
        db_session.add_all([choice1, choice2])
        db_session.commit()

        user_answers = schemas.AnswerPayload(
            answers=[schemas.UserAnswer(question_id=question.id, choice_id=choice1.id)]
        )
        result = crud.calculate_score(db_session, user_answers)

        assert result.score == 1
        assert result.total == 1
        assert result.results[0].is_correct


class TestSchemaValidation:
    """Test schema validation edge cases."""

    def test_choice_with_empty_text(self):
        """Test creating a choice with empty text."""
        choice = schemas.ChoiceBase(text="")
        assert choice.text == ""

    def test_question_with_empty_text(self):
        """Test creating a question with empty text."""
        question = schemas.QuestionCreate(text="")
        assert question.text == ""

    def test_answer_payload_with_duplicate_questions(self):
        """Test answer payload with duplicate question IDs."""
        payload = schemas.AnswerPayload(
            answers=[
                schemas.UserAnswer(question_id=1, choice_id=1),
                schemas.UserAnswer(question_id=1, choice_id=2),  # Duplicate question ID
            ]
        )
        assert len(payload.answers) == 2
        # The schema allows duplicates; business logic should handle this

    def test_quiz_result_with_zero_total(self):
        """Test quiz result with zero total questions."""
        result = schemas.QuizResult(score=0, total=0, results=[])
        assert result.score == 0
        assert result.total == 0
        assert len(result.results) == 0


class TestPerformance:
    """Test performance with larger datasets."""

    def test_get_questions_with_many_choices(self, db_session):
        """Test getting questions when each question has many choices."""
        question = models.Question(text="Question with many choices")
        db_session.add(question)
        db_session.flush()

        # Add 10 choices to the question
        choices = []
        for i in range(10):
            choice = models.Choice(
                text=f"Choice {i}",
                is_correct=(i == 0),  # First choice is correct
                question_id=question.id,
            )
            choices.append(choice)

        db_session.add_all(choices)
        db_session.commit()

        questions = crud.get_questions(db_session)
        assert len(questions) == 1
        assert len(questions[0].choices) == 10

    def test_calculate_score_with_many_questions(self, db_session):
        """Test calculating score with many questions."""
        questions = []
        correct_choices = []

        # Create 20 questions
        for i in range(20):
            question = models.Question(text=f"Question {i}")
            db_session.add(question)
            db_session.flush()

            correct_choice = models.Choice(
                text=f"Correct choice {i}", is_correct=True, question_id=question.id
            )
            wrong_choice = models.Choice(
                text=f"Wrong choice {i}", is_correct=False, question_id=question.id
            )

            db_session.add_all([correct_choice, wrong_choice])
            questions.append(question)
            correct_choices.append(correct_choice)

        db_session.commit()

        # Answer all questions correctly
        user_answers = schemas.AnswerPayload(
            answers=[
                schemas.UserAnswer(question_id=q.id, choice_id=c.id)
                for q, c in zip(questions, correct_choices)
            ]
        )

        result = crud.calculate_score(db_session, user_answers)
        assert result.score == 20
        assert result.total == 20
        assert len(result.results) == 20
        assert all(r.is_correct for r in result.results)
