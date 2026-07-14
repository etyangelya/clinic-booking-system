from sqlalchemy import Boolean, Column, Integer, String, Time, false

from app.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialty = Column(String(100), nullable=False)
    work_start = Column(Time, nullable=False)
    work_end = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True)
    is_general = Column(Boolean, nullable=False, default=False, server_default=false())
    email = Column(String(255), nullable=True, unique=True)
    hashed_password = Column(String(255), nullable=True)
