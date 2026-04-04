from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import TokenResponse, UserLogin, UserRegister

router = APIRouter()
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: UserRegister, db: Session = Depends(get_db)) -> None:
    """Регистрация нового пользователя."""
    hashed_password = _pwd_context.hash(body.password)
    user = User(email=str(body.email), password=hashed_password)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )


@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
def login(body: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    """Аутентификация: возвращает JWT-токен при успехе."""
    user = db.query(User).filter(User.email == str(body.email)).first()

    if user is None or not _pwd_context.verify(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user.id,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return TokenResponse(token=token)
