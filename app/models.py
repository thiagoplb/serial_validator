from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime
from typing import Optional
from uuid import uuid4
from datetime import datetime, timezone
from app.database import Base


class Serial(Base):
    __tablename__ = "serials"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    serial_key: Mapped[str] = mapped_column(String, unique=True)
    fingerprint: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pre_bound_fingerprint: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
