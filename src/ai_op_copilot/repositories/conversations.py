from typing import Protocol

from ..models import Conversation


class ConversationRepository(Protocol):
    def create(self, conversation: Conversation) -> None: ...

    def get_all(self) -> list[Conversation]: ...
