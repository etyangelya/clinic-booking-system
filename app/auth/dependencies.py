from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.service import decode_access_token
from app.database import get_db
from app.models.doctor import Doctor

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_doctor(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Doctor:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    doctor_id = decode_access_token(token)
    if doctor_id is None:
        raise credentials_error

    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor is None or not doctor.is_active:
        raise credentials_error
    return doctor
