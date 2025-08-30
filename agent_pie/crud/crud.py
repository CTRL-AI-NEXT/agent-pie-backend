# app/crud/crud.py
from sqlalchemy.orm import Session
from agent_pie.models import models
from agent_pie.schemas import schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -------------------
# User CRUD
# -------------------
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        name=user.name, email=user.email, password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# -------------------
# SOP CRUD
# -------------------
def create_sop(db: Session, sop: schemas.SOPCreate, manager_id: int):
    db_sop = models.SOP(
        file_data=sop.file_data,
        extracted_text=sop.extracted_text,
        manager_id=manager_id,
    )
    db.add(db_sop)
    db.commit()
    db.refresh(db_sop)
    return db_sop


def get_sop(db: Session, sop_id: int):
    return db.query(models.SOP).filter(models.SOP.id == sop_id).first()


def list_sops(db: Session, manager_id: int):
    return db.query(models.SOP).filter(models.SOP.manager_id == manager_id).all()


# -------------------
# Training Modules
# -------------------
def create_training_module(db: Session, sop_id: int):
    module = models.TrainingModule(sop_id=sop_id)
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


def get_training_module(db: Session, module_id: int):
    return (
        db.query(models.TrainingModule)
        .filter(models.TrainingModule.id == module_id)
        .first()
    )


def add_training_steps(db: Session, module_id: int, steps: list):
    for s in steps:
        step = models.TrainingStep(
            module_id=module_id,
            title=s.title,
            description=s.description,
            order=s.order,
            substeps=getattr(s, "substeps", None),
        )
        db.add(step)
    db.commit()


# -------------------
# Quiz CRUD
# -------------------
def create_quiz(db: Session, module_id: int):
    quiz = models.Quiz(module_id=module_id)
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def get_quiz(db: Session, quiz_id: int):
    return db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()


def add_quiz_questions(db: Session, quiz_id: int, questions: list):
    for q in questions:
        question = models.QuizQuestion(
            quiz_id=quiz_id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=getattr(q, "options", None),
            correct_answer=q.correct_answer,
        )
        db.add(question)
    db.commit()


def create_quiz_attempt(db: Session, attempt: schemas.QuizAttemptCreate):
    db_attempt = models.QuizAttempt(
        quiz_id=attempt.quiz_id,
        employee_id=attempt.employee_id,
        answers=attempt.answers,
        score=attempt.score,
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt


def list_quiz_attempts(db: Session, quiz_id: int = None, employee_id: int = None):
    query = db.query(models.QuizAttempt)
    if quiz_id:
        query = query.filter(models.QuizAttempt.quiz_id == quiz_id)
    if employee_id:
        query = query.filter(models.QuizAttempt.employee_id == employee_id)
    return query.all()
