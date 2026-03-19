from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IncidentBase(BaseModel):
    incident_type: str = Field(..., max_length=100)
    dispatch_time: datetime
    address: str = Field(..., max_length=255)
    longitude: float
    latitude: float
    handling_duration_min: int = Field(..., ge=0)
    police_unit_count: int = Field(..., ge=1)
    status: str = Field(default="closed", max_length=50)


class IncidentCreate(IncidentBase):
    pass


class IncidentRead(IncidentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
