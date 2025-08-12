import os
import tempfile
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .db import get_db, init_db
from .models import Meeting, ActionItem
from .schemas import MeetingOut, ActionItemOut
from .openai_client import transcribe_audio, summarize_and_extract
from .rate_limit import rate_limiter_optional

app = FastAPI(title="AI Meeting Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static for favicon and future assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    """Redirect to interactive docs (avoids 404 on /)."""
    return RedirectResponse(url="/docs")


@app.get("/favicon.ico")
def favicon():
    """Serve favicon if present in app/static; otherwise return a tiny transparent icon."""
    ico_path = os.path.join(static_dir, "favicon.ico")
    if os.path.isfile(ico_path):
        return FileResponse(ico_path, media_type="image/x-icon")
    # tiny 1x1 transparent icon bytes (minimal ICO header)
    ico = (b"\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x04\x00\x28\x01\x00\x00"
           b"\x16\x00\x00\x00\x28\x00\x00\x00\x10\x00\x00\x00\x20\x00\x00\x00\x01\x00"
           b"\x04\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
           b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
    return Response(content=ico, media_type="image/x-icon")


@app.post("/meetings", response_model=MeetingOut)
async def create_meeting(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    _rl=Depends(rate_limiter_optional("create_meeting", rate=60, per_seconds=60)),
):
    """Upload audio, transcribe, summarize, and persist meeting + action items."""
    if not audio.content_type or not (
        audio.content_type.startswith("audio/") or audio.filename.lower().endswith((".mp3", ".wav", ".m4a", ".webm", ".mp4"))
    ):
        raise HTTPException(status_code=400, detail="Please upload an audio file (mp3, wav, m4a, webm, mp4).")

    # Save to a temp file for OpenAI Whisper
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        transcript_text = transcribe_audio(tmp_path)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    if not transcript_text or not transcript_text.strip():
        raise HTTPException(status_code=422, detail="Transcription failed or was empty.")

    # Summarize & extract action items
    summary, action_items = summarize_and_extract(transcript_text)

    # Persist
    meeting = Meeting(transcript=transcript_text, summary=summary)
    db.add(meeting)
    db.flush()  # to get meeting.id

    for item in action_items:
        db.add(ActionItem(
            meeting_id=meeting.id,
            description=item.get("description", "").strip(),
            owner=item.get("owner"),
            due_date=item.get("due_date"),
            status="open"
        ))

    db.commit()
    db.refresh(meeting)

    return MeetingOut(
        id=meeting.id,
        summary=meeting.summary,
        transcript_preview=meeting.transcript[:1000],
    )


@app.get("/meetings/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).get(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return MeetingOut(
        id=meeting.id,
        summary=meeting.summary,
        transcript_preview=meeting.transcript[:1000],
    )


@app.get("/meetings/{meeting_id}/actions", response_model=List[ActionItemOut])
def list_actions(meeting_id: int, db: Session = Depends(get_db)):
    actions = db.query(ActionItem).filter(ActionItem.meeting_id == meeting_id).all()
    return [
        ActionItemOut(
            id=a.id,
            description=a.description,
            owner=a.owner,
            due_date=a.due_date.isoformat() if a.due_date else None,
            status=a.status,
        ) for a in actions
    ]


@app.get("/health")
def health_check():
    return {"status": "ok"}