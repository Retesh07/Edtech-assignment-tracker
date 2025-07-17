from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .. import models, schemas
from ..database import get_session
from ..deps import teacher_only, student_only, get_current_user

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/", response_model=schemas.AssignmentOut, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_in: schemas.AssignmentCreate,
    teacher: models.User = Depends(teacher_only),
    session: AsyncSession = Depends(get_session),
):
    new_assgn = models.Assignment(
        title=assignment_in.title,
        description=assignment_in.description,
        due_date=assignment_in.due_date,
        teacher_id=teacher.id,
    )
    session.add(new_assgn)
    await session.commit()
    await session.refresh(new_assgn)
    return new_assgn


@router.get("/", response_model=List[schemas.AssignmentOut])
async def list_assignments(
    mine: Optional[bool] = None,
    user: models.User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(models.Assignment)
    if mine is True and user.role == "teacher":
        stmt = stmt.where(models.Assignment.teacher_id == user.id)
    result = await session.execute(stmt.order_by(models.Assignment.created_at.desc()))
    return result.scalars().all()
