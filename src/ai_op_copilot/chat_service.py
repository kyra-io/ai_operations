from datetime import datetime, timezone
from uuid import UUID, uuid4

from .models import Conversation, Message, MessageRole
from .repositories.conversations import ConversationRepository
from .repositories.messages import MessageRepository
from .errors import ConversationNotFoundError
from .context import ContextBuilder
from .llm import LLMClient


class ChatService:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        context_builder: ContextBuilder,
        llm_client: LLMClient,
    ):
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.context_builder = context_builder
        self.llm_client = llm_client

    def create_conversation(self) -> Conversation:
        conversation = Conversation(
            id=uuid4(),
            created_at=datetime.now(timezone.utc),
        )

        self.conversation_repository.create(conversation)

        return conversation

    def get_all_conversations(self) -> list[Conversation]:
        return self.conversation_repository.get_all()

    def add_user_message(
        self,
        conversation_id: UUID,
        content: str,
    ) -> Message:
        if not content.strip():
            raise ValueError("Message content cannot be empty")

        conversation = self.conversation_repository.get_by_id(conversation_id)

        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} was not found"
            )

        message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=content,
            created_at=datetime.now(timezone.utc),
        )

        self.message_repository.create(message)

        return message

    def get_conversation_messages(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        conversation = self.conversation_repository.get_by_id(conversation_id)

        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} was not found"
            )
        return self.message_repository.list_by_conversation(conversation_id)

    def send_message(
        self,
        conversation_id: UUID,
        content: str,
    ) -> Message:
        self.add_user_message(
            conversation_id=conversation_id,
            content=content,
        )
        history = self.message_repository.list_by_conversation(conversation_id)

        context = self.context_builder.build(history)

        llm_result = self.llm_client.generate(context)

        assistant_message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=llm_result.content,
            created_at=datetime.now(timezone.utc),
        )

        self.message_repository.create(assistant_message)

        return assistant_message
