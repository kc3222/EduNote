from typing import List, Optional

import argparse
import json
import os

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from note_service.services.note_service import NoteService
from note_service.services.summarize_service import SummarizeService
from note_service.services.quiz_service import QuizService
from note_service.models.models import NoteCreate, NoteUpdate, NoteResponse


app = FastAPI(title="Notes Service", version="1.1.0")

note_service = NoteService()
summarize_service = SummarizeService()
quiz_service = QuizService()

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------
# Pydantic models for AI endpoints
# --------------------------------------------------------------------


class SummaryResponse(BaseModel):
    title: str
    tldr: str
    key_points: List[str]
    action_items: List[str]
    questions: List[str]
    keywords: List[str]


class AdHocSummarizeRequest(BaseModel):
    title_hint: Optional[str] = None
    markdown: str


class PersistedSummaryResponse(BaseModel):
    note_id: str
    summary: SummaryResponse


class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_option: int
    explanation: Optional[str] = None
    difficulty: Optional[str] = None


class QuizPayload(BaseModel):
    title: str
    questions: List[QuizQuestion]


class PersistedQuizResponse(BaseModel):
    note_id: str
    quiz: QuizPayload


# --------------------------------------------------------------------
# Basic health endpoints
# --------------------------------------------------------------------


@app.get("/")
async def root():
    return {"message": "Notes Service is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# --------------------------------------------------------------------
# CRUD for notes
# --------------------------------------------------------------------


@app.post("/notes", response_model=NoteResponse)
async def create_note(request: Request):
    """
    Create a new note.

    The frontend sends a JSON body; we parse it to NoteCreate and delegate
    to NoteService.
    """
    try:
        body = await request.body()
        note_data = json.loads(body)
        note = NoteCreate(**note_data)
        return note_service.create_note(note)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/notes", response_model=List[NoteResponse])
async def get_notes(
    owner_id: Optional[str] = None,
    is_archived: Optional[bool] = None,
):
    """Get notes with optional filtering."""
    return note_service.get_notes(owner_id=owner_id, is_archived=is_archived)


@app.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str):
    """Get a specific note by ID."""
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note_update: NoteUpdate):
    """Update a note."""
    return note_service.update_note(note_id, note_update)


@app.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete a note."""
    return note_service.delete_note(note_id)


# --------------------------------------------------------------------
# Summarization endpoints (note-aware)
# --------------------------------------------------------------------


@app.post("/notes/{note_id}/summarize", response_model=SummaryResponse)
def summarize_note_endpoint(note_id: str):
    """
    Compute a structured summary for the note (on-the-fly, NOT persisted).

    Suitable when you want a fresh summary but don't care about storing it.
    """
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    summary = summarize_service.summarize_note(note)
    return summary


@app.put(
    "/notes/{note_id}/summary",
    response_model=PersistedSummaryResponse,
)
def summarize_and_persist_endpoint(note_id: str):
    """
    Compute a Gemini summary and persist it to summary_json + summary_updated_at.

    Matches the frontend PUT /notes/{id}/summary call.
    """
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    try:
        summary = summarize_service.summarize_and_persist(note_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=503, detail="AI summary service unavailable")

    return {"note_id": note_id, "summary": summary}


@app.get("/notes/{note_id}/summary")
def get_persisted_summary(note_id: str):
    """
    Retrieve the stored summary (without recomputing).
    """
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {
        "note_id": note_id,
        "summary": note.summary_json,
        "summary_updated_at": note.summary_updated_at,
    }


# --------------------------------------------------------------------
# Generic AI endpoint for other services
# --------------------------------------------------------------------


@app.post("/ai/summarize", response_model=SummaryResponse)
def summarize_arbitrary_text(payload: AdHocSummarizeRequest):
    """
    General-purpose AI summarize endpoint.

    Other backend services (document_service, quiz_service, etc.) can call this
    with raw markdown content. It does NOT persist anything; it only returns
    the structured summary JSON.
    """
    try:
        # Build a minimal NoteResponse-like object expected by SummarizeService
        class _FakeNote:
            def __init__(self, title: Optional[str], markdown: str):
                self.title = title
                self.markdown = markdown

        fake_note = _FakeNote(payload.title_hint, payload.markdown)
        summary = summarize_service.summarize_note(fake_note)  # type: ignore[arg-type]
        return summary
    except Exception:
        raise HTTPException(status_code=503, detail="AI summary service unavailable")


# --------------------------------------------------------------------
# Quiz endpoints
# --------------------------------------------------------------------


@app.post("/notes/{note_id}/quizzes")
def generate_quiz_for_note(note_id: str):
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    try:
        quiz = quiz_service.generate_and_persist(note_id)
    except ValueError as e:
        # ValueError here means some internal quiz issue, not "note not found"
        print("Error generating quiz (ValueError):", e)
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        print("Error generating quiz:", e)
        raise HTTPException(status_code=503, detail="AI quiz service unavailable")

    return {"note_id": note_id, "quiz": quiz}


@app.get(
    "/notes/{note_id}/quizzes",
    response_model=PersistedQuizResponse,
)
def get_quiz_for_note(note_id: str):
    """
    Retrieve the stored quiz JSON for a note.
    Assumes NoteResponse exposes a quiz_json field.
    """
    note = note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    quiz = getattr(note, "quiz_json", None)
    if not quiz:
        raise HTTPException(status_code=404, detail="No quiz found for this note")

    return {"note_id": note_id, "quiz": quiz}


# --------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Notes Service")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("NOTES_SERVICE_PORT", "8001")),
        help="Port number to run the service on",
    )
    args = parser.parse_args()

    print(f"Starting Notes Service on port {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)