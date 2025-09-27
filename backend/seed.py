from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models

# Ensure tables are created
models.Base.metadata.create_all(bind=engine)


def seed_database(db: Session):
    """
    Populates the database with initial quiz questions and choices.
    This function can be called by tests or run as a standalone script.
    """
    # Clear existing data to prevent duplicates
    db.query(models.Choice).delete()
    db.query(models.Question).delete()
    db.commit()

    questions_data = [
        {
            "text": "What is the primary web framework used in this application's backend?",
            "choices": [
                {"text": "Django", "is_correct": False},
                {"text": "FastAPI", "is_correct": True},
                {"text": "Flask", "is_correct": False},
            ],
        },
        {
            "text": "Which library is used for data validation and settings management in FastAPI?",
            "choices": [
                {"text": "Marshmallow", "is_correct": False},
                {"text": "Pydantic", "is_correct": True},
                {"text": "Voluptuous", "is_correct": False},
            ],
        },
        {
            "text": "What does ASGI stand for in the context of Python web servers like Uvicorn?",
            "choices": [
                {"text": "Asynchronous Server Gateway Interface", "is_correct": True},
                {"text": "Automated Server Gateway Interaction", "is_correct": False},
                {
                    "text": "Asynchronous Standard Gateway Interface",
                    "is_correct": False,
                },
            ],
        },
        {
            "text": "Which frontend framework is this project planned to use?",
            "choices": [
                {"text": "Next.js", "is_correct": True},
                {"text": "React (CRA)", "is_correct": False},
                {"text": "Vue.js", "is_correct": False},
            ],
        },
        {
            "text": "What type of database is being used in this project?",
            "choices": [
                {"text": "PostgreSQL", "is_correct": False},
                {"text": "MySQL", "is_correct": False},
                {"text": "SQLite", "is_correct": True},
            ],
        },
    ]

    for q_data in questions_data:
        question = models.Question(text=q_data["text"])
        db.add(question)
        db.flush()  # Flush to get the question ID for choices
        for c_data in q_data["choices"]:
            choice = models.Choice(
                text=c_data["text"],
                is_correct=c_data["is_correct"],
                question_id=question.id,
            )
            db.add(choice)

    db.commit()
    print("Database has been seeded with initial data.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
