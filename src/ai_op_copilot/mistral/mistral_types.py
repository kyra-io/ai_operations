from pydantic import BaseModel


class LLM_Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLM_Res(BaseModel):
    id: str
    model: str
    usage: LLM_Usage
    role: str
    message: str
    # latency_ms: int


class LLM_Err(BaseModel):
    message: str
