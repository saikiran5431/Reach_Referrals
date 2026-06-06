"""
app/services/gmail_service.py
Handles sending emails via Gmail SMTP, with optional PDF resume attachment.
"""

import smtplib
import asyncio
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formataddr
from email import encoders
from typing import Optional


GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587


def build_mime_message(
    from_email: str,
    from_name: str,
    to_email: str,
    to_name: str,
    subject: str,
    body: str,
    resume_path: Optional[str] = None,
    resume_filename: Optional[str] = None,
) -> MIMEMultipart:
    # 'mixed' supports attachments; 'alternative' is text-only
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"]    = formataddr((from_name, from_email))
    msg["To"]      = formataddr((to_name, to_email))

    msg.attach(MIMEText(body, "plain", "utf-8"))

    if resume_path and os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = resume_filename or os.path.basename(resume_path)
        part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
        msg.attach(part)

    return msg


def send_email_sync(
    from_email: str,
    from_name: str,
    to_email: str,
    to_name: str,
    subject: str,
    body: str,
    app_password: str,
    resume_path: Optional[str] = None,
    resume_filename: Optional[str] = None,
) -> None:
    msg = build_mime_message(
        from_email, from_name, to_email, to_name, subject, body,
        resume_path, resume_filename
    )
    with smtplib.SMTP(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(from_email, app_password)
        server.sendmail(from_email, to_email, msg.as_string())


async def send_email_async(
    from_email: str,
    from_name: str,
    to_email: str,
    to_name: str,
    subject: str,
    body: str,
    app_password: str,
    resume_path: Optional[str] = None,
    resume_filename: Optional[str] = None,
) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: send_email_sync(
            from_email, from_name, to_email, to_name, subject, body,
            app_password, resume_path, resume_filename
        )
    )


async def test_gmail_connection(email: str, app_password: str) -> dict:
    try:
        loop = asyncio.get_event_loop()
        def _test():
            with smtplib.SMTP(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(email, app_password)
        await loop.run_in_executor(None, _test)
        return {"success": True, "message": "Gmail SMTP connection successful"}
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "error": "Authentication failed. Use a Gmail App Password, not your regular password.",
            "help": "Go to myaccount.google.com/apppasswords to create one."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
