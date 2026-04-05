from datetime import datetime, timedelta, timezone
import re
 
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
 
 
def _validate_password(password: str) -> None:
    """Проверяет надёжность пароля."""
    errors = []
    if len(password) < 8:
        errors.append("не менее 8 символов")
    if not re.search(r"[A-Za-z]", password):
        errors.append("минимум одна буква")
    if not re.search(r"\d", password):
        errors.append("минимум одна цифра")
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль должен содержать: " + ", ".join(errors),
        )
 
 
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: UserRegister, db: Session = Depends(get_db)) -> None:
    """Регистрация нового пользователя."""
    existing_user = db.query(User).filter(User.email == str(body.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )
 
    _validate_password(body.password)
 
    hashed_password = _pwd_context.hash(body.password)
    user = User(email=str(body.email), password=hashed_password)
    db.add(user)
    db.commit()
 
 
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