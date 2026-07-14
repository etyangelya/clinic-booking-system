from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.auth.security import decode_access_token
from app.database import get_db
from app.models.doctor import Doctor

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
bearer_scheme = HTTPBearer()


def get_current_doctor(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)) -> Doctor:
    token= credentials.credentials
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload= decode_access_token(token)
    print(payload)
    doctor_id= payload
    jti: None
    if doctor_id is None:
        raise credentials_error

    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor is None or not doctor.is_active:
        raise credentials_error
    return doctor
