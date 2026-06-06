"""
app/db/database.py — WHY IT EXISTS
====================================
Everything database-related lives here:
  - The SQLite engine (the file on disk)
  - A session factory (each request gets its own DB "conversation")
  - init_db() which creates all tables on first boot

We use SQLModel, which combines SQLAlchemy (DB engine) + Pydantic (validation)
into one class. Write the model once, get DB table + API schema validation free.

SQLite is stored at /data/recruiter.db inside the container.
Docker mounts a volume there so data survives container restarts.
"""

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import pathlib

# ── Database URL ────────────────────────────────────────────────────────────
# aiosqlite = async SQLite driver (lets FastAPI stay non-blocking)
# /data/ is a Docker volume mount — data persists across container restarts
# IMPORTANT: 4 slashes = absolute path on Linux (sqlite+aiosqlite:////data/...)
#            3 slashes = relative path (would look in /app/data/ — wrong!)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:////data/recruiter.db")

# ── Async engine ────────────────────────────────────────────────────────────
# echo=True prints every SQL query to logs — great for learning, turn off in prod
engine = create_async_engine(DATABASE_URL, echo=True)

# ── Session factory ─────────────────────────────────────────────────────────
# AsyncSessionLocal() creates one DB session per request
# expire_on_commit=False means objects stay usable after commit
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """
    Called once at startup. Creates all tables defined in SQLModel models.
    Also ensures /data directory exists with write permissions before connecting.
    """
    # Extract the file path from the URL and ensure the directory exists
    # "sqlite+aiosqlite:////data/recruiter.db" → "/data/recruiter.db"
    db_file = DATABASE_URL.split("sqlite+aiosqlite://")[-1]
    pathlib.Path(db_file).parent.mkdir(parents=True, exist_ok=True)

    # Import models here so SQLModel.metadata knows about them
    from app.models import recruiter, campaign, settings  # noqa: F401

    async with engine.begin() as conn:
        # run_sync wraps the sync SQLAlchemy call in async context
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    """
    FastAPI dependency. Use it in route functions like:
        async def my_route(session: AsyncSession = Depends(get_session)):

    'async with' ensures the session is always closed, even if an error occurs.
    yield = this is a generator-based dependency (runs setup, yields, runs teardown)
    """
    async with AsyncSessionLocal() as session:
        yield session