from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.router import router as auth_router
from app.config import settings
from app.core.exceptions import add_exception_handlers
from app.core.limiter import limiter
from app.database import get_db
from app.routers import appointments, doctors, patients

app = FastAPI(title="Clinic Booking System", version="0.1.0")

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": f"Rate limit exceeded: {exc.detail}"})


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(appointments.router)
app.include_router(doctors.router)
app.include_router(patients.router)
add_exception_handlers(app)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
