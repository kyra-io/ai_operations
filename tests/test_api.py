import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from fastapi.testclient import TestClient

from ai_op_copilot.api.server import create_app
from ai_op_copilot.chat_service import ChatService
from ai_op_copilot.context import Context, ContextBuilder
from ai_op_copilot.llm import LLMResult
from ai_op_copilot.repositories.sqlite import (
    SQLiteConversationRepository,
    SQLiteMessageRepository,
)
from ai_op_copilot.errors import LLMError


class FakeLLMClient:
    def __init__(self):
        self.should_fail = False

    def generate(self, context: Context) -> LLMResult:
        if self.should_fail:
            raise LLMError("Simulated LLM failure")

        return LLMResult(content="Simulated response")


class APITest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.llm_client = FakeLLMClient()

        db_path = Path(self.temporary_directory.name) / "test.db"

        conversation_repository = SQLiteConversationRepository(db_path)
        message_repository = SQLiteMessageRepository(db_path)
        conversation_repository.initialize()

        chat_service = ChatService(
            conversation_repository=conversation_repository,
            message_repository=message_repository,
            context_builder=ContextBuilder(),
            llm_client=self.llm_client,
        )

        self.client = TestClient(create_app(chat_service=chat_service))
        self.client.__enter__()

        self.addCleanup(
            self.client.__exit__,
            None,
            None,
            None,
        )

    def test_create_and_list_conversations(self):
        create_response = self.client.post("/conversations")

        self.assertEqual(create_response.status_code, 201)

        created_conversation = create_response.json()

        self.assertIn("id", created_conversation)
        self.assertIn("created_at", created_conversation)

        list_response = self.client.get("/conversations")

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(
            list_response.json(),
            [created_conversation],
        )

    def test_send_message_and_get_conversation_history(self):
        create_response = self.client.post("/conversations")
        conversation_id = create_response.json()["id"]

        message_response = self.client.post(
            f"/conversations/{conversation_id}/messages",
            json={"content": "Hello"},
        )

        self.assertEqual(message_response.status_code, 201)

        assistant_message = message_response.json()

        self.assertEqual(assistant_message["conversation_id"], conversation_id)
        self.assertEqual(assistant_message["role"], "assistant")
        self.assertEqual(assistant_message["content"], "Simulated response")

        history_response = self.client.get(f"/conversations/{conversation_id}/messages")

        self.assertEqual(history_response.status_code, 200)

        history = history_response.json()

        self.assertEqual(len(history), 2)

        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello")

        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Simulated response")

    def test_send_message_to_nonexistent_conversation_returns_404(self):
        conversation_id = uuid4()

        response = self.client.post(
            f"/conversations/{conversation_id}/messages",
            json={"content": "Hello"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {"detail": (f"Conversation {conversation_id} was not found")},
        )

    def test_empty_messages_return_422_and_are_not_stored(self):
        create_response = self.client.post("/conversations")
        conversation_id = create_response.json()["id"]

        invalid_contents = ["", " "]

        for content in invalid_contents:
            with self.subTest(content=repr(content)):
                response = self.client.post(
                    f"/conversations/{conversation_id}/messages",
                    json={"content": content},
                )

                self.assertEqual(response.status_code, 422)
        history_response = self.client.get(f"/conversations/{conversation_id}/messages")

        self.assertEqual(history_response.json(), [])
        self.assertEqual(history_response.status_code, 200)

    def test_llm_failure_returns_502(self):
        create_response = self.client.post("/conversations")
        conversation_id = create_response.json()["id"]

        self.llm_client.should_fail = True

        response = self.client.post(
            f"/conversations/{conversation_id}/messages",
            json={"content": "Hello"},
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(
            response.json(),
            {"detail": "The LLM request failed"},
        )

        history_response = self.client.get(f"/conversations/{conversation_id}/messages")

        self.assertEqual(history_response.status_code, 200)

        history = history_response.json()

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello")


if __name__ == "__main__":
    unittest.main()
