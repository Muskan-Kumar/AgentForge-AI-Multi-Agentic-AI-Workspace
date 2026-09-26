import smtplib
from email.message import EmailMessage

from src.core.config import settings


def send_password_reset_email(
    email: str,
    reset_token: str,
) -> None:

    reset_link = (
        f"{settings.FRONTEND_RESET_URL}"
        f"?token={reset_token}"
    )

    message = EmailMessage()

    message["Subject"] = "AgentForge AI - Password Reset"
    message["From"] = settings.EMAIL_FROM
    message["To"] = email

    message.set_content(
        f"""
Hello,

We received a request to reset your AgentForge AI password.

Use the following link to reset your password:

{reset_link}

This password reset link will expire in 15 minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
AgentForge AI
"""
    )

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
    ) as server:

        server.starttls()

        server.login(
            settings.SMTP_USERNAME,
            settings.SMTP_PASSWORD,
        )

        server.send_message(message)
        