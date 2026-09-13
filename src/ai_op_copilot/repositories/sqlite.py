import sqlite3
from contextlib import closing
from pathlib import Path

from ..models import Conversation


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
