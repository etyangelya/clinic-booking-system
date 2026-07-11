from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(hours=8)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)


def create_access_token(doctor_id: int) -> str:
    expire = datetime.utcnow() + ACCESS_TOKEN_EXPIRE
    payload = {"sub": str(doctor_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return None
    subject = payload.get("sub")
    if subject is None:
        return None
    try:
        return int(subject)
    except ValueError:
        return None
