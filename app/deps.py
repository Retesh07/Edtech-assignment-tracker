"""FastAPI dependencies for auth & DB."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from . import auth, models
from .database import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)) -> models.User:
    try:
        payload = auth.decode_token(token)
        user_id: int = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    user = await session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def teacher_only(user: models.User = Depends(get_current_user)) -> models.User:
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    return user


def student_only(user: models.User = Depends(get_current_user)) -> models.User:
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Students only")
    return user
