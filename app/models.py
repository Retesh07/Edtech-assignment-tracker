"""SQLAlchemy models – tiny but expressive."""
import datetime as dt
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False)  # "student" or "teacher"
    is_active = Column(Boolean, default=True)

    assignments = relationship("Assignment", back_populates="teacher", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.id} {self.email}>"


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    teacher = relationship("User", back_populates="assignments")

    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Assignment {self.id} {self.title}>"


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    text_answer = Column(Text)
    file_url = Column(String(255), nullable=True)
    submitted_at = Column(DateTime, default=dt.datetime.utcnow)

    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")

    def __repr__(self):
        return f"<Submission {self.id} by {self.student_id}>"
