from typing import Protocol
from uuid import UUID

from ..models import Message


class MessageRepository(Protocol):
    def create(self, message: Message) -> None: ...

    def list_by_conversation(self, conversation_id: UUID) -> list[Message]: ...
