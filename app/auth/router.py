from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.service import create_access_token, verify_password
from app.database import get_db
from app.models.doctor import Doctor

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.email == form_data.username).first()
    if doctor is None or not doctor.hashed_password or not verify_password(form_data.password, doctor.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token(doctor.id)
    return {"access_token": access_token, "token_type": "bearer"}
