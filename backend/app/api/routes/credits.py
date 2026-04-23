from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import CreditLedger, User
from app.schemas.credit import (
    CreditBalance,
    CreditEntryRead,
    CreditPack,
    PurchaseRequest,
)
from app.services.credit_service import (
    CREDIT_PACKS,
    FEATURE_COSTS,
    add_purchased_credits,
    get_free_usage,
    is_pro_active,
)
from app.core.config import settings

router = APIRouter(prefix="/credits", tags=["credits"])


@router.get("/balance", response_model=CreditBalance)
async def balance(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
) -> CreditBalance:
    usage = await get_free_usage(session, user.id)
    return CreditBalance(
        balance=user.credits_balance,
        subscription_tier=user.subscription_tier,
        can_use_free_tailor=is_pro_active(user)
        or usage.tailors_this_month < settings.FREE_TAILORED_RESUMES_PER_MONTH,
        can_use_free_cover_letter=is_pro_active(user)
        or usage.cover_letters_this_month < settings.FREE_COVER_LETTERS_PER_MONTH,
        can_use_free_mock=is_pro_active(user)
        or usage.mocks_this_week < settings.FREE_MOCK_INTERVIEWS_PER_WEEK,
        free_tailors_used_this_month=usage.tailors_this_month,
        free_cover_letters_used_this_month=usage.cover_letters_this_month,
        free_mocks_used_this_week=usage.mocks_this_week,
    )


@router.get("/packs", response_model=list[CreditPack])
async def list_packs() -> list[CreditPack]:
    return CREDIT_PACKS


@router.get("/costs")
async def feature_costs() -> dict[str, int]:
    return FEATURE_COSTS


@router.get("/ledger", response_model=list[CreditEntryRead])
async def ledger(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
) -> list[CreditEntryRead]:
    rows = (
        await session.scalars(
            select(CreditLedger).where(CreditLedger.user_id == user.id).order_by(desc(CreditLedger.created_at)).limit(100)
        )
    ).all()
    return [CreditEntryRead.model_validate(r) for r in rows]


@router.post("/purchase", response_model=CreditBalance)
async def purchase(
    payload: PurchaseRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CreditBalance:
    """Dev stub — in prod, verify Razorpay payment signature before granting credits."""
    pack = next((p for p in CREDIT_PACKS if p.id == payload.pack_id), None)
    if not pack:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pack not found")
    await add_purchased_credits(session, user, pack.credits, pack.id)
    await session.commit()
    await session.refresh(user)
    return await balance(user, session)
