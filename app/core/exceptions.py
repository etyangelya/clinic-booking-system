from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse


class SlotTakenError(Exception):
    def __init__(self, detail: str = "The selected time slot is already taken"):
        self.detail = detail
        super().__init__(detail)


class PastDateError(Exception):
    def __init__(self, detail: str = "Cannot book a slot in the past"):
        self.detail = detail
        super().__init__(detail)


class OutsideWorkingHoursError(Exception):
    def __init__(self, detail: str = "Slot is outside the doctor's working hours"):
        self.detail = detail
        super().__init__(detail)


class AlreadyCancelledError(Exception):
    def __init__(self, detail: str = "Appointment is already cancelled"):
        self.detail = detail
        super().__init__(detail)


class AppointmentNotFoundError(Exception):
    def __init__(self, detail: str = "Appointment not found"):
        self.detail = detail
        super().__init__(detail)


class InvalidLinkError(Exception):
    def __init__(self, detail: str = "Verification failed"):
        self.detail = detail
        super().__init__(detail)


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(SlotTakenError)
    async def slot_taken_handler(request: Request, exc: SlotTakenError):
        return JSONResponse(status_code=409, content={"detail": exc.detail})

    @app.exception_handler(AlreadyCancelledError)
    async def already_cancelled_handler(request: Request, exc: AlreadyCancelledError):
        return JSONResponse(status_code=409, content={"detail": exc.detail})

    @app.exception_handler(PastDateError)
    async def past_date_handler(request: Request, exc: PastDateError):
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    @app.exception_handler(OutsideWorkingHoursError)
    async def outside_working_hours_handler(request: Request, exc: OutsideWorkingHoursError):
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    @app.exception_handler(AppointmentNotFoundError)
    async def appointment_not_found_handler(request: Request, exc: AppointmentNotFoundError):
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    @app.exception_handler(InvalidLinkError)
    async def invalid_link_handler(request: Request, exc: InvalidLinkError):
        return JSONResponse(status_code=403, content={"detail": exc.detail})

    @app.exception_handler(FastAPIHTTPException)
    async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
