from datetime import date, datetime

from pydantic import BaseModel


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialty: str
    is_active: bool

    class Config:
        from_attributes = True


class AvailabilityResponse(BaseModel):
    doctor_id: int
    date: date
    available_slots: list[datetime]


class GeneralAvailabilitySlot(BaseModel):
    doctor_id: int
    slot_time: datetime


class GeneralAvailabilityResponse(BaseModel):
    date: date
    available_slots: list[GeneralAvailabilitySlot]


class SymptomMatchRequest(BaseModel):
    symptoms: str
    date: date


class SymptomMatchResponse(BaseModel):
    matched_speciality: str | None
    fallback: bool
    available_slots: list[GeneralAvailabilitySlot]
