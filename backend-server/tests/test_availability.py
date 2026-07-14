from datetime import timedelta

from tests.conftest import future_slot


def test_doctor_not_found_returns_404(client):
    tomorrow = future_slot().date()
    response = client.get(f"/doctors/999999/availability?date={tomorrow.isoformat()}")
    assert response.status_code == 404


def test_availability_lists_open_slots(client, doctor):
    target_date = future_slot().date()
    response = client.get(f"/doctors/{doctor.id}/availability?date={target_date.isoformat()}")
    assert response.status_code == 200
    body = response.json()
    assert body["doctor_id"] == doctor.id
    assert len(body["available_slots"]) > 0


def test_availability_excludes_booked_slot(client, doctor):
    slot = future_slot(hour=10)
    booking_payload = {
        "doctor_id": doctor.id,
        "patient_name": "Jane Doe",
        "patient_email": "jane@example.com",
        "patient_phone": "1234567890",
        "slot_time": slot.isoformat(),
    }
    booked = client.post("/appointments", json=booking_payload)
    assert booked.status_code == 201

    response = client.get(f"/doctors/{doctor.id}/availability?date={slot.date().isoformat()}")
    available = response.json()["available_slots"]
    assert slot.isoformat() not in available


def test_availability_excludes_leave(client, doctor, db_session):
    from app.models.doctor_leave import DoctorLeave

    target_date = future_slot(hour=0).replace(hour=0, minute=0)
    leave = DoctorLeave(
        doctor_id=doctor.id,
        start_datetime=target_date,
        end_datetime=target_date + timedelta(hours=23, minutes=30),
        reason="Conference",
    )
    db_session.add(leave)
    db_session.commit()

    response = client.get(f"/doctors/{doctor.id}/availability?date={target_date.date().isoformat()}")
    assert response.json()["available_slots"] == []
