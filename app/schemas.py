from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ValidationStatus(str, Enum):
    NOT_FOUND = "NOT_FOUND"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    UNAUTHORIZED_MACHINE = "UNAUTHORIZED_MACHINE"
    ALREADY_ACTIVATED = "ALREADY_ACTIVATED"


class SerialCreate(BaseModel):
    serial_key: Optional[str] = None
    pre_bound_fingerprint: Optional[str] = None
    expires_at: Optional[datetime] = None


class SerialResponse(BaseModel):
    id: str
    serial_key: str
    fingerprint: Optional[str]
    pre_bound_fingerprint: Optional[str]
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ValidateRequest(BaseModel):
    serial_key: str = Field(max_length=256)
    fingerprint: str = Field(max_length=512)


class ValidateResponse(BaseModel):
    valid: bool
    status: Optional[ValidationStatus] = None
    message: Optional[str] = None
