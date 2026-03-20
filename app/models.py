from sqlalchemy import Boolean, Column, DateTime, String
from uuid import uuid4
from datetime import datetime
from app.database import Base


class Serial(Base):
    __tablename__ = "serials"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    serial_key = Column(String, unique=True, nullable=False)
    fingerprint = Column(String, nullable=True)
    pre_bound_fingerprint = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
