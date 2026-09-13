from pydantic import BaseModel, PositiveInt


class LLM_Usage(BaseModel):
    prompt_tokens: int
    completion_tokes: int
    total_tokens: int


class LLM_Res(BaseModel):
    id: str
    model: str
    usage: LLM_Usage
    role: str
    message: str


class LLM_Err(BaseModel):
    message: str
