from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_manager: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------
# SOP Schemas
# ---------------------------
class SOPBase(BaseModel):
    # extracted_text: Optional[str] = None
    # title: str
    # file_name: str
    extracted_text: Optional[str] = None


class SOPCreate(SOPBase):
    file_name: str
    file_data: bytes  # upload as blob


class SOPRead(SOPBase):
    id: int
    manager_id: int
    file_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------
# Training Module Schemas
# ---------------------------
class TrainingStepBase(BaseModel):
    title: str
    description: Optional[str] = None
    substeps: Optional[List[Dict[str, Any]]] = []
    order: int


class TrainingStepCreate(TrainingStepBase):
    pass


class TrainingStepRead(TrainingStepBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TrainingModuleBase(BaseModel):
    pass


class TrainingModuleCreate(TrainingModuleBase):
    sop_id: int


class TrainingModuleRead(TrainingModuleBase):
    id: int
    sop_id: int
    created_at: datetime
    steps: List[TrainingStepRead] = []

    class Config:
        from_attributes = True


# ---------------------------
# Quiz Schemas
# ---------------------------
class QuizQuestionBase(BaseModel):
    question_text: str
    question_type: str  # "mcq", "true_false", "open"
    options: Optional[List[str]] = None
    correct_answer: Optional[Any] = None


class QuizQuestionCreate(QuizQuestionBase):
    pass


class QuizQuestionRead(QuizQuestionBase):
    id: int

    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    pass


class QuizCreate(QuizBase):
    module_id: int


class QuizRead(QuizBase):
    id: int
    module_id: int
    created_at: datetime
    questions: List[QuizQuestionRead] = []

    class Config:
        from_attributes = True


# ---------------------------
# Quiz Attempt Schemas
# ---------------------------
class QuizAttemptBase(BaseModel):
    answers: Dict[str, Any]  # employee’s answers
    score: Optional[int] = None


class QuizAttemptCreate(QuizAttemptBase):
    quiz_id: int
    employee_id: int


class QuizAttemptRead(QuizAttemptBase):
    id: int
    employee_id: int
    quiz_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class SOPReadLogin(BaseModel):
    id: int
    filename: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginWithSOPResponse(BaseModel):
    id: int
    name: str
    email: str
    is_manager: bool

    sops: List[SOPReadLogin] = []

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    question: str
    # sop_ids: list[int]


class ChatResponse(BaseModel):
    question: str
    answer: str
    sop_ids: List[int]
    sop_title: str | None
