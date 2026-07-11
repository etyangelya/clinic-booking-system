def send_confirmation_email(appointment, link_token: str | None = None):
    """Placeholder confirmation email sender."""
    result = {"status": "queued", "appointment_id": appointment.id}
    if link_token:
        result["booking_link"] = f"/appointments/{appointment.id}/view?token={link_token}"
    return result
