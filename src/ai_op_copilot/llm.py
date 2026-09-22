from typing import Protocol

from pydantic import BaseModel, ConfigDict

from .context import Context


class LLMUsage(BaseModel):
    model_config = ConfigDict(frozen=True)

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    content: str
    provider_response_id: str | None = None
    model: str | None = None
    usage: LLMUsage | None = None


class LLMClient(Protocol):
    def generate(self, context: Context) -> LLMResult: ...
