from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ValidateRequest
from app.services.serial_service import validate_serial

router = APIRouter()


@router.post("/validate")
def validate(body: ValidateRequest, db: Session = Depends(get_db)):
    response = validate_serial(db, body.serial_key, body.fingerprint)

    if response.valid:
        status_code = 200
    elif response.message == "Serial inválido":
        status_code = 401
    else:
        status_code = 403

    return JSONResponse(status_code=status_code, content=response.model_dump())
