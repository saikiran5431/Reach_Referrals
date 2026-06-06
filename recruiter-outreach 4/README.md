# Recruiter Outreach Pipeline 🎯

Automated cold-email pipeline: add recruiters → find emails → AI writes personalized messages → send via Gmail.

## Architecture

```
You → POST /recruiters/bulk      (add names + companies)
    → POST /recruiters/find-all-emails  (Hunter.io finds emails)
    → POST /emails/generate-all         (Claude writes emails)
    → POST /campaigns/send              (Gmail SMTP sends them)
    → GET  /campaigns/                  (track results)
```

**Tech Stack:**
| Layer | Tool | Why |
|-------|------|-----|
| API | FastAPI | Auto-generates Swagger docs, async, fast |
| DB | SQLite + SQLModel | Zero-config, file-based, perfect for local |
| Email finder | Hunter.io free tier | 25 searches/month, no card needed |
| AI generation | Claude claude-sonnet-4-20250514 | Best quality/cost for cold email |
| Email delivery | Gmail SMTP | Free, personal = better deliverability |
| Deployment | Docker + docker-compose | Reproducible, portable |

---

## Quick Start

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Gmail account with [App Password](https://myaccount.google.com/apppasswords) created
- [Hunter.io](https://hunter.io) account (free, no card) → get API key
- [Anthropic](https://console.anthropic.com) API key

### 2. Build & run
```bash
# Clone / create the project folder, then:
docker-compose up --build

# First run: --build compiles the Docker image
# Subsequent runs: docker-compose up (uses cached image)
```

The app starts at **http://localhost:8000**
Swagger UI: **http://localhost:8000/docs** ← do everything from here

### 3. Configure your profile (do this FIRST)
```
PUT /settings/
{
  "sender_name": "Alice Chen",
  "sender_email": "alice@gmail.com",
  "sender_role": "Senior Backend Engineer",
  "sender_experience": "5 years Python/Go, built payment systems at two startups",
  "sender_linkedin": "https://linkedin.com/in/alicechen",
  "gmail_app_password": "xxxx xxxx xxxx xxxx",
  "hunter_api_key": "your_hunter_key",
  "anthropic_api_key": "sk-ant-..."
}
```

### 4. Verify Gmail works
```
GET /settings/test-gmail
```

---

## Adding Recruiters

### Option A: Manual JSON (1-5 recruiters)
```
POST /recruiters/bulk
[
  {"first_name": "Sarah", "last_name": "Chen", "company": "Stripe", "title": "Technical Recruiter"},
  {"first_name": "Mike", "last_name": "Ross", "company": "OpenAI"}
]
```

### Option B: CSV Upload
Upload a CSV file to `POST /recruiters/import-csv`

Required columns (flexible naming):
```csv
first_name,last_name,company,title
Sarah,Chen,Stripe,Technical Recruiter
Mike,Ross,OpenAI,
Emma,Taylor,Figma,Senior Recruiter
```

### Option C: Google Sheets
1. Create a Google Sheet with the columns above
2. File → Share → Publish to web → CSV → copy URL
3. `POST /recruiters/import-gsheet?url=YOUR_URL`

---

## Full Pipeline Walk-through

```bash
# Step 1: Add recruiters
POST /recruiters/bulk   (or import-csv, or import-gsheet)

# Step 2: Check what was imported
GET /recruiters/stats
# → {"total": 10, "by_status": {"pending": 10}}

# Step 3: Find emails (uses Hunter.io credits!)
POST /recruiters/find-all-emails
# → {"processed": 10, "email_found": 7, "email_failed": 3}

# Step 4: Generate personalized emails with Claude
POST /emails/generate-all
# → {"processed": 10, "generated": 10, "failed": 0}

# Step 5: Preview before sending (optional but recommended)
GET /emails/preview/1
# → shows subject + body for recruiter ID 1

# Step 6: Edit if needed (optional)
PUT /emails/edit/1?subject=New Subject

# Step 7: Send one test email first
POST /campaigns/send/1
# → {"success": true, "message": "Email sent to sarah.chen@stripe.com"}

# Step 8: Send to everyone
POST /campaigns/send?campaign_name=June 2025 Batch
# → campaign summary with sent/failed counts
```

---

## Recruiter Status Flow

```
pending
  ↓ (POST /recruiters/find-all-emails)
email_found ──────────────→ email_failed (Hunter found nothing, guessed pattern)
  ↓ (POST /emails/generate-all)
ready
  ↓ (POST /campaigns/send)
sent ──────────────────────→ failed (SMTP error)
```

---

## Docker Deep-Dive 🐳

### What is Docker?
Docker packages your app + all dependencies into an **image** — a portable, self-contained unit.

Without Docker:
```
Developer A: "It works on my Mac with Python 3.11"
Developer B: "Broken on my Windows with Python 3.9"
```

With Docker:
```
Everyone runs the same image → same behavior everywhere
```

### Key Concepts

**Image** = A frozen snapshot of your app (like a ZIP file with everything needed)
```bash
docker build -t recruiter-outreach .   # Creates the image
docker images                           # Lists all images on your machine
```

**Container** = A running instance of an image (like a running program from a ZIP)
```bash
docker run recruiter-outreach          # Creates + starts a container from the image
docker ps                              # Lists running containers
docker ps -a                           # Lists all containers (including stopped)
```

**Layer Caching** = Why Docker builds are fast after the first time
```dockerfile
COPY requirements.txt .    # Layer 1: changes rarely
RUN pip install ...        # Layer 2: skipped if Layer 1 unchanged
COPY app/ .                # Layer 3: changes every time you edit code
```
If you only change app code, Docker skips pip install → 30s build instead of 5 minutes.

**Volumes** = Persistent storage that survives container restarts
```yaml
volumes:
  - recruiter_data:/data   # Your SQLite DB lives here forever
```
Without a volume, your database disappears every time you restart Docker.

**Port Mapping** = How your laptop talks to the container
```yaml
ports:
  - "8000:8000"   # localhost:8000 → container:8000
  - "9000:8000"   # localhost:9000 → container:8000  (different host port)
```

### Useful Docker Commands

```bash
# Start everything (builds if needed)
docker-compose up --build

# Start in background (detached mode)
docker-compose up -d

# See container logs
docker-compose logs -f api

# Stop everything
docker-compose down

# Stop AND delete volumes (DELETES YOUR DATABASE)
docker-compose down -v

# Open a shell inside the running container
docker-compose exec api bash

# Rebuild without cache (if something's broken)
docker-compose build --no-cache

# See what's using disk space
docker system df

# Clean up unused images/containers
docker system prune
```

### Volume Deep-Dive

Named volumes (`recruiter_data`) are managed by Docker and stored at:
- **Mac**: Inside Docker Desktop VM (`~/Library/Containers/...`)
- **Linux**: `/var/lib/docker/volumes/recruiter_data/`
- **Windows**: Inside WSL2

To see your volume:
```bash
docker volume ls
docker volume inspect recruiter_data
# → shows the actual path on disk
```

Bind mounts (`./app:/app/app`) point to actual folders on your machine:
```bash
# This means: your local ./app folder IS the /app/app folder in the container
# Edit a file locally → container sees it instantly → uvicorn --reload restarts
```

---

## Project Structure

```
recruiter-outreach/
├── app/
│   ├── main.py              ← FastAPI app + router registration
│   ├── db/
│   │   └── database.py      ← SQLite engine + session factory
│   ├── models/
│   │   ├── recruiter.py     ← Recruiter table + API schemas
│   │   ├── campaign.py      ← Campaign tracking table
│   │   └── settings.py      ← App settings (credentials) table
│   ├── services/
│   │   ├── hunter_service.py ← Hunter.io API calls
│   │   ├── claude_service.py ← Claude email generation
│   │   ├── gmail_service.py  ← Gmail SMTP sending
│   │   └── csv_service.py    ← CSV + Google Sheets parsing
│   └── routers/
│       ├── settings.py       ← GET/PUT /settings
│       ├── recruiters.py     ← CRUD + email finding
│       ├── emails.py         ← Email generation + preview
│       └── campaigns.py      ← Send + track campaigns
├── Dockerfile               ← Image build recipe
├── docker-compose.yml       ← Container orchestration
├── requirements.txt         ← Python dependencies
└── README.md
```

---

## Tips & Gotchas

**Hunter.io free tier = 25 credits/month**
- Use `GET /recruiters/stats` to see how many are pending before running find-all
- Each recruiter = 1 credit
- Check usage at hunter.io/users/me

**Gmail daily limits**
- ~500 emails/day on personal Gmail
- Space out sends if doing large batches

**Gmail App Password setup**
1. Enable 2-Step Verification at myaccount.google.com/security
2. Go to myaccount.google.com/apppasswords
3. Create → "Mail" / "Other (Custom)" → name it "Recruiter Outreach"
4. Copy the 16-char password (only shown once)

**Domain inference**
- "Stripe" → "stripe.com" ✓
- "Acme Corp" → "acmecorp.com" ✗ (probably wrong)
- Set `company_domain` manually for unusual company names

**If emails end up in spam**
- Warm up your Gmail account first (send/receive normal emails)
- Personalize subject lines (Claude does this automatically)
- Don't send to 50+ people on day 1 — ramp up slowly
