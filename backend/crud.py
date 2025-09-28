from sqlalchemy.orm import Session, joinedload

from . import models, schemas


def get_questions(db: Session):
    """
    Fetches all questions from the database, eagerly loading their choices.
    """
    return db.query(models.Question).options(joinedload(models.Question.choices)).all()


def calculate_score(db: Session, user_answers: schemas.AnswerPayload):
    """
    Calculates the user's score and provides detailed results for each question.
    """
    score = 0
    all_questions = get_questions(db)

    # Create a quick lookup map of user's answers {question_id: choice_id}
    user_answers_map = {
        answer.question_id: answer.choice_id for answer in user_answers.answers
    }

    # Create a definitive answer key from the database {question_id: correct_choice_id}
    answer_key = {}
    for question in all_questions:
        for choice in question.choices:
            if choice.is_correct:
                answer_key[question.id] = choice.id
                break

    detailed_results = []
    for question in all_questions:
        question_id = question.id
        user_choice_id = user_answers_map.get(question_id)
        correct_choice_id = answer_key.get(question_id)

        is_correct = (user_choice_id is not None) and (
            user_choice_id == correct_choice_id
        )
        if is_correct:
            score += 1

        # Find the text for user's answer and correct answer
        user_answer_text = "Unanswered"
        correct_answer_text = ""

        for choice in question.choices:
            if choice.id == user_choice_id:
                user_answer_text = choice.text
            if choice.id == correct_choice_id:
                correct_answer_text = choice.text

        detailed_results.append(
            schemas.QuestionResult(
                question_id=question.id,
                question_text=question.text,
                user_answer_text=user_answer_text,
                correct_answer_text=correct_answer_text,
                is_correct=is_correct,
            )
        )

    return schemas.QuizResult(
        score=score, total=len(all_questions), results=detailed_results
    )
