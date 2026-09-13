from .mistral.mistral import Mistral

client = Mistral()


def main():
    print("---LLM CLI---")
    input = ask_user()
    output = client.mistral_req(input)

    if output is not None:
        if output.message is not None:
            print(output.message)
    else:
        return


def ask_user():
    user_input = input("Ask a question: ")

    data = {"role": "user", "content": user_input}
    return data


if __name__ == "__main__":
    main()
