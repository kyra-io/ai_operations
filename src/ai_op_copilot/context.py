from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from .models import Message


class ContextRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ContextMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    role: ContextRole

    content: str


class Context(BaseModel):
    model_config = ConfigDict(frozen=True)

    messages: tuple[ContextMessage, ...]


class ContextBuilder:
    def build(self, messages: list[Message]) -> Context:
        context_messages = tuple(
            ContextMessage(
                role=ContextRole(message.role.value),
                content=message.content,
            )
            for message in messages
        )
        return Context(messages=context_messages)
