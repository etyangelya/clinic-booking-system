from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AlreadyCancelledError,
    AppointmentNotFoundError,
    InvalidLinkError,
    OutsideWorkingHoursError,
    PastDateError,
    SlotTakenError,
)
from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.models.doctor_leave import DoctorLeave
from app.models.doctor_schedule import DoctorSchedule
from app.models.patient import Patient
from app.schemas.appointment import BookingRequest
from app.services.magic_link_service import generate_link_token, hash_token, verify_token

MIN_LEAD_TIME = timedelta(hours=1)


def _validate_slot(db: Session, doctor: Doctor, slot_time: datetime, exclude_appointment_id: int | None = None) -> None:
    now = datetime.utcnow()
    if slot_time < now + MIN_LEAD_TIME:
        raise PastDateError("Slot must be booked at least 1 hour in advance")

    slot_date = slot_time.date()
    previous_date = slot_date - timedelta(days=1)
    schedules = (
        db.query(DoctorSchedule)
        .filter(DoctorSchedule.doctor_id == doctor.id)
        .filter(DoctorSchedule.day_of_week.in_((slot_date.weekday(), previous_date.weekday())))
        .all()
    )

    matched_schedule = None
    for schedule in schedules:
        crosses_midnight = schedule.end_time <= schedule.start_time
        if schedule.day_of_week == slot_date.weekday():
            block_start = datetime.combine(slot_date, schedule.start_time)
            block_end_date = slot_date + timedelta(days=1) if crosses_midnight else slot_date
            block_end = datetime.combine(block_end_date, schedule.end_time)
        elif schedule.day_of_week == previous_date.weekday() and crosses_midnight:
            # The tail of an overnight shift that started the day before.
            block_start = datetime.combine(previous_date, schedule.start_time)
            block_end = datetime.combine(slot_date, schedule.end_time)
        else:
            continue

        if block_start <= slot_time < block_end:
            offset_minutes = (slot_time - block_start).total_seconds() / 60
            if offset_minutes % schedule.slot_duration_minutes == 0:
                matched_schedule = schedule
                break

    if matched_schedule is None:
        raise OutsideWorkingHoursError("Slot is outside the doctor's working hours")

    slot_end = slot_time + timedelta(minutes=matched_schedule.slot_duration_minutes)
    leaves = db.query(DoctorLeave).filter(DoctorLeave.doctor_id == doctor.id).all()
    if any(leave.start_datetime < slot_end and leave.end_datetime > slot_time for leave in leaves):
        raise OutsideWorkingHoursError("Doctor is on leave at this time")

    existing_query = (
        db.query(Appointment)
        .filter(Appointment.doctor_id == doctor.id)
        .filter(Appointment.slot_time == slot_time)
        .filter(Appointment.status == AppointmentStatus.CONFIRMED)
    )
    if exclude_appointment_id is not None:
        existing_query = existing_query.filter(Appointment.id != exclude_appointment_id)
    if existing_query.first() is not None:
        raise SlotTakenError()


def _get_or_create_patient(db: Session, name: str, email: str, phone: str | None) -> Patient:
    patient = db.query(Patient).filter(Patient.email == email).first()
    if patient is None:
        patient = Patient(full_name=name, email=email, phone=phone)
        db.add(patient)
        db.flush()
    return patient


def get_upcoming_appointments(db: Session, patient_id: int) -> list[Appointment]:
    return (
        db.query(Appointment)
        .filter(Appointment.patient_id == patient_id)
        .filter(Appointment.status == AppointmentStatus.CONFIRMED)
        .filter(Appointment.slot_time >= datetime.utcnow())
        .order_by(Appointment.slot_time.asc())
        .all()
    )


def get_doctor_upcoming_appointments(db: Session, doctor_id: int) -> list[Appointment]:
    return (
        db.query(Appointment)
        .filter(Appointment.doctor_id == doctor_id)
        .filter(Appointment.status == AppointmentStatus.CONFIRMED)
        .filter(Appointment.slot_time >= datetime.utcnow())
        .order_by(Appointment.slot_time.asc())
        .all()
    )


def create_booking(db: Session, payload: BookingRequest) -> tuple[Appointment, str]:
    doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id).with_for_update().first()
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")

    _validate_slot(db, doctor, payload.slot_time)

    patient = _get_or_create_patient(db, payload.patient_name, str(payload.patient_email), payload.patient_phone)

    raw_token = generate_link_token()
    appointment = Appointment(
        doctor_id=doctor.id,
        patient_id=patient.id,
        slot_time=payload.slot_time,
        status=AppointmentStatus.CONFIRMED,
        link_token_hash=hash_token(raw_token),
        link_expires_at=payload.slot_time,
    )
    db.add(appointment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise SlotTakenError()
    db.refresh(appointment)
    return appointment, raw_token


def get_appointment_by_link_token(db: Session, appointment_id: int, raw_token: str) -> Appointment:
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if (
        appointment is None
        or not verify_token(raw_token, appointment.link_token_hash)
        or appointment.link_expires_at is None
        or appointment.link_expires_at < datetime.utcnow()
    ):
        # Deliberately identical to the "not found" case so a tampered or
        # expired token cannot be used to infer whether the appointment exists.
        raise AppointmentNotFoundError()
    return appointment


def cancel_via_link(db: Session, appointment_id: int, raw_token: str, phone_last4: str) -> Appointment:
    appointment = get_appointment_by_link_token(db, appointment_id, raw_token)

    patient_phone = appointment.patient.phone or ""
    if patient_phone[-4:] != phone_last4 or len(phone_last4) != 4:
        raise InvalidLinkError("Phone verification failed")

    if appointment.status == AppointmentStatus.CANCELLED:
        raise AlreadyCancelledError()

    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancelled_reason = "Cancelled by patient via booking link"
    db.commit()
    db.refresh(appointment)
    return appointment


def cancel_booking(db: Session, appointment_id: int, reason: str | None) -> Appointment:
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if appointment is None:
        raise AppointmentNotFoundError()
    if appointment.status == AppointmentStatus.CANCELLED:
        raise AlreadyCancelledError()

    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancelled_reason = reason
    db.commit()
    db.refresh(appointment)
    return appointment


def reschedule_booking(db: Session, appointment_id: int, new_slot_time: datetime) -> Appointment:
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).with_for_update().first()
    if appointment is None:
        raise AppointmentNotFoundError()
    if appointment.status == AppointmentStatus.CANCELLED:
        raise AlreadyCancelledError()

    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).with_for_update().first()
    _validate_slot(db, doctor, new_slot_time, exclude_appointment_id=appointment.id)

    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancelled_reason = "Rescheduled"

    raw_token = generate_link_token()
    new_appointment = Appointment(
        doctor_id=appointment.doctor_id,
        patient_id=appointment.patient_id,
        slot_time=new_slot_time,
        status=AppointmentStatus.CONFIRMED,
        rescheduled_from_id=appointment.id,
        link_token_hash=hash_token(raw_token),
        link_expires_at=new_slot_time,
    )
    db.add(new_appointment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise SlotTakenError()
    db.refresh(new_appointment)
    return new_appointment
