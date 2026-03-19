from datetime import datetime

from pydantic import BaseModel, Field


class AssignmentCreate(BaseModel):
    incident_id: int
    officer_id: str = Field(..., max_length=50)
    start_time: datetime
    end_time: datetime
    created_by: str = Field(..., max_length=50)


class AssignmentRead(BaseModel):
    id: int
    incident_id: int
    officer_id: str
    start_time: datetime
    end_time: datetime
    status: str
    created_by: str


class ConflictItem(BaseModel):
    assignment_id: int
    incident_id: int
    officer_id: str
    start_time: datetime
    end_time: datetime


class AssignmentCreateResult(BaseModel):
    accepted: bool
    message: str
    conflicts: list[ConflictItem] = []
    assignment: AssignmentRead | None = None
