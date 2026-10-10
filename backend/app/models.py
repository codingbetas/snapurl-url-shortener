from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String, nullable=True)