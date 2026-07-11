from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_doctor
from app.database import get_db
from app.models.doctor import Doctor
from app.schemas.appointment import AppointmentResponse
from app.schemas.doctor import (
    AvailabilityResponse,
    GeneralAvailabilityResponse,
    GeneralAvailabilitySlot,
    SymptomMatchRequest,
    SymptomMatchResponse,
)
from app.services.availability_service import (
    get_availability_by_speciality,
    get_available_slots,
    get_general_availability,
)
from app.services.booking_service import get_doctor_upcoming_appointments
from app.services.matching_service import match_speciality

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/me/appointments", response_model=list[AppointmentResponse])
def my_appointments(current_doctor: Doctor = Depends(get_current_doctor), db: Session = Depends(get_db)):
    return get_doctor_upcoming_appointments(db, current_doctor.id)


@router.get("/availability/general", response_model=GeneralAvailabilityResponse)
def general_availability(date: date, db: Session = Depends(get_db)):
    slots = get_general_availability(db, date)
    return GeneralAvailabilityResponse(
        date=date,
        available_slots=[GeneralAvailabilitySlot(doctor_id=doctor_id, slot_time=slot_time) for doctor_id, slot_time in slots],
    )


@router.post("/match-speciality", response_model=SymptomMatchResponse)
def match_speciality_endpoint(payload: SymptomMatchRequest, db: Session = Depends(get_db)):
    speciality = match_speciality(payload.symptoms)
    slots = get_availability_by_speciality(db, speciality, payload.date)
    return SymptomMatchResponse(
        matched_speciality=speciality,
        fallback=speciality is None,
        available_slots=[GeneralAvailabilitySlot(doctor_id=doctor_id, slot_time=slot_time) for doctor_id, slot_time in slots],
    )


@router.get("/{doctor_id}/availability", response_model=AvailabilityResponse)
def doctor_availability(doctor_id: int, date: date, db: Session = Depends(get_db)):
    available_slots = get_available_slots(db, doctor_id, date)
    if available_slots is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return AvailabilityResponse(doctor_id=doctor_id, date=date, available_slots=available_slots)
