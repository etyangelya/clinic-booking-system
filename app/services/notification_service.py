import logging
import smtplib
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


def send_confirmation_email(appointment, link_token: str | None = None):
    """Send a booking confirmation email via SMTP. Fire-and-forget: called as a BackgroundTask."""
    result = {"status": "queued", "appointment_id": appointment.id}
    booking_link = None
    if link_token:
        relative_path = f"/appointments/{appointment.id}/view?token={link_token}"
        booking_link = f"{settings.frontend_origins_list[0]}{relative_path}"
        result["booking_link"] = booking_link

    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP not configured; skipping confirmation email for appointment %s", appointment.id)
        return result

    slot_time = appointment.slot_time.strftime("%A, %B %d %Y at %I:%M %p")
    html = (
        f"<p>Hi {appointment.patient.full_name},</p>"
        f"<p>Your appointment with Dr. {appointment.doctor.name} is confirmed for {slot_time}.</p>"
    )
    if booking_link:
        html += (
            f'<p><a href="{booking_link}" '
            'style="display:inline-block;padding:10px 20px;background-color:#0d6efd;'
            'color:#ffffff;text-decoration:none;border-radius:6px;font-family:sans-serif;">'
            "View or manage your booking</a></p>"
        )

    message = MIMEText(html, "html")
    message["Subject"] = "Your appointment is confirmed"
    message["From"] = settings.smtp_from_email or settings.smtp_user
    message["To"] = appointment.patient.email

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(message["From"], [message["To"]], message.as_string())
        result["status"] = "sent"
    except smtplib.SMTPException:
        logger.exception("Failed to send confirmation email for appointment %s", appointment.id)
        result["status"] = "failed"

    return result
