"""HTTP adapter for Nova's fictional return demo.

Run with: uvicorn nova.api:app --reload
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from nova.__main__ import build_service
from nova.service import WorkflowService


class ChatRequest(BaseModel):
    conversation_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    next_step: str
    status: str


def create_app(service: WorkflowService | None = None) -> FastAPI:
    """Application factory permits isolated API tests and adapter injection."""
    app = FastAPI(title="Nova — Store Operations Agent", version="0.1.0")
    app.state.workflow_service = service if service is not None else build_service(
        demo=True, db_path=os.environ.get("NOVA_DB_PATH", "nova_state.sqlite3")
    )
    web_dir = Path(__file__).resolve().parent / "web"
    app.mount("/ui", StaticFiles(directory=web_dir), name="ui")

    @app.get("/", include_in_schema=False)
    def home() -> FileResponse:
        return FileResponse(web_dir / "index.html")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest) -> ChatResponse:
        if not request.conversation_id.strip() or not request.message.strip():
            from fastapi import HTTPException
            raise HTTPException(status_code=422, detail="conversation_id and message cannot be blank")
        reply, state = app.state.workflow_service.handle_message(
            request.conversation_id, request.message
        )
        return ChatResponse(
            conversation_id=request.conversation_id,
            reply=reply,
            next_step=state.next_step.value,
            status=state.status.value,
        )

    return app


app = create_app()
