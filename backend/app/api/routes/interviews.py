from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import Resume, User
from app.models.interview import InterviewIntel, MockInterview
from app.services import ai_service
from app.services.credit_service import spend_or_raise

router = APIRouter(prefix="/interviews", tags=["interviews"])


class PrepDeckRequest(BaseModel):
    company: str
    role: str
    jd: str = ""


class MockQuestionRequest(BaseModel):
    role: str
    interview_type: str = "behavioral"
    difficulty: str = "medium"


class MockScoreRequest(BaseModel):
    mock_id: UUID | None = None
    question: str
    answer: str
    role: str


@router.post("/prep-deck")
async def prep_deck(
    payload: PrepDeckRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    await spend_or_raise(session, user, "company_prep_pack", allow_free=False)
    primary = await session.scalar(
        select(Resume).where(Resume.user_id == user.id, Resume.is_primary.is_(True))
    )
    if not primary or not primary.parsed_json:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Upload a primary resume first")

    intel_rows = (
        await session.scalars(
            select(InterviewIntel).where(InterviewIntel.company.ilike(payload.company)).limit(5)
        )
    ).all()
    intel = [
        {"questions": r.questions, "process": r.process_description, "difficulty": r.difficulty}
        for r in intel_rows
    ]

    deck = ai_service.generate_interview_prep_deck(
        payload.company, payload.role, payload.jd, primary.parsed_json, intel
    )
    await session.commit()
    return deck


@router.post("/mock/score")
async def mock_score(
    payload: MockScoreRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    await spend_or_raise(session, user, "text_mock")
    result = ai_service.score_interview_answer(payload.question, payload.answer, payload.role)

    if payload.mock_id:
        mock = await session.get(MockInterview, payload.mock_id)
        if mock and mock.user_id == user.id:
            turns = list(mock.turns or [])
            turns.append({"question": payload.question, "answer": payload.answer, "score": result})
            mock.turns = turns
    else:
        mock = MockInterview(
            user_id=user.id,
            role=payload.role,
            turns=[{"question": payload.question, "answer": payload.answer, "score": result}],
        )
        session.add(mock)

    await session.commit()
    return result
