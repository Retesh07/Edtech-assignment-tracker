"""Pydantic schemas for request/response bodies."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = Field(pattern="^(student|teacher)$")


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        orm_mode = True


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class AssignmentOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True


class SubmissionCreate(BaseModel):
    text_answer: Optional[str] = None


class SubmissionOut(BaseModel):
    id: int
    text_answer: Optional[str]
    file_url: Optional[str]
    submitted_at: datetime
    student: UserOut

    class Config:
        orm_mode = True


class AssignmentWithSubs(AssignmentOut):
    submissions: List[SubmissionOut] = []
