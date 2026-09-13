from typing import Protocol

from ..models import Conversation


class ConversationRepository(Protocol):
    def create(self, conversation: Conversation) -> None: ...
