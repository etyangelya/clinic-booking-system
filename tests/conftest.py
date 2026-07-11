from datetime import datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth.service import hash_password
from app.core.limiter import limiter
from app.database import Base, get_db
from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule
from main import app

DOCTOR_PASSWORD = "correct-horse-battery-staple"

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def future_slot(days_ahead: int = 1, hour: int = 10, minute: int = 0) -> datetime:
    """A datetime guaranteed to be within the test doctor's working hours and >1h from now."""
    target = datetime.utcnow() + timedelta(days=days_ahead)
    return target.replace(hour=hour, minute=minute, second=0, microsecond=0)


@pytest.fixture()
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    limiter.enabled = False
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    limiter.enabled = True


def _make_doctor(db_session, name: str, email: str) -> Doctor:
    """A doctor available every day of the week, all day, in 30-minute slots."""
    doc = Doctor(
        name=name,
        specialty="General Medicine",
        work_start=time(0, 0),
        work_end=time(23, 30),
        email=email,
        hashed_password=hash_password(DOCTOR_PASSWORD),
    )
    db_session.add(doc)
    db_session.flush()

    for day_of_week in range(7):
        db_session.add(
            DoctorSchedule(
                doctor_id=doc.id,
                day_of_week=day_of_week,
                start_time=time(0, 0),
                end_time=time(23, 30),
                slot_duration_minutes=30,
            )
        )
    db_session.commit()
    db_session.refresh(doc)
    return doc


@pytest.fixture()
def doctor(db_session):
    return _make_doctor(db_session, "Dr. Jane Smith", "jane.smith@clinic.test")


@pytest.fixture()
def other_doctor(db_session):
    return _make_doctor(db_session, "Dr. Alex Kim", "alex.kim@clinic.test")
