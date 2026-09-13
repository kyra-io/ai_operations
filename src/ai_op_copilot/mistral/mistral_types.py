from pydantic import BaseModel, ConfigDict


class LLM_Usage(BaseModel):
    model_config = ConfigDict(frozen=True)

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLM_Res(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    model: str
    usage: LLM_Usage
    role: str
    message: str
    # latency_ms: int


class LLM_Err(BaseModel):
    message: str
