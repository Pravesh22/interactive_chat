"""FastAPI application for context-aware chatbot."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import run_agent
from config import SESSION_TIMEOUT

app = FastAPI(
    title="Context-Aware Chatbot API",
    description="API for document queries and appointment booking",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (use Redis in production)
sessions: Dict[str, Dict[str, Any]] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str
    appointment_data: Optional[Dict[str, Any]] = None


class DocumentUploadResponse(BaseModel):
    message: str
    session_id: str


def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, dict]:
    """Get existing session or create a new one."""
    if session_id and session_id in sessions:
        # Update last accessed time
        sessions[session_id]["last_accessed"] = datetime.now()
        return session_id, sessions[session_id]
    else:
        # Create new session
        new_session_id = str(uuid.uuid4())
        sessions[new_session_id] = {
            "appointment_data": {},
            "conversation_history": [],
            "documents_content": "",
            "created_at": datetime.now(),
            "last_accessed": datetime.now()
        }
        return new_session_id, sessions[new_session_id]


def cleanup_old_sessions():
    """Remove sessions that have exceeded timeout."""
    current_time = datetime.now()
    expired_sessions = [
        sid for sid, data in sessions.items()
        if (current_time - data["last_accessed"]).seconds > SESSION_TIMEOUT
    ]
    for sid in expired_sessions:
        del sessions[sid]


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Context-Aware Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "upload_document": "/upload-document",
            "sessions": "/sessions",
            "health": "/health"
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for both document queries and appointment booking.
    Automatically switches context based on user intent.
    """
    try:
        # Cleanup old sessions
        cleanup_old_sessions()

        # Get or create session
        session_id, session_data = get_or_create_session(request.session_id)

        print("chat session data", session_data)
        print("chat session id", session_id)

        # Run the agent
        result = run_agent(request.message, session_data)

        # Update session
        sessions[session_id] = result["session_data"]
        sessions[session_id]["last_accessed"] = datetime.now()

        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            intent=result["intent"],
            appointment_data=result["session_data"].get("appointment_data")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(
        file: UploadFile = File(...),
        session_id: Optional[str] = None
):
    """
    Upload a document for querying.
    The document content will be stored in the session.
    """
    try:
        # Get or create session
        session_id, session_data = get_or_create_session(session_id)

        # Read file content
        content = await file.read()
        text_content = content.decode("utf-8")

        # Store in session
        sessions[session_id]["documents_content"] = text_content
        sessions[session_id]["last_accessed"] = datetime.now()

        return DocumentUploadResponse(
            message=f"Document '{file.filename}' uploaded successfully. You can now ask questions about it.",
            session_id=session_id
        )

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be a text file (UTF-8 encoded)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session data."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = sessions[session_id]
    return {
        "session_id": session_id,
        "appointment_data": session_data.get("appointment_data", {}),
        "conversation_history": session_data.get("conversation_history", []),
        "has_documents": bool(session_data.get("documents_content", "")),
        "created_at": session_data.get("created_at").isoformat(),
        "last_accessed": session_data.get("last_accessed").isoformat()
    }


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del sessions[session_id]
    return {"message": "Session deleted successfully"}


@app.get("/sessions")
async def list_sessions():
    """List all active sessions."""
    cleanup_old_sessions()
    return {
        "active_sessions": len(sessions),
        "sessions": [
            {
                "session_id": sid,
                "created_at": data["created_at"].isoformat(),
                "last_accessed": data["last_accessed"].isoformat(),
                "has_appointment": bool(data.get("appointment_data")),
                "has_documents": bool(data.get("documents_content"))
            }
            for sid, data in sessions.items()
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(sessions)
    }


if __name__ == "__main__":
    import uvicorn
    from config import APP_HOST, APP_PORT

    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
