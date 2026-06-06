"""
app/services/gemini_service.py
Generates personalized cold emails using Groq (free tier).
"""

import json
import asyncio
import urllib.request
import urllib.error

from app.models.recruiter import Recruiter
from app.models.settings import AppSettings


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Personal email domains — not real companies, don't use as company name
PERSONAL_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "live.com",
    "icloud.com", "me.com", "protonmail.com", "proton.me", "aol.com",
    "ymail.com", "googlemail.com", "msn.com", "mail.com",
}

SYSTEM_PROMPT = """You are an expert at writing personalized cold outreach emails to recruiters.

CRITICAL RULE: When given a template, you MUST use it almost word-for-word.
Only replace the placeholder text in brackets like [Name], [Company Name] etc.
Do NOT rewrite, shorten, or restructure the email. Preserve every sentence.

Always respond with ONLY a JSON object, no markdown, no extra text:
{
  "subject": "email subject here",
  "body": "full email body here with \\n for line breaks"
}"""


def company_from_email(email: str) -> str:
    """
    Derives a clean company name from an email domain.
    Returns empty string for personal email domains (gmail, yahoo etc).
    e.g. recruiter@equifax.com  -> Equifax
         hr@google.co.uk        -> Google
         jobs@talent-hub.io     -> Talent Hub
         user@gmail.com         -> ""  (personal, not a company)
    """
    domain = email.split("@")[-1].lower()

    if domain in PERSONAL_EMAIL_DOMAINS:
        return ""

    parts = domain.split(".")
    tlds = {"com", "org", "net", "io", "co", "uk", "in", "au", "de", "ai", "app"}
    while len(parts) > 1 and parts[-1].lower() in tlds:
        parts.pop()

    name = parts[0].replace("-", " ").replace("_", " ").title()
    return name


def build_prompt(recruiter: Recruiter, settings: AppSettings) -> str:
    name_part  = recruiter.first_name or recruiter.email.split("@")[0]
    title_part = f" ({recruiter.title})" if recruiter.title else ""

    # Use stored company if available, otherwise derive from email domain
    if recruiter.company and recruiter.company.strip():
        company_part = recruiter.company.strip()
    else:
        company_part = company_from_email(recruiter.email)

    has_company = bool(company_part)

    # Build profile block
    profile_lines = []
    if settings.sender_name:       profile_lines.append(f"- Name: {settings.sender_name}")
    if settings.sender_role:       profile_lines.append(f"- Role: {settings.sender_role}")
    if settings.sender_experience: profile_lines.append(f"- Background: {settings.sender_experience}")
    if settings.sender_linkedin:   profile_lines.append(f"- LinkedIn: {settings.sender_linkedin}")
    profile_block = ("MY PROFILE:\n" + "\n".join(profile_lines) + "\n") if profile_lines else ""

    # Template mode vs free-write mode
    if settings.email_context.strip():
        company_instruction = (
            f'Replace [Company Name] with "{company_part}".' if has_company
            else 'The recruiter uses a personal email — replace [Company Name] with "your company" or omit it naturally.'
        )
        task = f"""Use the following email template EXACTLY. Only fill in the placeholders:
- Replace [Recruiter/Employee Name] or [Name] with: {name_part}
- {company_instruction}
- Replace [Your LinkedIn URL] with: {settings.sender_linkedin or "your LinkedIn"}
- Keep every other sentence exactly as written.

TEMPLATE:
{settings.email_context.strip()}

Generate an appropriate subject line (6 words max).
Return ONLY the JSON object."""
    else:
        company_line = f"- Company: {company_part}" if has_company else "- Company: unknown (personal email)"
        task = f"""Write a concise cold outreach email to this recruiter.

RECRUITER:
- Name: {name_part}{title_part}
{company_line}
- Email: {recruiter.email}

{profile_block}
RULES:
- Address them by first name
- {"Mention their company: " + company_part if has_company else "Do not mention a company name since we only have their personal email"}
- Keep it under 150 words
- End with a clear CTA (15-min call or share resume)
- Subject: 6 words max
- Return ONLY the JSON object"""

    return task


async def generate_email(recruiter: Recruiter, settings: AppSettings) -> tuple[str, str]:
    prompt = build_prompt(recruiter, settings)

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 800,
    }

    def _call():
        data = json.dumps(payload).encode("utf-8")
        req  = urllib.request.Request(
            GROQ_URL,
            data=data,
            headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {settings.gemini_api_key}",
                "User-Agent":    "Mozilla/5.0 (compatible; recruiter-outreach/1.0)",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    loop   = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _call)

    try:
        raw = result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError):
        raise ValueError(f"Unexpected Groq response structure: {result}")

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"Model returned non-JSON: {raw[:200]}")

    subject = parsed.get("subject", "").strip()
    body    = parsed.get("body", "").strip()

    if not subject or not body:
        raise ValueError(f"Response missing subject or body: {parsed}")

    return subject, body
