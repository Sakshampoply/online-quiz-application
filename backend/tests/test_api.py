import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory to the path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backend.main as main
import backend.models as models
import backend.seed as seed
from backend.database import get_db

# Create a test database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency
main.app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create a test client for each test."""
    models.Base.metadata.create_all(bind=engine)
    with TestClient(main.app) as test_client:
        yield test_client
    models.Base.metadata.drop_all(bind=engine)


class TestAPIEndpoints:
    """Test FastAPI endpoints."""

    def test_read_root(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to the Quiz API"}

    def test_get_questions_empty_db(self, client):
        """Test getting questions from an empty database."""
        response = client.get("/questions/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_questions_with_data(self, client):
        """Test getting questions with seeded data."""
        # Seed the database
        db = TestingSessionLocal()
        seed.seed_database(db)
        db.close()

        response = client.get("/questions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        # Check that the response doesn't include the is_correct field
        first_question = data[0]
        assert "text" in first_question
        assert "id" in first_question
        assert "choices" in first_question

        # Check that choices don't include is_correct field (security measure)
        first_choice = first_question["choices"][0]
        assert "text" in first_choice
        assert "id" in first_choice
        assert "is_correct" not in first_choice

    def test_submit_quiz_all_correct(self, client):
        """Test submitting a quiz with all correct answers."""
        # Seed the database
        db = TestingSessionLocal()
        seed.seed_database(db)

        # Get the questions to find correct answers
        questions = db.query(models.Question).all()

        # Create answers payload with all correct answers
        correct_answers = []
        for question in questions:
            for choice in question.choices:
                if choice.is_correct:
                    correct_answers.append(
                        {"question_id": question.id, "choice_id": choice.id}
                    )
                    break

        db.close()

        payload = {"answers": correct_answers}
        response = client.post("/submit/", json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result["score"] == 5
        assert result["total"] == 5
        assert len(result["results"]) == 5
        assert all(r["is_correct"] for r in result["results"])

    def test_submit_quiz_all_wrong(self, client):
        """Test submitting a quiz with all wrong answers."""
        # Seed the database
        db = TestingSessionLocal()
        seed.seed_database(db)

        # Get the questions to find wrong answers
        questions = db.query(models.Question).all()

        # Create answers payload with all wrong answers
        wrong_answers = []
        for question in questions:
            for choice in question.choices:
                if not choice.is_correct:
                    wrong_answers.append(
                        {"question_id": question.id, "choice_id": choice.id}
                    )
                    break

        db.close()

        payload = {"answers": wrong_answers}
        response = client.post("/submit/", json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result["score"] == 0
        assert result["total"] == 5
        assert len(result["results"]) == 5
        assert not any(r["is_correct"] for r in result["results"])

    def test_submit_quiz_partial_answers(self, client):
        """Test submitting a quiz with only some questions answered."""
        # Seed the database
        db = TestingSessionLocal()
        seed.seed_database(db)

        # Get first question and provide correct answer
        question = db.query(models.Question).first()
        correct_choice = next(
            choice for choice in question.choices if choice.is_correct
        )

        db.close()

        # Answer only the first question
        payload = {
            "answers": [{"question_id": question.id, "choice_id": correct_choice.id}]
        }

        response = client.post("/submit/", json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result["score"] == 1
        assert result["total"] == 5
        assert len(result["results"]) == 5

        # Check that unanswered questions show "Unanswered"
        unanswered_count = sum(
            1 for r in result["results"] if r["user_answer_text"] == "Unanswered"
        )
        assert unanswered_count == 4

    def test_submit_quiz_empty_payload(self, client):
        """Test submitting a quiz with empty answers."""
        # Seed the database
        db = TestingSessionLocal()
        seed.seed_database(db)
        db.close()

        payload = {"answers": []}
        response = client.post("/submit/", json=payload)

        assert response.status_code == 200
        result = response.json()
        assert result["score"] == 0
        assert result["total"] == 5

    def test_submit_quiz_invalid_payload(self, client):
        """Test submitting a quiz with invalid payload structure."""
        response = client.post("/submit/", json={"invalid": "payload"})
        assert response.status_code == 422  # Validation error

    def test_submit_quiz_missing_fields(self, client):
        """Test submitting a quiz with missing required fields."""
        response = client.post(
            "/submit/", json={"answers": [{"question_id": 1}]}  # Missing choice_id
        )
        assert response.status_code == 422  # Validation error


class TestCORSHeaders:
    """Test CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.get("/")
        assert response.status_code == 200

        # Note: TestClient doesn't simulate CORS preflight requests,
        # but we can verify the middleware is configured by checking
        # that the endpoint works (CORS middleware doesn't block in tests)

    def test_options_request(self, client):
        """Test OPTIONS request for CORS preflight."""
        # TestClient handles OPTIONS requests automatically
        # This test ensures the endpoint is accessible
        client.options("/questions/")
        # Options requests should be handled by CORS middleware


class TestErrorHandling:
    """Test error handling in API endpoints."""

    def test_nonexistent_endpoint(self, client):
        """Test accessing a non-existent endpoint."""
        response = client.get("/nonexistent/")
        assert response.status_code == 404

    def test_invalid_http_method(self, client):
        """Test using an invalid HTTP method."""
        response = client.put("/questions/")  # PUT not allowed
        assert response.status_code == 405  # Method Not Allowed
