from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import Application, Job, Resume, User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationNotesUpdate,
    ApplicationRead,
    ApplicationStatusUpdate,
    KanbanBoard,
)
from app.services import ai_service
from app.services.credit_service import spend_or_raise

router = APIRouter(prefix="/applications", tags=["applications"])

VALID_STATUSES = {"applied", "viewed", "interviewing", "offer", "hired", "rejected", "ghosted"}


@router.get("", response_model=list[ApplicationRead])
async def list_applications(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
) -> list[ApplicationRead]:
    rows = (
        await session.scalars(
            select(Application)
            .options(selectinload(Application.job))
            .where(Application.user_id == user.id)
            .order_by(desc(Application.created_at))
        )
    ).all()
    return [ApplicationRead.model_validate(a) for a in rows]


@router.get("/kanban", response_model=KanbanBoard)
async def kanban(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
) -> KanbanBoard:
    rows = (
        await session.scalars(
            select(Application)
            .options(selectinload(Application.job))
            .where(Application.user_id == user.id)
            .order_by(desc(Application.created_at))
        )
    ).all()
    board: dict[str, list[ApplicationRead]] = {k: [] for k in VALID_STATUSES}
    for a in rows:
        board.setdefault(a.status, []).append(ApplicationRead.model_validate(a))
    return KanbanBoard(**board)


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApplicationRead:
    job = await session.get(Job, payload.job_id)
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")

    existing = await session.scalar(
        select(Application).where(Application.user_id == user.id, Application.job_id == payload.job_id)
    )
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Already applied to this job")

    cover_letter = payload.cover_letter
    if not cover_letter:
        await spend_or_raise(session, user, "cover_letter")
        primary = await session.scalar(
            select(Resume).where(Resume.user_id == user.id, Resume.is_primary.is_(True))
        )
        if primary and primary.parsed_json:
            cover_letter = ai_service.generate_cover_letter(
                primary.parsed_json,
                {
                    "title": job.title,
                    "company": job.company,
                    "description": job.description,
                },
            )

    app = Application(
        user_id=user.id,
        job_id=job.id,
        status="applied",
        applied_via="manual",
        cover_letter=cover_letter,
        notes=payload.notes,
    )
    session.add(app)
    await session.commit()
    await session.refresh(app, ["job"])
    return ApplicationRead.model_validate(app)


@router.patch("/{application_id}/status", response_model=ApplicationRead)
async def update_status(
    application_id: UUID,
    payload: ApplicationStatusUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApplicationRead:
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid status. Use one of: {sorted(VALID_STATUSES)}")
    app = await _get_owned(session, application_id, user.id)
    app.status = payload.status
    await session.commit()
    await session.refresh(app, ["job"])
    return ApplicationRead.model_validate(app)


@router.patch("/{application_id}/notes", response_model=ApplicationRead)
async def update_notes(
    application_id: UUID,
    payload: ApplicationNotesUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApplicationRead:
    app = await _get_owned(session, application_id, user.id)
    app.notes = payload.notes
    await session.commit()
    await session.refresh(app, ["job"])
    return ApplicationRead.model_validate(app)


async def _get_owned(session: AsyncSession, application_id: UUID, user_id: UUID) -> Application:
    app = await session.scalar(
        select(Application).options(selectinload(Application.job)).where(Application.id == application_id)
    )
    if not app or app.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
    return app
