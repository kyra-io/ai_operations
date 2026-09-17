from datetime import datetime
from uuid import UUID
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class Conversation(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    created_at: datetime


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
