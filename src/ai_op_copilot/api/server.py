from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, APIRouter

from ..chat_service import ChatService
from ..repositories.sqlite import SQLiteConversationRepository, SQLiteMessageRepository
from ..models import Conversation, Message
from ..errors import ConversationNotFoundError, LLMError
from .schemas import CreateMessageRequest
from ..context import ContextBuilder
from ..mistral.mistral import Mistral


def build_chat_service() -> ChatService:
    project_root = Path(__file__).resolve().parents[3]
    data_directory = project_root / "data"
    data_directory.mkdir(parents=True, exist_ok=True)

    db_path = data_directory / "conversations.db"

    conversation_repository = SQLiteConversationRepository(db_path=db_path)
    message_repository = SQLiteMessageRepository(db_path=db_path)

    conversation_repository.initialize()

    return ChatService(
        conversation_repository=conversation_repository,
        message_repository=message_repository,
        context_builder=ContextBuilder(),
        llm_client=Mistral(),
    )


router = APIRouter()


@router.get("/")
def read_root():
    return {"Hello World"}


@router.get("/health", status_code=200)
def check_health():
    return {"status": "200 OK", "message": "KyraIO - AI Operations Copilot is running"}


@router.post("/conversations", response_model=Conversation, status_code=201)
def create_conversation(request: Request) -> Conversation:
    service: ChatService = request.app.state.chat_service
    return service.create_conversation()


@router.get("/conversations", response_model=list[Conversation], status_code=200)
def get_all_conversations(request: Request) -> list[Conversation]:
    service: ChatService = request.app.state.chat_service
    return service.get_all_conversations()


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=Message,
    status_code=201,
)
def create_user_message(
    conversation_id: UUID,
    payload: CreateMessageRequest,
    request: Request,
) -> Message:
    service: ChatService = request.app.state.chat_service

    try:
        return service.send_message(
            conversation_id=conversation_id,
            content=payload.content,
        )
    except ConversationNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error
    except LLMError as error:
        raise HTTPException(status_code=502, detail="The LLM request failed") from error


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[Message],
    status_code=200,
)
def get_conversation_messages(
    conversation_id: UUID,
    request: Request,
) -> list[Message]:
    service: ChatService = request.app.state.chat_service

    try:
        return service.get_conversation_messages(conversation_id)
    except ConversationNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


def create_app(
    chat_service: ChatService | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.chat_service = (
            chat_service if chat_service is not None else build_chat_service()
        )

        yield

    application = FastAPI(lifespan=lifespan)
    application.include_router(router)

    return application


app = create_app()
