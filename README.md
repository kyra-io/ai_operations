# AI OP Copilot

AI OP Copilot is a Python chat service built with FastAPI and the Mistral API.
It supports multiple conversations, persists conversation history in SQLite,
and sends server-managed context to the language model on each turn.

Author: Pedro Santo.

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A Mistral API key and model identifier

## Setup

Install the locked project dependencies from the repository root:

```sh
uv sync --locked
```

Create a `.env` file in the repository root:

```dotenv
MISTRAL_API_KEY=<your API key>
MISTRAL_MODEL=<model identifier>
```

The `.env` file is excluded from Git.

## Running the application

Start the FastAPI server:

```sh
uv run ai-op-copilot
```

The server listens on `http://127.0.0.1:8000`. Interactive API documentation
is available at `http://127.0.0.1:8000/docs`.

For development with automatic reload and debug logging:

```sh
uv run ai-op-copilot --dev
```

Development mode binds the server to `0.0.0.0:8000`.

The original one-shot CLI remains available:

```sh
uv run ai-op-copilot --cli
```

The package can also be started with:

```sh
uv run python -m ai_op_copilot
```

## API

### Health check

```http
GET /health
```

### Create a conversation

```http
POST /conversations
```

The request has no body. The server creates the conversation ID and timestamp,
persists them in SQLite, and returns the new conversation:

```json
{
  "id": "3c13b4e6-4e8a-4fb8-9a21-9c0345d46271",
  "created_at": "2026-09-22T10:30:00Z"
}
```

### List conversations

```http
GET /conversations
```

### Send a message

```http
POST /conversations/{conversation_id}/messages
Content-Type: application/json
```

```json
{
  "content": "What did we discuss in the previous turn?"
}
```

The server performs the complete chat turn:

1. It validates and persists the user message.
2. It loads the conversation history from SQLite.
3. `ContextBuilder` converts that history into LLM context.
4. `LLMClient` sends the context to Mistral.
5. It persists and returns the assistant message.

The client only sends the new message. It does not resend conversation history.

If the LLM request fails, the user message remains in the conversation, no
assistant message is created, and the endpoint returns `502 Bad Gateway`.

### Get conversation history

```http
GET /conversations/{conversation_id}/messages
```

Messages are returned in chronological order. A missing conversation returns
`404 Not Found`; an existing conversation without messages returns an empty
list.

## Architecture

The main responsibilities are separated as follows:

- `Conversation` and `Message` represent persisted chat data.
- `ConversationRepository` and `MessageRepository` define persistence
  contracts.
- `SQLiteConversationRepository` and `SQLiteMessageRepository` implement
  those contracts with SQLite.
- `Context` represents the data sent to the LLM for one turn.
- `ContextBuilder` converts persisted messages into context. It currently uses
  the full conversation history.
- `LLMClient` defines a provider-independent language model contract.
- `Mistral` adapts the Mistral SDK to the `LLMClient` contract.
- `ChatService` coordinates conversation creation, persistence, context
  construction, and model calls.
- The FastAPI layer validates HTTP data and translates application errors into
  HTTP responses.

The current request flow is:

```text
FastAPI
   |
   v
ChatService
   |-- ConversationRepository --> SQLite
   |-- MessageRepository -------> SQLite
   |-- ContextBuilder
   `-- LLMClient ---------------> Mistral API
```

The SQLite database is created at `data/conversations.db`. The `data/`
directory is excluded from Git.

## Project structure

```text
src/ai_op_copilot/
    __init__.py
    __main__.py
    main.py
    cli.py
    models.py
    errors.py
    context.py
    llm.py
    chat_service.py
    api/
        __init__.py
        schemas.py
        server.py
    repositories/
        __init__.py
        conversations.py
        messages.py
        sqlite.py
    mistral/
        __init__.py
        mistral.py
        mistral_types.py
tests/
    test_chat_chat_service.py
```

## Tests

Run the test suite with:

```sh
uv run python -m unittest discover -s tests -v
```

The current tests use a temporary SQLite database and fake LLM clients. They
verify context continuity across multiple turns and confirm that a failed LLM
request preserves the user message without creating an assistant response.
They do not call the real Mistral API.

## Dependency management

The project uses the uv project workflow:

```sh
uv add <package>
uv remove <package>
uv lock
uv sync --locked
```

Direct dependencies are declared in `pyproject.toml`, while `uv.lock` pins the
complete dependency graph.

## Current limitations

- Context currently contains the entire conversation history; there is no token
  budget, sliding window, summarization, system prompt, long-term memory, or
  retrieval-augmented generation yet.
- SQLite persistence is intended for the current single-instance stage. Chat
  turns are not yet serialized per conversation, so concurrent requests for the
  same conversation can build context from overlapping state.
- There is no authentication or ownership model for conversations.
- LLM usage and provider response metadata are returned internally by the
  adapter but are not persisted.
- The legacy CLI still uses its original single-question integration path.

To build package distributions in `dist/`, run:

```sh
uv build
```

## License

Copyright 2026 Pedro Santo.

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
