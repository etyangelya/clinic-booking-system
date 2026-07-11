from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class AppointmentStatus:
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    slot_time = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default=AppointmentStatus.CONFIRMED)
    cancelled_reason = Column(String(255), nullable=True)
    rescheduled_from_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    link_token_hash = Column(String(64), nullable=True)
    link_expires_at = Column(DateTime, nullable=True)

    doctor = relationship("Doctor")
    patient = relationship("Patient")
    rescheduled_from = relationship("Appointment", remote_side=[id])

    __table_args__ = (
        Index(
            "unique_confirmed_slot",
            "doctor_id",
            "slot_time",
            unique=True,
            postgresql_where=(status == AppointmentStatus.CONFIRMED),
            sqlite_where=(status == AppointmentStatus.CONFIRMED),
        ),
        Index("idx_bookings_doctor_time", "doctor_id", "slot_time"),
    )
