"""
AI-First CRM HCP Module - Chat Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4

from app.database import get_db
from app.models import ChatSession, ChatMessage
from app.schemas import ChatSessionCreate, ChatMessageCreate, ChatMessage, ChatSession, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/sessions", response_model=ChatSession)
def create_chat_session(session_data: ChatSessionCreate, db: Session = Depends(get_db)):
    """Create a new chat session."""
    session_token = str(uuid4())
    session = ChatSession(
        user_id=session_data.user_id,
        session_token=session_token,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions/{session_id}", response_model=ChatSession)
def get_chat_session(session_id: int, db: Session = Depends(get_db)):
    """Get a chat session with messages."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.post("/messages", response_model=ChatMessage)
def send_chat_message(message_data: ChatMessageCreate, db: Session = Depends(get_db)):
    """Send a message in a chat session."""
    session = db.query(ChatSession).filter(ChatSession.id == message_data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    message = ChatMessage(
        session_id=message_data.session_id,
        role=message_data.role,
        content=message_data.content,
        metadata_json=message_data.metadata_json,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/messages/{session_id}", response_model=List[ChatMessage])
def get_chat_messages(session_id: int, db: Session = Depends(get_db)):
    """Get all messages for a chat session."""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return messages
