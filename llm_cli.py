import os
from dotenv import load_dotenv
from pydantic import BaseModel, PositiveInt
import json
from mistralai.client import Mistral as mistral

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL = "open-mistral-nemo-2407"

MISTRAL_CLIENT = mistral(api_key=API_KEY)


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


def main():
    print("---LLM CLI---")
    input = ask_user()
    output = mistral_req(input)

    if output is not None:
        if output.message is not None:
            print(output.message)


def ask_user():
    user_input = input("Ask a question: ")

    data = {"role": "user", "content": user_input}
    return data


def mistral_req(input):
    response = MISTRAL_CLIENT.chat.complete(
        model=MODEL, messages=[{"role": input["role"], "content": input["content"]}]
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
                "completion_tokes": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "role": response.choices[0].message.role,
            "message": response.choices[0].message.content,
        }

        chat_res = LLM_Res(**chat_res)
        return chat_res

    return None


if __name__ == "__main__":
    main()
