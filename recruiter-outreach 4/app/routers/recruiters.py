from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, field_validator

from app.db.database import get_session
from app.models.recruiter import Recruiter, RecruiterRead, RecruiterStatus

router = APIRouter()


class RecruiterIn(BaseModel):
    first_name:     Optional[str] = ""
    last_name:      Optional[str] = ""
    email:          str
    company:        Optional[str] = ""
    company_domain: Optional[str] = None
    title:          Optional[str] = None   # always optional, AI infers it

    @field_validator('email')
    @classmethod
    def email_must_have_at(cls, v):
        v = v.strip().lower()
        if '@' not in v:
            raise ValueError(f"'{v}' is not a valid email address")
        return v

    @field_validator('first_name', 'last_name', 'company', mode='before')
    @classmethod
    def coerce_none_to_str(cls, v):
        return v or ""


class BulkAddRequest(BaseModel):
    recruiters: List[RecruiterIn]


@router.post("/bulk", response_model=List[RecruiterRead], status_code=201)
async def add_bulk(body: BulkAddRequest, session: AsyncSession = Depends(get_session)):
    if not body.recruiters:
        raise HTTPException(400, "No recruiters provided")

    created = []
    for r in body.recruiters:
        # Derive name from email if not provided
        first = r.first_name.strip()
        last  = r.last_name.strip()
        if not first:
            local = r.email.split('@')[0]
            parts = local.replace('.', ' ').replace('_', ' ').replace('-', ' ').split()
            first = parts[0].capitalize() if parts else ""
            last  = " ".join(p.capitalize() for p in parts[1:]) if len(parts) > 1 else ""

        rec = Recruiter(
            first_name=first,
            last_name=last,
            email=r.email,
            company=r.company or "",
            company_domain=r.company_domain,
            title=r.title,
            status=RecruiterStatus.ready,
        )
        session.add(rec)
        created.append(rec)

    await session.commit()
    for r in created:
        await session.refresh(r)
    return created


@router.get("/", response_model=List[RecruiterRead])
async def list_recruiters(
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    q = select(Recruiter)
    if status:
        q = q.where(Recruiter.status == status)
    result = await session.execute(q)
    return result.scalars().all()


@router.get("/stats")
async def stats(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Recruiter))
    all_r = result.scalars().all()
    from collections import Counter
    counts = Counter(r.status.value for r in all_r)
    return {"total": len(all_r), "by_status": dict(counts)}


@router.delete("/{rid}")
async def delete_recruiter(rid: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Recruiter).where(Recruiter.id == rid))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Not found")
    await session.delete(r)
    await session.commit()
    return {"deleted": rid}