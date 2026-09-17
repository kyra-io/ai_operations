import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import UUID

from ..models import Conversation, Message


class SQLiteConversationRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def initialize(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.execute("""
                   CREATE TABLE IF NOT EXISTS conversations (
                       id TEXT PRIMARY KEY,
                       created_at TEXT NOT NULL
                       )
                   """)
                connection.execute("""
                   CREATE TABLE IF NOT EXISTS messages (
                       id TEXT PRIMARY KEY,
                       conversation_id TEXT NOT NULL,
                       role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                       content TEXT NOT NULL,
                       created_at TEXT NOT NULL,
                       FOREIGN KEY (conversation_id)
                        REFERENCES conversations(id)
                        ON DELETE CASCADE
                       )
                   """)

    def create(self, conversation: Conversation) -> None:
        with closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO conversations (id, created_at)
                    VALUES (?, ?)
                    """,
                    (
                        str(conversation.id),
                        conversation.created_at.isoformat(),
                    ),
                )

    def get_all(self) -> list[Conversation]:
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row

            with connection:
                rows = connection.execute("""
                        SELECT id, created_at
                        FROM conversations
                        ORDER BY created_at DESC
                        """).fetchall()
        return [Conversation.model_validate(dict(row)) for row in rows]

    def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row

            row = connection.execute(
                """
                 SELECT id, created_at
                 FROM conversations
                 WHERE id = ?
                 """,
                (str(conversation_id),),
            ).fetchone()

            return Conversation.model_validate(dict(row))


class SQLiteMessageRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def create(self, message: Message) -> None:
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")

            with connection:
                connection.execute(
                    """
                    INSERT INTO messages (
                        id,
                        conversation_id,
                        role,
                        content,
                        created_at
                        )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        str(message.id),
                        str(message.conversation_id),
                        message.role.value,
                        message.content,
                        message.created_at.isoformat(),
                    ),
                )

    def list_by_conversation(self, conversation_id: UUID) -> list[Message]:
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row

            rows = connection.execute(
                """
                SELECT id, conversation_id, role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (str(conversation_id),),
            ).fetchall()

        return [Message.model_validate(dict(row)) for row in rows]
