from datetime import datetime, time, timedelta

from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule


def _next_datetime_for_weekday(weekday: int, hour: int, minute: int = 0, days_ahead_min: int = 2) -> datetime:
    base = datetime.utcnow() + timedelta(days=days_ahead_min)
    while base.weekday() != weekday:
        base += timedelta(days=1)
    return base.replace(hour=hour, minute=minute, second=0, microsecond=0)


def _night_doctor(db_session):
    monday_night = _next_datetime_for_weekday(weekday=0, hour=21)
    doc = Doctor(
        name="Dr. Night Owl",
        specialty="General Medicine",
        work_start=time(21, 0),
        work_end=time(5, 0),
        is_general=True,
    )
    db_session.add(doc)
    db_session.flush()
    db_session.add(
        DoctorSchedule(
            doctor_id=doc.id,
            day_of_week=0,  # Monday
            start_time=time(21, 0),
            end_time=time(5, 0),
            slot_duration_minutes=30,
        )
    )
    db_session.commit()
    db_session.refresh(doc)
    return doc, monday_night


def test_overnight_availability_spans_past_midnight(client, db_session):
    doctor, monday_night = _night_doctor(db_session)

    response = client.get(f"/doctors/{doctor.id}/availability?date={monday_night.date().isoformat()}")
    assert response.status_code == 200
    slots = response.json()["available_slots"]

    assert monday_night.isoformat() in slots  # 21:00 Monday
    tuesday_early_morning = (monday_night + timedelta(hours=7, minutes=30)).isoformat()  # 04:30 Tuesday
    assert tuesday_early_morning in slots
    tuesday_after_shift = (monday_night + timedelta(hours=9)).isoformat()  # 06:00 Tuesday, past end_time
    assert tuesday_after_shift not in slots


def test_booking_at_start_of_overnight_shift_succeeds(client, db_session):
    doctor, monday_night = _night_doctor(db_session)

    response = client.post(
        "/appointments",
        json={
            "doctor_id": doctor.id,
            "patient_name": "Jane Doe",
            "patient_email": "jane@example.com",
            "slot_time": monday_night.isoformat(),
        },
    )
    assert response.status_code == 201


def test_booking_after_midnight_within_overnight_shift_succeeds(client, db_session):
    doctor, monday_night = _night_doctor(db_session)
    tuesday_2am = monday_night + timedelta(hours=5)  # Tuesday 02:00, part of Monday's shift

    response = client.post(
        "/appointments",
        json={
            "doctor_id": doctor.id,
            "patient_name": "Jane Doe",
            "patient_email": "jane@example.com",
            "slot_time": tuesday_2am.isoformat(),
        },
    )
    assert response.status_code == 201


def test_booking_past_end_of_overnight_shift_fails(client, db_session):
    doctor, monday_night = _night_doctor(db_session)
    tuesday_6am = monday_night + timedelta(hours=9)  # past the 05:00 end time

    response = client.post(
        "/appointments",
        json={
            "doctor_id": doctor.id,
            "patient_name": "Jane Doe",
            "patient_email": "jane@example.com",
            "slot_time": tuesday_6am.isoformat(),
        },
    )
    assert response.status_code == 400
