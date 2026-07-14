from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from tests.conftest import future_slot


def _booking_payload(doctor_id, slot_time, email="jane@example.com"):
    return {
        "doctor_id": doctor_id,
        "patient_name": "Jane Doe",
        "patient_email": email,
        "patient_phone": "1234567890",
        "slot_time": slot_time.isoformat(),
    }


def test_create_booking_succeeds(client, doctor):
    response = client.post("/appointments", json=_booking_payload(doctor.id, future_slot()))
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "CONFIRMED"
    assert body["doctor_id"] == doctor.id


def test_booking_already_taken_slot_fails(client, doctor):
    slot = future_slot(hour=11)
    first = client.post("/appointments", json=_booking_payload(doctor.id, slot))
    assert first.status_code == 201

    second = client.post("/appointments", json=_booking_payload(doctor.id, slot, email="other@example.com"))
    assert second.status_code == 409


def test_booking_outside_working_hours_fails(client, doctor):
    slot = future_slot(hour=23, minute=45)
    response = client.post("/appointments", json=_booking_payload(doctor.id, slot))
    assert response.status_code == 400


def test_booking_past_datetime_fails(client, doctor):
    past_slot = future_slot(days_ahead=-1)
    response = client.post("/appointments", json=_booking_payload(doctor.id, past_slot))
    assert response.status_code == 400


def test_booking_within_one_hour_fails(client, doctor):
    from datetime import datetime

    soon = (datetime.utcnow() + timedelta(minutes=30)).replace(second=0, microsecond=0)
    response = client.post("/appointments", json=_booking_payload(doctor.id, soon))
    assert response.status_code == 400


def test_concurrent_bookings_only_one_succeeds(client, doctor):
    slot = future_slot(hour=14)

    def book(email):
        return client.post("/appointments", json=_booking_payload(doctor.id, slot, email=email))

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(book, "patient-a@example.com"),
            executor.submit(book, "patient-b@example.com"),
        ]
        results = [f.result() for f in futures]

    status_codes = sorted(r.status_code for r in results)
    assert status_codes == [201, 409]
