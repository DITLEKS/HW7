from typing import Annotated

import jwt
from fastapi import Header, HTTPException, status

from app.config import settings

_BEARER_PREFIX = "Bearer "


def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> int:
    """
    Извлекает и валидирует JWT из заголовка Authorization.

    Возвращает user_id при успехе.
    Raises:
        400 — заголовок отсутствует, неверный формат или невалидная подпись
        401 — токен просрочен
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка",
        )
    if not authorization.startswith(_BEARER_PREFIX):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка",
        )

    token = authorization[len(_BEARER_PREFIX):]

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return int(payload["user_id"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка",
        )
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка",
        )
