from datetime import datetime
import csv
from io import StringIO

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentRead

router = APIRouter()


@router.post("", response_model=IncidentRead)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(**payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    return db.query(Incident).order_by(Incident.dispatch_time.desc()).offset(skip).limit(limit).all()


@router.post("/upload-csv")
async def upload_incident_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    filename = file.filename or ""
    if not filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    reader = csv.DictReader(StringIO(content.decode("utf-8")))
    rows = list(reader)

    required_cols = {
        "incident_type",
        "dispatch_time",
        "address",
        "longitude",
        "latitude",
        "handling_duration_min",
        "police_unit_count",
        "status",
    }
    missing = required_cols - set(reader.fieldnames or [])
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {sorted(missing)}")

    created = 0
    for row in rows:
        dispatch_time = datetime.fromisoformat(str(row["dispatch_time"]).replace("Z", "+00:00"))
        incident = Incident(
            incident_type=str(row["incident_type"]),
            dispatch_time=dispatch_time,
            address=str(row["address"]),
            longitude=float(row["longitude"]),
            latitude=float(row["latitude"]),
            handling_duration_min=int(row["handling_duration_min"]),
            police_unit_count=int(row["police_unit_count"]),
            status=str(row["status"]),
        )
        db.add(incident)
        created += 1

    db.commit()
    return {"created": created}
