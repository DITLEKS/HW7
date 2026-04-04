import re

from pydantic import BaseModel, EmailStr, field_validator


class UserRegister(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_is_strong(cls, v: str) -> str:
        errors = []
        if len(v) < 8:
            errors.append("не менее 8 символов")
        if not re.search(r"[A-Za-z]", v):
            errors.append("минимум одна буква")
        if not re.search(r"\d", v):
            errors.append("минимум одна цифра")
        if errors:
            raise ValueError("Пароль должен содержать: " + ", ".join(errors))
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str
