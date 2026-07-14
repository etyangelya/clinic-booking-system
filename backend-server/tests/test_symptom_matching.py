from datetime import time

from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule
from tests.conftest import future_slot


def _make_doctor(db_session, name, specialty):
    doc = Doctor(
        name=name,
        specialty=specialty,
        work_start=time(0, 0),
        work_end=time(23, 30),
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


def test_symptom_match_returns_speciality_and_its_doctors_availability(client, db_session):
    _make_doctor(db_session, "Dr. Molar", "Dentistry")
    dermatologist = _make_doctor(db_session, "Dr. Skin", "Dermatology")

    target_date = future_slot().date()
    response = client.post(
        "/doctors/match-speciality",
        json={"symptoms": "I have a bad skin rash", "date": target_date.isoformat()},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["matched_speciality"] == "Dermatology"
    assert body["fallback"] is False
    doctor_ids = {slot["doctor_id"] for slot in body["available_slots"]}
    assert doctor_ids == {dermatologist.id}


def test_symptom_match_falls_back_when_no_keyword_matches(client, db_session):
    doc_a = _make_doctor(db_session, "Dr. Molar", "Dentistry")
    doc_b = _make_doctor(db_session, "Dr. Skin", "Dermatology")

    target_date = future_slot().date()
    response = client.post(
        "/doctors/match-speciality",
        json={"symptoms": "feeling generally unwell", "date": target_date.isoformat()},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["matched_speciality"] is None
    assert body["fallback"] is True
    doctor_ids = {slot["doctor_id"] for slot in body["available_slots"]}
    assert doctor_ids == {doc_a.id, doc_b.id}
