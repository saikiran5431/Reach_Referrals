from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import os
import pathlib
import shutil

from app.db.database import get_session
from app.models.settings import AppSettings, AppSettingsUpdate, AppSettingsRead
from app.services.gmail_service import test_gmail_connection

router = APIRouter()
SETTINGS_ID = 1
RESUME_DIR = "/data/resume"


async def get_or_create_settings(session: AsyncSession) -> AppSettings:
    result = await session.execute(
        select(AppSettings).where(AppSettings.id == SETTINGS_ID)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = AppSettings(id=SETTINGS_ID)
        session.add(settings)
        await session.commit()
        await session.refresh(settings)
    return settings


def to_read(s: AppSettings) -> AppSettingsRead:
    return AppSettingsRead(
        sender_name=s.sender_name,
        sender_email=s.sender_email,
        sender_linkedin=s.sender_linkedin,
        sender_role=s.sender_role,
        sender_experience=s.sender_experience,
        email_context=s.email_context,
        gemini_api_key_set=bool(s.gemini_api_key),
        hunter_api_key_set=bool(s.hunter_api_key),
        gmail_configured=bool(s.sender_email and s.gmail_app_password),
        resume_filename=s.resume_filename,
    )


@router.get("/", response_model=AppSettingsRead)
async def read_settings(session: AsyncSession = Depends(get_session)):
    return to_read(await get_or_create_settings(session))


@router.put("/", response_model=AppSettingsRead)
async def update_settings(updates: AppSettingsUpdate, session: AsyncSession = Depends(get_session)):
    s = await get_or_create_settings(session)
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    session.add(s)
    await session.commit()
    await session.refresh(s)
    return to_read(s)


@router.post("/resume", response_model=AppSettingsRead)
async def upload_resume(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted.")

    pathlib.Path(RESUME_DIR).mkdir(parents=True, exist_ok=True)
    dest = os.path.join(RESUME_DIR, "resume.pdf")

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    s = await get_or_create_settings(session)
    s.resume_path = dest
    s.resume_filename = file.filename
    session.add(s)
    await session.commit()
    await session.refresh(s)
    return to_read(s)


@router.delete("/resume", response_model=AppSettingsRead)
async def delete_resume(session: AsyncSession = Depends(get_session)):
    s = await get_or_create_settings(session)
    if s.resume_path and os.path.exists(s.resume_path):
        os.remove(s.resume_path)
    s.resume_path = ""
    s.resume_filename = ""
    session.add(s)
    await session.commit()
    await session.refresh(s)
    return to_read(s)


@router.get("/test-gmail")
async def test_gmail(session: AsyncSession = Depends(get_session)):
    s = await get_or_create_settings(session)
    if not s.sender_email or not s.gmail_app_password:
        raise HTTPException(400, "Gmail not configured.")
    return await test_gmail_connection(s.sender_email, s.gmail_app_password)
