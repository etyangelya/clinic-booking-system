from datetime import time

from app.auth.security import hash_password
from app.database import SessionLocal
from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule

DEFAULT_PASSWORD = "ChangeMe123!"

DAY_SHIFT = {"start": time(7, 0), "end": time(19, 0)}
NIGHT_SHIFT = {"start": time(21, 0), "end": time(5, 0)}
SLOT_DURATION_MINUTES = 30

# Monday=0 ... Sunday=6. Each doctor works 4 days/nights and gets 3 off,
# staggered across the week so the clinic has day coverage every day.
DOCTORS = [
    {
        "name": "Dr. Tom Kamau",
        "specialty": "General Medicine",
        "is_general": True,
        "email": "tom.kamau@clinic.com",
        "shift": DAY_SHIFT,
        "working_days": [0, 1, 2, 3],  # Mon-Thu
    },
    {
        "name": "Dr. Grace Wanjiru",
        "specialty": "General Medicine",
        "is_general": True,
        "email": "grace.wanjiru@clinic.com",
        "shift": DAY_SHIFT,
        "working_days": [2, 3, 4, 5],  # Wed-Sat
    },
    {
        "name": "Dr. Peter Otieno",
        "specialty": "General Medicine",
        "is_general": True,
        "email": "peter.otieno@clinic.com",
        "shift": NIGHT_SHIFT,
        "working_days": [0, 2, 4, 5],  # Mon, Wed, Fri, Sat nights
    },
    {
        "name": "Dr. Faith Cherono",
        "specialty": "Dermatology",
        "is_general": False,
        "email": "faith.cherono@clinic.com",
        "shift": DAY_SHIFT,
        "working_days": [4, 5, 6, 0],  # Fri-Mon
    },
    {
        "name": "Dr. Hiroshi Tanaka",  # the one foreign name among the five
        "specialty": "Dentistry",
        "is_general": False,
        "email": "hiroshi.tanaka@clinic.com",
        "shift": DAY_SHIFT,
        "working_days": [6, 0, 1, 2],  # Sun-Wed
    },
]


def seed_doctors() -> None:
    db = SessionLocal()
    try:
        for entry in DOCTORS:
            if db.query(Doctor).filter(Doctor.email == entry["email"]).first():
                print(f"Skipping {entry['name']} (already exists)")
                continue

            doctor = Doctor(
                name=entry["name"],
                specialty=entry["specialty"],
                is_general=entry["is_general"],
                work_start=entry["shift"]["start"],
                work_end=entry["shift"]["end"],
                is_active=True,
                email=entry["email"],
                hashed_password=hash_password(DEFAULT_PASSWORD),
            )
            db.add(doctor)
            db.flush()

            for day_of_week in entry["working_days"]:
                db.add(
                    DoctorSchedule(
                        doctor_id=doctor.id,
                        day_of_week=day_of_week,
                        start_time=entry["shift"]["start"],
                        end_time=entry["shift"]["end"],
                        slot_duration_minutes=SLOT_DURATION_MINUTES,
                    )
                )
            print(f"Created {entry['name']} ({entry['specialty']}, {len(entry['working_days'])} days/week)")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_doctors()
    print(f"\nDefault password for all seeded doctors: {DEFAULT_PASSWORD}")
