from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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
    serial_key: str
    fingerprint: str


class ValidateResponse(BaseModel):
    valid: bool
    message: Optional[str] = None
