from typing import Optional
from pydantic import BaseModel

class MeetingCreate(BaseModel):
    pass  # placeholder if you add metadata later

class MeetingOut(BaseModel):
    id: int
    summary: str
    transcript_preview: str

    class Config:
        from_attributes = True

class ActionItemOut(BaseModel):
    id: int
    description: str
    owner: Optional[str] = None
    due_date: Optional[str] = None
    status: str

    class Config:
        from_attributes = True