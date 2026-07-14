from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.appointment import AppointmentResponse
from app.services.booking_service import get_upcoming_appointments

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/{patient_id}/appointments", response_model=list[AppointmentResponse])
def patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    return get_upcoming_appointments(db, patient_id)
