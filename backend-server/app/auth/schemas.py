from pydantic import BaseModel


class Loginrequest(BaseModel):
    email: str
    password: str
