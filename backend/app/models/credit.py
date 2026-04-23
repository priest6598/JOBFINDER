from enum import Enum
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class CreditTransactionType(str, Enum):
    GRANT = "grant"
    PURCHASE = "purchase"
    SPEND = "spend"
    REFUND = "refund"


class CreditLedger(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "credit_ledger"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    transaction_type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="credit_entries")  # noqa: F821
