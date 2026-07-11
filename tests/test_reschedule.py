from tests.conftest import future_slot


def _book(client, doctor, slot_time):
    payload = {
        "doctor_id": doctor.id,
        "patient_name": "Jane Doe",
        "patient_email": "jane@example.com",
        "patient_phone": "1234567890",
        "slot_time": slot_time.isoformat(),
    }
    return client.post("/appointments", json=payload)


def test_reschedule_to_free_slot_succeeds(client, doctor):
    old_slot = future_slot(hour=9)
    new_slot = future_slot(hour=13)
    booking = _book(client, doctor, old_slot)
    appointment_id = booking.json()["id"]

    response = client.patch(
        f"/appointments/{appointment_id}/reschedule",
        json={"new_slot_time": new_slot.isoformat()},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "CONFIRMED"
    assert body["id"] != appointment_id

    old_status = client.patch(f"/appointments/{appointment_id}/cancel", json={"reason": "check state"})
    assert old_status.status_code == 409  # already cancelled by the reschedule

    rebooked_old_slot = _book(client, doctor, old_slot)
    assert rebooked_old_slot.status_code == 201  # old slot is free again


def test_reschedule_to_taken_slot_fails_and_leaves_original_untouched(client, doctor):
    old_slot = future_slot(hour=9)
    taken_slot = future_slot(hour=16)

    original = _book(client, doctor, old_slot)
    original_id = original.json()["id"]

    other = _book(client, doctor, taken_slot)
    assert other.status_code == 201

    response = client.patch(
        f"/appointments/{original_id}/reschedule",
        json={"new_slot_time": taken_slot.isoformat()},
    )
    assert response.status_code == 409

    cancel_response = client.patch(f"/appointments/{original_id}/cancel", json={"reason": "verify still confirmed"})
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"


def test_reschedule_cancelled_appointment_fails(client, doctor):
    old_slot = future_slot(hour=9)
    new_slot = future_slot(hour=17)
    booking = _book(client, doctor, old_slot)
    appointment_id = booking.json()["id"]

    client.patch(f"/appointments/{appointment_id}/cancel", json={"reason": "no longer needed"})

    response = client.patch(
        f"/appointments/{appointment_id}/reschedule",
        json={"new_slot_time": new_slot.isoformat()},
    )
    assert response.status_code == 409
