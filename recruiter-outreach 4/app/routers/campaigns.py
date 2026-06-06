"""
app/routers/campaigns.py
Generate emails with Claude + send via Gmail. Single endpoint for both.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.db.database import get_session
from app.models.recruiter import Recruiter, RecruiterStatus
from app.models.campaign import Campaign, CampaignRead
from app.services.gemini_service import generate_email
from app.services.gmail_service import send_email_async
from app.routers.settings import get_or_create_settings

router = APIRouter()


class GenerateAndSendRequest(BaseModel):
    recruiter_ids: Optional[List[int]] = None  # None = all ready recruiters
    send_after_generate: bool = True
    campaign_name: str = "Outreach Batch"


@router.post("/run", summary="Generate emails with Claude then send via Gmail")
async def run_campaign(
    body: GenerateAndSendRequest,
    session: AsyncSession = Depends(get_session),
):
    settings = await get_or_create_settings(session)

    if not settings.gemini_api_key:
        raise HTTPException(400, "Groq API key not set. Paste your gsk_... key at /setup and save.")
    if body.send_after_generate and (not settings.sender_email or not settings.gmail_app_password):
        raise HTTPException(400, "Gmail not configured. Set sender email + app password at /setup")

    # Get target recruiters
    if body.recruiter_ids:
        result = await session.execute(
            select(Recruiter).where(Recruiter.id.in_(body.recruiter_ids))
        )
    else:
        result = await session.execute(
            select(Recruiter).where(Recruiter.status == RecruiterStatus.ready)
        )
    recruiters = result.scalars().all()

    if not recruiters:
        raise HTTPException(400, "No ready recruiters found. Add some at /setup first.")

    results = []

    for rec in recruiters:
        item = {"id": rec.id, "email": rec.email, "name": f"{rec.first_name} {rec.last_name}".strip()}

        # Step 1: Generate with Claude
        try:
            subject, body_text = await generate_email(rec, settings)
            rec.generated_subject = subject
            rec.generated_body = body_text
            item["generated"] = True
            item["subject"] = subject
        except Exception as e:
            rec.status = RecruiterStatus.failed
            rec.error_message = f"Generate failed: {e}"
            item["generated"] = False
            item["error"] = str(e)
            session.add(rec)
            results.append(item)
            continue

        # Step 2: Send via Gmail
        if body.send_after_generate:
            try:
                await send_email_async(
                    from_email=settings.sender_email,
                    from_name=settings.sender_name,
                    to_email=rec.email,
                    to_name=f"{rec.first_name} {rec.last_name}".strip() or rec.email,
                    subject=subject,
                    body=body_text,
                    app_password=settings.gmail_app_password,
                    resume_path=settings.resume_path or None,
                    resume_filename=settings.resume_filename or None,
                )
                rec.status = RecruiterStatus.sent
                item["sent"] = True
            except Exception as e:
                rec.status = RecruiterStatus.failed
                rec.error_message = f"Send failed: {e}"
                item["sent"] = False
                item["error"] = str(e)
        else:
            item["sent"] = False

        rec.updated_at = datetime.utcnow()
        session.add(rec)
        results.append(item)

    await session.commit()

    sent_count = sum(1 for r in results if r.get("sent"))
    fail_count = sum(1 for r in results if r.get("error"))

    return {
        "total": len(results),
        "sent": sent_count,
        "failed": fail_count,
        "results": results,
    }


@router.get("/preview", summary="Preview generated emails without sending")
async def preview_all(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Recruiter))
    all_r = result.scalars().all()
    return [
        {
            "id": r.id,
            "to": r.email,
            "name": f"{r.first_name} {r.last_name}".strip(),
            "company": r.company,
            "subject": r.generated_subject,
            "body": r.generated_body,
            "status": r.status,
        }
        for r in all_r if r.generated_subject
    ]


@router.get("/", response_model=List[CampaignRead])
async def list_campaigns(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Campaign).order_by(Campaign.created_at.desc())
    )
    return result.scalars().all()
