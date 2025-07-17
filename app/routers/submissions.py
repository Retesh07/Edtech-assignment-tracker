"""Routes for student submissions and teacher viewing them."""
from typing import List
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .. import models, schemas
from ..database import get_session
from ..deps import student_only, teacher_only

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(prefix="/assignments/{assignment_id}/submissions", tags=["submissions"])


@router.post("/", response_model=schemas.SubmissionOut, status_code=status.HTTP_201_CREATED)
async def create_submission(
    assignment_id: int,
    text_answer: str = Form(None),
    file: UploadFile | None = File(None),
    student: models.User = Depends(student_only),
    session: AsyncSession = Depends(get_session),
):
    # check assignment exists
    assignment = await session.get(models.Assignment, assignment_id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")

    file_url = None
    if file is not None:
        dest = UPLOAD_DIR / f"a{assignment_id}_u{student.id}_{file.filename}"
        content = await file.read()
        dest.write_bytes(content)
        file_url = dest.as_posix()

    sub = models.Submission(
        assignment_id=assignment_id,
        student_id=student.id,
        text_answer=text_answer,
        file_url=file_url,
    )
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub


@router.get("/", response_model=List[schemas.SubmissionOut])
async def list_submissions(
    assignment_id: int,
    teacher: models.User = Depends(teacher_only),
    session: AsyncSession = Depends(get_session),
):
    # verify assignment belongs to teacher
    assignment = await session.get(models.Assignment, assignment_id)
    if not assignment or assignment.teacher_id != teacher.id:
        raise HTTPException(404, "Assignment not found or not yours")

    result = await session.execute(
        select(models.Submission).where(models.Submission.assignment_id == assignment_id)
    )
    return result.scalars().all()
