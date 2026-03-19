from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_type: Mapped[str] = mapped_column(String(100), index=True)
    dispatch_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    address: Mapped[str] = mapped_column(String(255), index=True)
    longitude: Mapped[float] = mapped_column(Float)
    latitude: Mapped[float] = mapped_column(Float)
    handling_duration_min: Mapped[int] = mapped_column(Integer)
    police_unit_count: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="closed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DispatchAssignment(Base):
    __tablename__ = "dispatch_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_id: Mapped[int] = mapped_column(Integer, index=True)
    officer_id: Mapped[str] = mapped_column(String(50), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_by: Mapped[str] = mapped_column(String(50), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
