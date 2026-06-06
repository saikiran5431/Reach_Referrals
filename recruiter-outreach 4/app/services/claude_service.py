# """
# app/services/claude_service.py — WHY IT EXISTS
# ================================================
# All Claude (Anthropic) AI logic lives here.
# One job: given a recruiter's info + your profile, write a cold outreach email.

# Why Claude instead of a template?
# - Templates feel robotic. Claude personalizes based on company, title, context.
# - Claude can vary tone, length, and angle per recruiter.

# We use the official anthropic Python SDK (async version).
# The prompt is carefully structured to get professional, concise output.
# """

# from anthropic import AsyncAnthropic
# from app.models.recruiter import Recruiter
# from app.models.settings import AppSettings


# # Email generation prompt template
# # {placeholders} are filled in at call time
# SYSTEM_PROMPT = """You are an expert at writing concise, professional cold outreach emails to recruiters.
# Your emails are:
# - Short (150-200 words max)
# - Personalized to the company and recruiter's role
# - Direct about what the candidate wants
# - Warm but not sycophantic
# - Closing with a specific call to action

# Always respond with ONLY a JSON object in this exact format (no markdown, no extra text):
# {
#   "subject": "email subject line here",
#   "body": "full email body here with \\n for line breaks"
# }"""


# def build_user_prompt(recruiter: Recruiter, settings: AppSettings) -> str:
#     """
#     Builds the user-facing prompt by filling in real data.
    
#     We include:
#     - Your background (so Claude can sell you properly)
#     - Recruiter's name + company + title (so Claude can personalize)
#     - Explicit instructions on format and length
#     """
#     title_line = f" ({recruiter.title})" if recruiter.title else ""
    
#     return f"""Write a cold outreach email from me to a recruiter.

# MY PROFILE:
# - Name: {settings.sender_name}
# - Seeking: {settings.sender_role}
# - Background: {settings.sender_experience}
# - LinkedIn: {settings.sender_linkedin}

# RECRUITER:
# - Name: {recruiter.first_name} {recruiter.last_name}{title_line}
# - Company: {recruiter.company}

# INSTRUCTIONS:
# - Open by addressing them by first name only
# - Mention their company specifically (why I'm interested)
# - 2-3 sentences on my background / value
# - 1 sentence CTA: ask for a 15-min call or to share my resume
# - Sign off with my name and LinkedIn URL
# - NO subject line fluff like "Exciting Opportunity"
# - Subject: 6 words max, specific and intriguing

# Return ONLY the JSON object, no markdown fences."""


# async def generate_email(
#     recruiter: Recruiter,
#     settings: AppSettings,
# ) -> tuple[str, str]:
#     """
#     Calls Claude claude-sonnet-4-20250514 to generate a personalized cold email.
    
#     Returns: (subject, body) tuple
    
#     Raises: ValueError if the response isn't valid JSON (shouldn't happen with good prompting)
#     """
#     import json
    
#     client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    
#     message = await client.messages.create(
#         model="claude-sonnet-4-20250514",  # Fast, cheap, high quality
#         max_tokens=500,                     # ~375 words — more than enough
#         system=SYSTEM_PROMPT,
#         messages=[
#             {
#                 "role": "user",
#                 "content": build_user_prompt(recruiter, settings)
#             }
#         ],
#     )
    
#     # Extract the text from Claude's response
#     # message.content is a list of content blocks; we want the first text block
#     raw = message.content[0].text.strip()
    
#     # Strip markdown fences if Claude added them despite instructions
#     if raw.startswith("```"):
#         raw = raw.split("```")[1]
#         if raw.startswith("json"):
#             raw = raw[4:]
#         raw = raw.strip()
    
#     # Parse JSON
#     try:
#         parsed = json.loads(raw)
#     except json.JSONDecodeError as e:
#         raise ValueError(f"Claude returned non-JSON response: {raw[:200]}... Error: {e}")
    
#     subject = parsed.get("subject", "").strip()
#     body    = parsed.get("body", "").strip()
    
#     if not subject or not body:
#         raise ValueError(f"Claude response missing subject or body: {parsed}")
    
#     return subject, body


# async def generate_emails_batch(
#     recruiters: list[Recruiter],
#     settings: AppSettings,
#     on_progress=None,
# ) -> dict[int, tuple[str, str]]:
#     """
#     Generates emails for multiple recruiters.
    
#     on_progress: optional async callback(recruiter_id, success, error_msg)
#     Returns: dict of {recruiter_id: (subject, body)} for successful ones
    
#     Runs sequentially (not parallel) to avoid rate limits.
#     Claude API has a requests-per-minute limit on free tier.
#     """
#     results = {}
    
#     for recruiter in recruiters:
#         try:
#             subject, body = await generate_email(recruiter, settings)
#             results[recruiter.id] = (subject, body)
#             if on_progress:
#                 await on_progress(recruiter.id, True, None)
#         except Exception as e:
#             if on_progress:
#                 await on_progress(recruiter.id, False, str(e))
    
#     return results
