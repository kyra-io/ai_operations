from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Conversation(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    created_at: datetime
