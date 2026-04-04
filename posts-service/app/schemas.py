from pydantic import BaseModel, field_validator


class PostMessage(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Сообщение не может быть пустым")
        return v
