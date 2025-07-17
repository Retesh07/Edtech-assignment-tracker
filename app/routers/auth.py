from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import auth as auth_utils, models, schemas
from ..database import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.UserOut)
async def signup(user_in: schemas.UserCreate, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(
        models.User.__table__.select().where(models.User.email == user_in.email)
    )
    if existing.first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        name=user_in.name,
        email=user_in.email,
        password_hash=auth_utils.hash_password(user_in.password),
        role=user_in.role,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.TokenOut)
async def login(form: schemas.LoginIn, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(
        models.User.__table__.select().where(models.User.email == form.email)
    )
    if not user or not auth_utils.verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = auth_utils.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token}
