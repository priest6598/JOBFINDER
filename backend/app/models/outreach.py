from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class OutreachMessage(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "outreach_messages"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[UUID | None] = mapped_column(ForeignKey("jobs.id"))
    application_id: Mapped[UUID | None] = mapped_column(ForeignKey("applications.id"))
    recipient_name: Mapped[str | None] = mapped_column(String)
    recipient_title: Mapped[str | None] = mapped_column(String)
    recipient_linkedin: Mapped[str | None] = mapped_column(String)
    recipient_email: Mapped[str | None] = mapped_column(String)
    message_type: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str | None] = mapped_column(String)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="draft")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
