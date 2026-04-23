from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreditEntryRead(BaseModel):
    id: UUID
    transaction_type: str
    amount: int
    reason: str
    balance_after: int
    created_at: datetime

    class Config:
        from_attributes = True


class CreditBalance(BaseModel):
    balance: int
    subscription_tier: str
    can_use_free_tailor: bool
    can_use_free_cover_letter: bool
    can_use_free_mock: bool
    free_tailors_used_this_month: int
    free_cover_letters_used_this_month: int
    free_mocks_used_this_week: int


class CreditPack(BaseModel):
    id: str
    credits: int
    price_inr: int
    label: str
    bonus_pct: int = 0


class PurchaseRequest(BaseModel):
    pack_id: str
