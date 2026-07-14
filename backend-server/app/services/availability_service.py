from datetime import date as date_type, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.models.doctor_leave import DoctorLeave
from app.models.doctor_schedule import DoctorSchedule


def _slots_overlap_leave(slot_start: datetime, slot_end: datetime, leaves: list[DoctorLeave]) -> bool:
    return any(leave.start_datetime < slot_end and leave.end_datetime > slot_start for leave in leaves)


def get_available_slots(db: Session, doctor_id: int, target_date: date_type) -> list[datetime] | None:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor is None:
        return None

    day_of_week = target_date.weekday()
    schedules = (
        db.query(DoctorSchedule)
        .filter(DoctorSchedule.doctor_id == doctor_id)
        .filter(DoctorSchedule.day_of_week == day_of_week)
        .all()
    )
    if not schedules:
        return []

    leaves = db.query(DoctorLeave).filter(DoctorLeave.doctor_id == doctor_id).all()

    day_start = datetime.combine(target_date, datetime.min.time())
    # Widened to 2 days so overnight shifts (end_time <= start_time, spilling
    # past midnight into the next calendar day) still see their bookings.
    day_end = day_start + timedelta(days=2)
    booked_slots = {
        appointment.slot_time
        for appointment in (
            db.query(Appointment)
            .filter(Appointment.doctor_id == doctor_id)
            .filter(Appointment.status == AppointmentStatus.CONFIRMED)
            .filter(Appointment.slot_time >= day_start)
            .filter(Appointment.slot_time < day_end)
            .all()
        )
    }

    now = datetime.utcnow()
    available: list[datetime] = []
    for schedule in schedules:
        duration = timedelta(minutes=schedule.slot_duration_minutes)
        slot_start = datetime.combine(target_date, schedule.start_time)
        crosses_midnight = schedule.end_time <= schedule.start_time
        block_end_date = target_date + timedelta(days=1) if crosses_midnight else target_date
        block_end = datetime.combine(block_end_date, schedule.end_time)

        while slot_start + duration <= block_end:
            slot_end = slot_start + duration
            if (
                slot_start > now
                and slot_start not in booked_slots
                and not _slots_overlap_leave(slot_start, slot_end, leaves)
            ):
                available.append(slot_start)
            slot_start = slot_end

    return sorted(available)


def get_general_availability(db: Session, target_date: date_type) -> list[tuple[int, str, datetime]]:
    general_doctors = db.query(Doctor).filter(Doctor.is_general.is_(True)).filter(Doctor.is_active.is_(True)).all()

    merged: list[tuple[int, str, datetime]] = []
    for doctor in general_doctors:
        slots = get_available_slots(db, doctor.id, target_date) or []
        merged.extend((doctor.id, doctor.name, slot) for slot in slots)

    return sorted(merged, key=lambda triple: triple[2])


def get_availability_by_speciality(
    db: Session, speciality: str | None, target_date: date_type
) -> list[tuple[int, str, datetime]]:
    """Merged availability for doctors in a speciality, or all active doctors if speciality is None."""
    query = db.query(Doctor).filter(Doctor.is_active.is_(True))
    if speciality is not None:
        query = query.filter(Doctor.specialty == speciality)
    doctors = query.all()

    merged: list[tuple[int, str, datetime]] = []
    for doctor in doctors:
        slots = get_available_slots(db, doctor.id, target_date) or []
        merged.extend((doctor.id, doctor.name, slot) for slot in slots)

    return sorted(merged, key=lambda triple: triple[2])
