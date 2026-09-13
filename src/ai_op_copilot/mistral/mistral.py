import os
from dotenv import load_dotenv

from mistralai.client import Mistral as mistral

from .mistral_types import LLM_Res, LLM_Err

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

        response = self.MISTRAL_CLIENT.chat.complete(
            model=self.MODEL,
            messages=[{"role": input["role"], "content": input["content"]}],
        )

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
                    "completion_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "role": response.choices[0].message.role,
                "message": response.choices[0].message.content,
                "latency_ms": "",
            }

            chat_res = LLM_Res(**chat_res)
            return chat_res

        return None
