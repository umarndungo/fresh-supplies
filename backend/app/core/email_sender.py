"""SMTP email sending for the mobile app's email-based OTP login.

Deliberately minimal: stdlib smtplib only, no third-party mail service. If
SMTP_ENABLED is false (no SMTP_PASSWORD configured), send_otp_email() logs
the code instead of emailing it — so local dev and CI never need real
credentials. Real send happens over TLS via a Gmail App Password (a normal
Gmail account password is rejected by SMTP AUTH).
"""

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("freshroute.email")


class EmailSendError(Exception):
    pass


def _send_sync(to_email: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
        if settings.SMTP_USE_TLS:
            smtp.starttls()
        smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(message)


def send_otp_email(to_email: str, code: str, expires_in_minutes: int) -> None:
    """Sends (or, if SMTP isn't configured, logs) the OTP code.

    Never raises on a real send failure — a bad SMTP config shouldn't 500
    the /otp/request endpoint and shouldn't leak delivery failures to an
    unauthenticated caller (that would let someone probe which emails have
    accounts). Failures are logged loudly instead; see the caller in
    otp_service.py for the "fail open, log loud" rationale.
    """
    subject = "Your Fresh Supplies login code"
    body = (
        f"Your Fresh Supplies verification code is: {code}\n\n"
        f"This code expires in {expires_in_minutes} minutes. "
        "If you didn't request this, you can safely ignore this email."
    )

    if not settings.SMTP_ENABLED:
        logger.info("SMTP disabled — OTP for %s: %s (would expire in %sm)", to_email, code, expires_in_minutes)
        return

    try:
        _send_sync(to_email, subject, body)
    except Exception as exc:  # smtplib raises several distinct exception types
        logger.error("Failed to send OTP email to %s: %s", to_email, exc)


def send_invite_email(to_email: str, full_name: str, role: str) -> None:
    """Notifies a newly-provisioned account (admin or cooperative-admin
    invite) that they now have access, and how to sign in — there is no
    password to relay; the first login is an emailed OTP (see
    /auth/otp/request, /auth/otp/verify) followed by set-password. Same
    fail-open, log-loud rationale as send_otp_email."""
    subject = "You've been added to Fresh Supplies"
    greeting = f"Hi {full_name}," if full_name else "Hi,"
    body = (
        f"{greeting}\n\n"
        f"You've been added to Fresh Supplies as a {role}.\n\n"
        "To sign in for the first time, go to the login page and choose "
        "\"Email me a sign-in code\" with this email address. You'll set "
        "your own password right after verifying the code.\n\n"
        "If you weren't expecting this, you can safely ignore this email."
    )

    if not settings.SMTP_ENABLED:
        logger.info("SMTP disabled — invite email for %s (role=%s) not sent", to_email, role)
        return

    try:
        _send_sync(to_email, subject, body)
    except Exception as exc:
        logger.error("Failed to send invite email to %s: %s", to_email, exc)
