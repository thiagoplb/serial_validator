import secrets
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.config import ADMIN_API_KEY
from app.database import get_db
from app.models import Serial
from app.schemas import SerialCreate, SerialResponse

router = APIRouter(prefix="/admin")


def verify_admin_key(x_admin_key: str = Header(...)):
    if x_admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")


@router.post("/serials", response_model=SerialResponse, status_code=201, dependencies=[Depends(verify_admin_key)])
def create_serial(body: SerialCreate, db: Session = Depends(get_db)):
    serial = Serial(
        serial_key=body.serial_key or secrets.token_urlsafe(16),
        pre_bound_fingerprint=body.pre_bound_fingerprint,
        expires_at=body.expires_at,
    )
    db.add(serial)
    db.commit()
    db.refresh(serial)
    return serial


@router.get("/serials", response_model=List[SerialResponse], dependencies=[Depends(verify_admin_key)])
def list_serials(db: Session = Depends(get_db)):
    return db.query(Serial).all()


@router.get("/serials/{serial_id}", response_model=SerialResponse, dependencies=[Depends(verify_admin_key)])
def get_serial(serial_id: str, db: Session = Depends(get_db)):
    serial = db.query(Serial).filter(Serial.id == serial_id).first()
    if not serial:
        raise HTTPException(status_code=404, detail="Serial not found")
    return serial


@router.patch("/serials/{serial_id}/revoke", response_model=SerialResponse, dependencies=[Depends(verify_admin_key)])
def revoke_serial(serial_id: str, db: Session = Depends(get_db)):
    serial = db.query(Serial).filter(Serial.id == serial_id).first()
    if not serial:
        raise HTTPException(status_code=404, detail="Serial not found")
    serial.is_active = False
    db.commit()
    db.refresh(serial)
    return serial
