from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.auth import get_current_user
from backend.rag import get_rag_response

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@router.post("/chat")
async def chat(request: ChatRequest, user=Depends(get_current_user)):
    messages = [m.model_dump() for m in request.messages]
    response = get_rag_response(messages)
    return {"response": response}
