# from pydantic import BaseModel
# from datetime import datetime
# from typing import List, Optional
# from uuid import UUID
# from pydantic import BaseModel, EmailStr
# from enum import Enum


# class RequestQuestion(BaseModel):
#     question: str


# class ResponseQuestion(BaseModel):
#     response: str


# class QueryRequest(BaseModel):
#     question: str


# class QueryResponse(BaseModel):
#     answer: str
#     response_time: float


# # //////////////////////////////


# class Role(str, Enum):
#     manager = "manager"
#     employee = "employee"


# class Gender(str, Enum):
#     male = "male"
#     female = "female"


# class User(BaseModel):
#     # user_id: Optional[UUID] = Field(default_factory=uuid4)
#     full_name: str
#     gender: Gender
#     role: Role


# class ResponseUsers(BaseModel):
#     user_id: UUID
#     full_name: str
#     gender: Gender
#     role: str
#     created_at: datetime

#     class Config:
#         orm_mode = True


# # class UserUpdateRequest(BaseModel):
# #     first_name: Optional[str] = None
# #     middle_name: Optional[str] = None
# #     last_name: Optional[str] = None
# #     roles: Optional[List[Role]] = []


# # class DeleteUser(BaseModel):
# #     user_id: UUID

# #     class Config:
# #         orm_mode = True


# class UserLoginRequest(BaseModel):
#     email: EmailStr
#     password: str


# class UserLoginResponse(BaseModel):
#     _id: UUID
#     full_name: str
#     email: EmailStr
#     gender: Gender
#     role: Role
#     created_at: datetime

#     class Config:
#         orm_mode = True


# class Token(BaseModel):
#     access_token: str
#     token_type: str

#     class Config:
#         orm_mode = True


# class TokenData(BaseModel):
#     employee_id: str


# # Task related schemas
# class Task(BaseModel):
#     # task_id: UUID
#     # employee_id: UUID
#     task_title: str
#     task_description: Optional[str] = None
#     # task_status: str
#     # task_start_date: str
#     # task_end_date: str
#     # created_at: datetime


# class ResponseTask(BaseModel):
#     task_id: UUID
#     employee_id: UUID
#     task_title: str
#     task_description: Optional[str]
#     created_at: datetime

#     class Config:
#         orm_mode = True


# class TaskUpdateRequest(BaseModel):
#     task_title: Optional[str] = None
#     task_description: Optional[str] = None

# -------------------------------------------------------
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# ---------------------------
# User Schemas
# ---------------------------
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
    extracted_text: Optional[str] = None


class SOPCreate(SOPBase):
    file_data: bytes  # uploaded as blob


class SOPRead(SOPBase):
    id: int
    manager_id: int
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
        from_attributes = True
