import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import SessionLocal, get_session
from app.models import Job, Resume, User
from app.schemas.resume import ResumeParseResult, ResumeRead, TailorRequest
from app.services import ai_service, job_matching
from app.services.credit_service import spend_or_raise
from app.services.resume_parser import extract_text

log = logging.getLogger(__name__)
router = APIRouter(prefix="/resume", tags=["resume"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", response_model=ResumeParseResult, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ResumeParseResult:
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Resume over 10 MB")

    try:
        raw_text = extract_text(file.filename or "resume.pdf", data)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e

    if len(raw_text) < 100:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Could not extract text from resume")

    storage = settings.storage_path / str(user.id)
    storage.mkdir(parents=True, exist_ok=True)
    saved = storage / f"{uuid4()}-{file.filename}"
    saved.write_bytes(data)

    parsed = ai_service.parse_resume(raw_text)

    # Mark any existing primary resumes as non-primary
    existing = (await session.scalars(select(Resume).where(Resume.user_id == user.id, Resume.is_primary.is_(True)))).all()
    for r in existing:
        r.is_primary = False

    resume = Resume(
        user_id=user.id,
        file_url=str(saved),
        file_name=file.filename,
        raw_text=raw_text,
        parsed_json=parsed,
        career_dna=parsed.get("career_dna"),
        is_primary=True,
    )
    session.add(resume)

    user.career_readiness_score = int(parsed.get("readiness_score", 0))
    await session.commit()
    await session.refresh(resume)

    background.add_task(_match_jobs_for_user, user.id, resume.id)

    skills = [s.get("name", "") for s in (parsed.get("skills") or []) if s.get("name")]
    return ResumeParseResult(
        resume=ResumeRead.model_validate(resume),
        skills=skills,
        readiness_score=user.career_readiness_score,
        career_dna=parsed.get("career_dna") or {},
    )


async def _match_jobs_for_user(user_id: UUID, resume_id: UUID) -> None:
    async with SessionLocal() as session:
        resume = await session.get(Resume, resume_id)
        if not resume:
            return
        try:
            await job_matching.match_all_jobs_for_resume(session, user_id, resume, limit=30)
            await session.commit()
        except Exception as exc:
            log.exception("Background match failed: %s", exc)
            await session.rollback()


@router.get("", response_model=ResumeRead | None)
async def get_primary_resume(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ResumeRead | None:
    resume = await session.scalar(
        select(Resume).where(Resume.user_id == user.id, Resume.is_primary.is_(True)).order_by(Resume.created_at.desc())
    )
    return ResumeRead.model_validate(resume) if resume else None


@router.get("/versions", response_model=list[ResumeRead])
async def list_versions(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ResumeRead]:
    rows = (await session.scalars(select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc()))).all()
    return [ResumeRead.model_validate(r) for r in rows]


@router.post("/tailor", response_model=ResumeRead)
async def tailor_for_job(
    payload: TailorRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ResumeRead:
    await spend_or_raise(session, user, "tailor_resume")

    primary = await session.scalar(
        select(Resume).where(Resume.user_id == user.id, Resume.is_primary.is_(True))
    )
    if not primary or not primary.parsed_json:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Upload a primary resume first")

    job = await session.get(Job, payload.job_id)
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")

    tailored = ai_service.tailor_resume(
        primary.parsed_json,
        {
            "title": job.title,
            "company": job.company,
            "description": job.description,
            "requirements": job.requirements,
        },
    )

    new_version = Resume(
        user_id=user.id,
        raw_text=primary.raw_text,
        parsed_json=tailored,
        career_dna=primary.career_dna,
        is_primary=False,
        version=primary.version + 1,
        tailored_for_job_id=job.id,
        file_name=f"tailored-{job.company}-{job.title}.json",
    )
    session.add(new_version)
    await session.commit()
    await session.refresh(new_version)
    return ResumeRead.model_validate(new_version)
