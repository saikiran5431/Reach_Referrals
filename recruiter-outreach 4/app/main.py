"""
main.py — WHY IT EXISTS
========================
Entry point for the FastAPI app. Registers all routers and sets up the DB.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.database import init_db
from app.routers import recruiters, emails, settings, campaigns, ui


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Recruiter Outreach API",
    description="""
## Automated recruiter cold-outreach pipeline

**First time?** Visit [/setup](/setup) to configure your profile and API keys.

**Workflow:**
1. `POST /recruiters/bulk` — add recruiter names + companies
2. `POST /recruiters/find-all-emails` — Hunter.io resolves emails
3. `POST /emails/generate-all` — Claude writes personalized emails
4. `POST /campaigns/send` — Gmail SMTP delivers them
5. `GET /campaigns/` — track results
    """,
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(ui.router,         tags=["UI"])
app.include_router(settings.router,   prefix="/settings",   tags=["Settings"])
app.include_router(recruiters.router, prefix="/recruiters", tags=["Recruiters"])
app.include_router(emails.router,     prefix="/emails",     tags=["Email Preview"])
app.include_router(campaigns.router,  prefix="/campaigns",  tags=["Campaigns"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "recruiter-outreach"}