from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.incident import DispatchAssignment, Incident
from app.schemas.collaboration import (
    AssignmentCreate,
    AssignmentCreateResult,
    AssignmentRead,
    ConflictItem,
)

router = APIRouter()


def _find_time_conflicts(db: Session, officer_id: str, start_time, end_time):
    return (
        db.query(DispatchAssignment)
        .filter(
            DispatchAssignment.officer_id == officer_id,
            DispatchAssignment.status == "active",
            or_(
                and_(DispatchAssignment.start_time <= start_time, DispatchAssignment.end_time > start_time),
                and_(DispatchAssignment.start_time < end_time, DispatchAssignment.end_time >= end_time),
                and_(DispatchAssignment.start_time >= start_time, DispatchAssignment.end_time <= end_time),
            ),
        )
        .all()
    )


@router.post("/assignments", response_model=AssignmentCreateResult)
def create_assignment(payload: AssignmentCreate, db: Session = Depends(get_db)):
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail="end_time must be later than start_time")

    incident = db.query(Incident).filter(Incident.id == payload.incident_id).first()
    if incident is None:
        raise HTTPException(status_code=404, detail="incident not found")

    conflicts = _find_time_conflicts(db, payload.officer_id, payload.start_time, payload.end_time)
    if conflicts:
        return AssignmentCreateResult(
            accepted=False,
            message="Conflict detected: officer already has an active assignment in this time window.",
            conflicts=[
                ConflictItem(
                    assignment_id=x.id,
                    incident_id=x.incident_id,
                    officer_id=x.officer_id,
                    start_time=x.start_time,
                    end_time=x.end_time,
                )
                for x in conflicts
            ],
            assignment=None,
        )

    item = DispatchAssignment(
        incident_id=payload.incident_id,
        officer_id=payload.officer_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status="active",
        created_by=payload.created_by,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return AssignmentCreateResult(
        accepted=True,
        message="Assignment created successfully.",
        assignment=AssignmentRead(
            id=item.id,
            incident_id=item.incident_id,
            officer_id=item.officer_id,
            start_time=item.start_time,
            end_time=item.end_time,
            status=item.status,
            created_by=item.created_by,
        ),
    )


@router.get("/assignments", response_model=list[AssignmentRead])
def list_assignments(db: Session = Depends(get_db)):
    rows = db.query(DispatchAssignment).order_by(DispatchAssignment.start_time.desc()).limit(200).all()
    return [
        AssignmentRead(
            id=x.id,
            incident_id=x.incident_id,
            officer_id=x.officer_id,
            start_time=x.start_time,
            end_time=x.end_time,
            status=x.status,
            created_by=x.created_by,
        )
        for x in rows
    ]
