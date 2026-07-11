from datetime import datetime

from pydantic import BaseModel, EmailStr


class BookingRequest(BaseModel):
    doctor_id: int
    patient_name: str
    patient_email: EmailStr
    patient_phone: str | None = None
    slot_time: datetime


class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    slot_time: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CancelRequest(BaseModel):
    reason: str | None = None


class RescheduleRequest(BaseModel):
    new_slot_time: datetime
