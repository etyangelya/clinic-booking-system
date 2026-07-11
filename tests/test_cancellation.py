from tests.conftest import future_slot


def _book(client, doctor, slot_time=None):
    payload = {
        "doctor_id": doctor.id,
        "patient_name": "Jane Doe",
        "patient_email": "jane@example.com",
        "patient_phone": "1234567890",
        "slot_time": (slot_time or future_slot()).isoformat(),
    }
    return client.post("/appointments", json=payload)


def test_cancel_confirmed_appointment_succeeds(client, doctor):
    booking = _book(client, doctor)
    appointment_id = booking.json()["id"]

    response = client.patch(f"/appointments/{appointment_id}/cancel", json={"reason": "Patient unavailable"})
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_cancelled_slot_becomes_available_again(client, doctor):
    slot = future_slot(hour=15)
    booking = _book(client, doctor, slot)
    appointment_id = booking.json()["id"]

    client.patch(f"/appointments/{appointment_id}/cancel", json={"reason": "no longer needed"})

    rebooked = client.post(
        "/appointments",
        json={
            "doctor_id": doctor.id,
            "patient_name": "John Roe",
            "patient_email": "john@example.com",
            "patient_phone": "0987654321",
            "slot_time": slot.isoformat(),
        },
    )
    assert rebooked.status_code == 201


def test_cancel_already_cancelled_appointment_fails(client, doctor):
    booking = _book(client, doctor)
    appointment_id = booking.json()["id"]
    client.patch(f"/appointments/{appointment_id}/cancel", json={"reason": "first cancel"})

    response = client.patch(f"/appointments/{appointment_id}/cancel", json={"reason": "second cancel"})
    assert response.status_code == 409


def test_cancel_nonexistent_appointment_fails(client, doctor):
    response = client.patch("/appointments/999999/cancel", json={"reason": "does not exist"})
    assert response.status_code == 404
