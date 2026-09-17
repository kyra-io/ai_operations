from typing import Protocol
from uuid import UUID

from ..models import Conversation


class ConversationRepository(Protocol):
    def create(self, conversation: Conversation) -> None: ...

    def get_all(self) -> list[Conversation]: ...

    def get_by_id(self, conversation_id: UUID) -> Conversation | None: ...
