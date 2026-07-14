from sqlalchemy import Column, Date, Integer, Time, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_duration_minutes = Column(Integer, nullable=False, default=30)
    date = Column(Date, nullable=True)

    doctor = relationship("Doctor")
