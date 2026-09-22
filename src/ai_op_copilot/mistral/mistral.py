import os
from dotenv import load_dotenv

from mistralai.client import Mistral as mistral
from mistralai.client.models import (
    AssistantMessage,
    ChatCompletionRequestMessage,
    SystemMessage,
    UserMessage,
)

from .mistral_types import LLM_Res, LLM_Err
from ..context import Context, ContextRole
from ..llm import LLMResult, LLMUsage
from ..errors import LLMError

load_dotenv()


class Mistral:
    API_KEY = os.getenv("MISTRAL_API_KEY")
    MODEL = os.getenv("MISTRAL_MODEL")

    MISTRAL_CLIENT = mistral(api_key=API_KEY)

    def mistral_req(self, input):
        if self.API_KEY is None:
            msg = {"message": "Missing Mistral API KEY"}
            msg = LLM_Err(**msg)
            return msg
        if self.MODEL is None:
            msg = {"message": "Missing Mistral Model"}
            msg = LLM_Err(**msg)
            return msg

        try:
            response = self.MISTRAL_CLIENT.chat.complete(
                model=self.MODEL,
                messages=[{"role": input["role"], "content": input["content"]}],
            )
        except Exception as error:
            raise LLMError("Mistral request failed") from error

        if (
            response
            and response.choices
            and response.choices[0].message
            and response.choices[0].message.content
        ):
            chat_res = {
                "id": response.id,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "role": response.choices[0].message.role,
                "message": response.choices[0].message.content,
                "latency_ms": "",
            }

            chat_res = LLM_Res(**chat_res)
            return chat_res

        return None

    def generate(self, context: Context) -> LLMResult:
        if self.API_KEY is None:
            raise LLMError("Missing Mistral API KEY")

        if self.MODEL is None:
            raise LLMError("Missing Mistral model")

        messages: list[ChatCompletionRequestMessage] = []

        for message in context.messages:
            match message.role:
                case ContextRole.USER:
                    messages.append(UserMessage(content=message.content))
                case ContextRole.ASSISTANT:
                    messages.append(AssistantMessage(content=message.content))
                case ContextRole.SYSTEM:
                    messages.append(SystemMessage(content=message.content))

        try:
            response = self.MISTRAL_CLIENT.chat.complete(
                model=self.MODEL,
                messages=messages,
            )
        except Exception as error:
            raise LLMError("Mistral request failed") from error

        if not response or not response.choices or not response.choices[0].message:
            raise LLMError("Mistral returned an invalid response")

        content = response.choices[0].message.content

        if not isinstance(content, str) or not content:
            raise LLMError("Mistral returned an empty response")

        usage = None

        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens

        if (
            prompt_tokens is not None
            and completion_tokens is not None
            and total_tokens is not None
        ):
            usage = LLMUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )

        return LLMResult(
            content=content,
            provider_response_id=response.id,
            model=response.model,
            usage=usage,
        )
