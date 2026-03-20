from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Serial
from app.schemas import ValidateResponse, ValidationStatus


def validate_serial(db: Session, serial_key: str, fingerprint: str) -> ValidateResponse:
    serial = db.query(Serial).filter(Serial.serial_key == serial_key).first()

    if not serial:
        return ValidateResponse(valid=False, status=ValidationStatus.NOT_FOUND, message="Invalid serial")

    if not serial.is_active:
        return ValidateResponse(valid=False, status=ValidationStatus.REVOKED, message="Serial revoked")

    if serial.expires_at is not None and serial.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        return ValidateResponse(valid=False, status=ValidationStatus.EXPIRED, message="Serial expired")

    if serial.pre_bound_fingerprint is not None and serial.pre_bound_fingerprint != fingerprint:
        return ValidateResponse(valid=False, status=ValidationStatus.UNAUTHORIZED_MACHINE, message="Unauthorized machine")

    if serial.fingerprint is None:
        serial.fingerprint = fingerprint
        db.commit()
        return ValidateResponse(valid=True)

    if serial.fingerprint == fingerprint:
        return ValidateResponse(valid=True)

    return ValidateResponse(valid=False, status=ValidationStatus.ALREADY_ACTIVATED, message="Serial already activated on another machine")
