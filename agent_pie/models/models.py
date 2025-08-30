from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    TIMESTAMP,
    func,
    LargeBinary,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship
from agent_pie.crud.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=True)
    is_manager = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    sops = relationship("SOP", back_populates="manager")
    quiz_attempts = relationship("QuizAttempt", back_populates="employee")


class SOP(Base):
    __tablename__ = "sops"
    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    file_data = Column(LargeBinary, nullable=False)  # raw PDF stored as blob
    extracted_text = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    manager = relationship("User", back_populates="sops")
    training_module = relationship(
        "TrainingModule", uselist=False, back_populates="sop"
    )


class TrainingModule(Base):
    __tablename__ = "training_modules"
    id = Column(Integer, primary_key=True, index=True)
    sop_id = Column(Integer, ForeignKey("sops.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    sop = relationship("SOP", back_populates="training_module")
    steps = relationship(
        "TrainingStep", back_populates="module", cascade="all, delete-orphan"
    )
    quiz = relationship("Quiz", uselist=False, back_populates="module")


class TrainingStep(Base):
    __tablename__ = "training_steps"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("training_modules.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    substeps = Column(JSON, default=[])  # list of substep dicts
    order = Column(Integer, nullable=False)  # step ordering
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    module = relationship("TrainingModule", back_populates="steps")


class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("training_modules.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    module = relationship("TrainingModule", back_populates="quiz")
    questions = relationship(
        "QuizQuestion", back_populates="quiz", cascade="all, delete-orphan"
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"))
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # "mcq", "true_false", "open"
    options = Column(JSON, nullable=True)  # list of options (for mcq/true_false)
    correct_answer = Column(JSON, nullable=True)  # correct option(s) or keywords

    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"))
    answers = Column(JSON, nullable=False)  # employee’s submitted answers
    score = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    employee = relationship("User", back_populates="quiz_attempts")
