from sqlalchemy import Column, Integer, Text, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    transcript = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)

    action_items = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan")

class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    description = Column(Text, nullable=False)
    owner = Column(String(255), nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(String(32), default="open", nullable=False)

    meeting = relationship("Meeting", back_populates="action_items")