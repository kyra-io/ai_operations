from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request

from ..chat_service import ChatService
from ..repositories.sqlite import SQLiteConversationRepository
from ..models import Conversation


@asynccontextmanager
async def lifespan(app: FastAPI):
    project_root = Path(__file__).resolve().parents[3]
    data_directory = project_root / "data"
    data_directory.mkdir(parents=True, exist_ok=True)

    repository = SQLiteConversationRepository(
        db_path=data_directory / "conversations.db"
    )
    repository.initialize()

    app.state.chat_service = ChatService(repository)

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello World"}


@app.get("/health", status_code=200)
def check_health():
    return {"status": "200 OK", "message": "KyraIO - AI Operations Copilot is running"}


@app.post("/conversations", response_model=Conversation, status_code=201)
def create_conversation(request: Request) -> Conversation:
    service: ChatService = request.app.state.chat_service
    return service.create_conversation()


@app.get("/conversations", response_model=list[Conversation], status_code=200)
def get_all_conversations(request: Request) -> list[Conversation]:
    service: ChatService = request.app.state.chat_service
    return service.get_all_conversations()
