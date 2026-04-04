from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_id
from app.models import Message
from app.schemas import PostMessage

router = APIRouter()


@router.post("/posts", status_code=201)
def create_post(
    body: PostMessage,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> None:
    """Сохраняет сообщение от аутентифицированного пользователя."""
    message = Message(
        user_id=user_id,
        time=datetime.now(timezone.utc),
        message=body.message,
    )
    db.add(message)
    db.commit()
