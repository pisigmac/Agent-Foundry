from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel
from services.async_podcast_agent_service import podcast_agent_service

router = APIRouter()

class SessionRequest(BaseModel):
    context_id: Optional[str] = None

class ChatRequest(BaseModel):
    context_id: str
    message: str

class ChatResponse(BaseModel):
    context_id: str
    response: str
    stage: str
    session_state: str
    is_processing: bool = False
    process_type: Optional[str] = None
    task_id: Optional[str] = None
    browser_recording_path: Optional[str] = None

class StatusRequest(BaseModel):
    context_id: str
    task_id: Optional[str] = None  

@router.post("/session")
async def create_session(request: SessionRequest = None):
    """Create or reuse a session with the podcast assistant"""
    return await podcast_agent_service.create_session(request)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the podcast assistant and get a response"""
    return await podcast_agent_service.chat(request)

@router.post("/status", response_model=ChatResponse)
async def check_status(request: StatusRequest):
    """Check if a result is available for the session"""
    return await podcast_agent_service.check_result_status(request)

@router.get("/sessions")
async def list_sessions(page: int = 1, per_page: int = 10):
    """List all saved podcast sessions with pagination"""
    return await podcast_agent_service.list_sessions(page, per_page)

@router.get("/session_history")
async def get_session_history(context_id: str):
    """Get the complete message history for a session"""
    return await podcast_agent_service.get_session_history(context_id)

@router.delete("/session/{context_id}")
async def delete_session(context_id: str):
    """Delete a podcast session and all its data"""
    return await podcast_agent_service.delete_session(context_id)

@router.get("/languages")
async def get_supported_languages():
    """Get the list of supported languages"""
    return await podcast_agent_service.get_supported_languages()
