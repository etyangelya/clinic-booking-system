from datetime import datetime, timedelta

from app.schemas.appointment import BookingRequest
from app.services.booking_service import create_booking
from tests.conftest import future_slot


def _book_directly(db_session, doctor, phone="5551234567", slot=None):
    payload = BookingRequest(
        doctor_id=doctor.id,
        patient_name="Jane Doe",
        patient_email="jane@example.com",
        patient_phone=phone,
        slot_time=slot or future_slot(),
    )
    appointment, raw_token = create_booking(db_session, payload)
    return appointment, raw_token


def test_view_with_valid_token_returns_booking_details(client, db_session, doctor):
    appointment, raw_token = _book_directly(db_session, doctor)

    response = client.get(f"/appointments/{appointment.id}/view?token={raw_token}")
    assert response.status_code == 200
    assert response.json()["id"] == appointment.id


def test_view_with_invalid_token_returns_404(client, db_session, doctor):
    appointment, _ = _book_directly(db_session, doctor)

    tampered = client.get(f"/appointments/{appointment.id}/view?token=not-the-real-token")
    nonexistent = client.get("/appointments/999999/view?token=not-the-real-token")

    assert tampered.status_code == 404
    assert nonexistent.status_code == 404
    assert tampered.json() == nonexistent.json()


def test_view_with_expired_token_returns_404(client, db_session, doctor):
    appointment, raw_token = _book_directly(db_session, doctor)
    appointment.link_expires_at = datetime.utcnow() - timedelta(days=1)
    db_session.commit()

    response = client.get(f"/appointments/{appointment.id}/view?token={raw_token}")
    assert response.status_code == 404


def test_link_cancel_with_correct_phone_succeeds(client, db_session, doctor):
    appointment, raw_token = _book_directly(db_session, doctor, phone="5551234567")

    response = client.patch(
        f"/appointments/{appointment.id}/link-cancel?token={raw_token}&phone_last4=4567"
    )
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_link_cancel_with_wrong_phone_digits_rejected(client, db_session, doctor):
    appointment, raw_token = _book_directly(db_session, doctor, phone="5551234567")

    response = client.patch(
        f"/appointments/{appointment.id}/link-cancel?token={raw_token}&phone_last4=9999"
    )
    assert response.status_code == 403

    # confirm the appointment was left untouched
    view = client.get(f"/appointments/{appointment.id}/view?token={raw_token}")
    assert view.json()["status"] == "CONFIRMED"


def test_link_cancel_with_tampered_token_rejected(client, db_session, doctor):
    appointment, _ = _book_directly(db_session, doctor, phone="5551234567")

    response = client.patch(
        f"/appointments/{appointment.id}/link-cancel?token=tampered-token&phone_last4=4567"
    )
    assert response.status_code == 404
