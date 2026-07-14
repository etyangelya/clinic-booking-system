from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, verify_password
from app.database import get_db
from app.models.doctor import Doctor

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.email == username).first()
    if doctor is None or not doctor.hashed_password or not verify_password(password, doctor.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token(doctor.id)
    return {"access_token": access_token, "token_type": "bearer"}
