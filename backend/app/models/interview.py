from typing import Any
from uuid import UUID

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class InterviewIntel(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "interview_intel"

    company: Mapped[str] = mapped_column(String, nullable=False, index=True)
    role_level: Mapped[str | None] = mapped_column(String)
    interview_type: Mapped[str | None] = mapped_column(String)
    questions: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON)
    process_description: Mapped[str | None] = mapped_column(Text)
    difficulty: Mapped[int | None] = mapped_column(Integer)
    outcome: Mapped[str | None] = mapped_column(String)
    submitted_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)


class MockInterview(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "mock_interviews"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    company: Mapped[str | None] = mapped_column(String)
    role: Mapped[str | None] = mapped_column(String)
    interview_type: Mapped[str] = mapped_column(String, default="behavioral")
    difficulty: Mapped[str] = mapped_column(String, default="medium")
    turns: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON)
    final_score: Mapped[int | None] = mapped_column(Integer)
    feedback: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    medium: Mapped[str] = mapped_column(String, default="text")
