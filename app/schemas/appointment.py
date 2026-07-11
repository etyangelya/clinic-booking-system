from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, field_validator


def _to_naive_utc(value: datetime) -> datetime:
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


class BookingRequest(BaseModel):
    doctor_id: int
    patient_name: str
    patient_email: EmailStr
    patient_phone: str | None = None
    slot_time: datetime

    @field_validator("slot_time")
    @classmethod
    def _validate_slot_time(cls, value: datetime) -> datetime:
        return _to_naive_utc(value)


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

    @field_validator("new_slot_time")
    @classmethod
    def _validate_new_slot_time(cls, value: datetime) -> datetime:
        return _to_naive_utc(value)
