import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from ai_op_copilot.chat_service import ChatService
from ai_op_copilot.context import Context, ContextBuilder, ContextRole
from ai_op_copilot.errors import LLMError
from ai_op_copilot.llm import LLMResult
from ai_op_copilot.models import MessageRole
from ai_op_copilot.repositories.sqlite import (
    SQLiteConversationRepository,
    SQLiteMessageRepository,
)


class FakeLLMClient:
    def __init__(self):
        self.received_contexts: list[Context] = []

    def generate(self, context: Context) -> LLMResult:
        self.received_contexts.append(context)
        return LLMResult(content="Resposta simulada")


class FailingLLMClient:
    def generate(self, context: Context) -> LLMResult:
        raise LLMError("Simulated LLM failure")


class ChatServiceTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)

        db_path = Path(self.temporary_directory.name) / "test.db"

        self.conversation_repository = SQLiteConversationRepository(db_path)
        self.message_repository = SQLiteMessageRepository(db_path)
        self.conversation_repository.initialize()

    def test_send_message_preserves_context_between_turns(self):
        llm_client = FakeLLMClient()

        service = ChatService(
            conversation_repository=self.conversation_repository,
            message_repository=self.message_repository,
            context_builder=ContextBuilder(),
            llm_client=llm_client,
        )

        conversation = service.create_conversation()

        service.send_message(conversation.id, "Primeira pergunta")
        service.send_message(conversation.id, "Segunda pergunta")

        history = service.get_conversation_messages(conversation.id)

        self.assertEqual(
            [message.role for message in history],
            [
                MessageRole.USER,
                MessageRole.ASSISTANT,
                MessageRole.USER,
                MessageRole.ASSISTANT,
            ],
        )

        self.assertEqual(
            [message.content for message in history],
            [
                "Primeira pergunta",
                "Resposta simulada",
                "Segunda pergunta",
                "Resposta simulada",
            ],
        )

        second_context = llm_client.received_contexts[1]

        self.assertEqual(
            [message.role for message in second_context.messages],
            [
                ContextRole.USER,
                ContextRole.ASSISTANT,
                ContextRole.USER,
            ],
        )

    def test_llm_failure_preserves_user_message(self):
        service = ChatService(
            conversation_repository=self.conversation_repository,
            message_repository=self.message_repository,
            context_builder=ContextBuilder(),
            llm_client=FailingLLMClient(),
        )

        conversation = service.create_conversation()

        with self.assertRaises(LLMError):
            service.send_message(
                conversation.id,
                "Mensagem antes da falha",
            )

        history = service.get_conversation_messages(conversation.id)

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].role, MessageRole.USER)
        self.assertEqual(
            history[0].content,
            "Mensagem antes da falha",
        )


if __name__ == "__main__":
    unittest.main()
