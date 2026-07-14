from datetime import time

from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule
from tests.conftest import future_slot


def _make_doctor(db_session, name, is_general):
    doc = Doctor(
        name=name,
        specialty="General Medicine" if is_general else "Cardiology",
        work_start=time(0, 0),
        work_end=time(23, 30),
        is_general=is_general,
    )
    db_session.add(doc)
    db_session.flush()
    for day_of_week in range(7):
        db_session.add(
            DoctorSchedule(
                doctor_id=doc.id,
                day_of_week=day_of_week,
                start_time=time(0, 0),
                end_time=time(23, 30),
                slot_duration_minutes=30,
            )
        )
    db_session.commit()
    db_session.refresh(doc)
    return doc


def test_general_availability_excludes_specialists(client, db_session):
    general_doc = _make_doctor(db_session, "Dr. General One", is_general=True)
    specialist_doc = _make_doctor(db_session, "Dr. Specialist One", is_general=False)

    target_date = future_slot().date()
    response = client.get(f"/doctors/availability/general?date={target_date.isoformat()}")
    assert response.status_code == 200

    doctor_ids = {slot["doctor_id"] for slot in response.json()["available_slots"]}
    assert general_doc.id in doctor_ids
    assert specialist_doc.id not in doctor_ids


def test_booking_from_general_slot_assigns_correct_doctor(client, db_session):
    general_doc = _make_doctor(db_session, "Dr. General Two", is_general=True)
    target_date = future_slot().date()

    response = client.get(f"/doctors/availability/general?date={target_date.isoformat()}")
    slot = response.json()["available_slots"][0]

    booking = client.post(
        "/appointments",
        json={
            "doctor_id": slot["doctor_id"],
            "patient_name": "Jane Doe",
            "patient_email": "jane@example.com",
            "slot_time": slot["slot_time"],
        },
    )
    assert booking.status_code == 201
    assert booking.json()["doctor_id"] == general_doc.id


def test_identical_slot_from_two_general_doctors_not_deduplicated(client, db_session):
    _make_doctor(db_session, "Dr. General Three", is_general=True)
    _make_doctor(db_session, "Dr. General Four", is_general=True)

    target_date = future_slot().date()
    response = client.get(f"/doctors/availability/general?date={target_date.isoformat()}")
    slots = response.json()["available_slots"]

    slot_times = [s["slot_time"] for s in slots]
    duplicated_times = {t for t in slot_times if slot_times.count(t) > 1}
    assert duplicated_times, "expected identical slot times from different doctors to both appear"
