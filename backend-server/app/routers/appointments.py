from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.limiter import limiter
from app.database import get_db
from app.schemas.appointment import AppointmentResponse, BookingRequest, CancelRequest, RescheduleRequest
from app.services.booking_service import (
    cancel_booking,
    cancel_via_link,
    create_booking,
    get_appointment_by_link_token,
    reschedule_booking,
    reschedule_via_link,
)
from app.services.notification_service import send_confirmation_email

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_booking)
def create_appointment(
    request: Request,
    payload: BookingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    appointment, raw_token = create_booking(db, payload)
    background_tasks.add_task(send_confirmation_email, appointment, raw_token)
    return appointment


@router.get("/{appointment_id}/view", response_model=AppointmentResponse)
def view_appointment_via_link(appointment_id: int, token: str, db: Session = Depends(get_db)):
    return get_appointment_by_link_token(db, appointment_id, token)


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(appointment_id: int, payload: CancelRequest, db: Session = Depends(get_db)):
    return cancel_booking(db, appointment_id, payload.reason)


@router.patch("/{appointment_id}/link-cancel", response_model=AppointmentResponse)
def cancel_appointment_via_link(
    appointment_id: int,
    token: str,
    phone: str,
    reason: str | None = None,
    db: Session = Depends(get_db),
):
    return cancel_via_link(db, appointment_id, token, phone, reason)


@router.patch("/{appointment_id}/reschedule", response_model=AppointmentResponse)
def reschedule_appointment(appointment_id: int, payload: RescheduleRequest, db: Session = Depends(get_db)):
    appointment, _raw_token = reschedule_booking(db, appointment_id, payload.new_slot_time)
    return appointment


@router.patch("/{appointment_id}/link-reschedule", response_model=AppointmentResponse)
def reschedule_appointment_via_link(
    appointment_id: int,
    token: str,
    phone: str,
    payload: RescheduleRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    appointment, raw_token = reschedule_via_link(db, appointment_id, token, phone, payload.new_slot_time)
    background_tasks.add_task(send_confirmation_email, appointment, raw_token)
    return appointment
