from datetime import datetime, timezone
from uuid import uuid4

from .models import Conversation
from .repositories.conversations import ConversationRepository


class ChatService:
    def __init__(self, repository: ConversationRepository):
        self.repository = repository

    def create_conversation(self) -> Conversation:
        conversation = Conversation(
            id=uuid4(),
            created_at=datetime.now(timezone.utc),
        )

        self.repository.create(conversation)

        return conversation

    def get_all_conversations(self) -> list[Conversation]:
        return self.repository.get_all()
