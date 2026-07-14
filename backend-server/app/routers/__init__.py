from app.routers.appointments import router as appointments_router
from app.routers.doctors import router as doctors_router
from app.routers.patients import router as patients_router

__all__ = ["appointments_router", "doctors_router", "patients_router"]
