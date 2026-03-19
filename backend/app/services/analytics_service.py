from collections import defaultdict
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.incident import Incident


def get_overview(db: Session) -> dict:
    total, avg_duration, avg_units = db.query(
        func.count(Incident.id),
        func.avg(Incident.handling_duration_min),
        func.avg(Incident.police_unit_count),
    ).one()
    return {
        "total_incidents": int(total or 0),
        "avg_duration_min": round(float(avg_duration or 0), 2),
        "avg_police_unit_count": round(float(avg_units or 0), 2),
    }


def get_type_distribution(db: Session, top_n: int = 10) -> list[dict]:
    rows = (
        db.query(Incident.incident_type, func.count(Incident.id).label("count"))
        .group_by(Incident.incident_type)
        .order_by(func.count(Incident.id).desc())
        .limit(top_n)
        .all()
    )
    return [{"incident_type": r[0], "count": int(r[1])} for r in rows]


def get_hour_distribution(db: Session) -> list[dict]:
    rows = db.query(Incident.dispatch_time).all()
    bucket = defaultdict(int)
    for (dispatch_time,) in rows:
        bucket[dispatch_time.hour] += 1
    return [{"hour": hour, "count": bucket.get(hour, 0)} for hour in range(24)]


def get_daily_trend(db: Session) -> list[dict]:
    rows = db.query(Incident.dispatch_time).all()
    bucket = defaultdict(int)
    for (dispatch_time,) in rows:
        day = dispatch_time.date().isoformat()
        bucket[day] += 1
    sorted_days = sorted(bucket.items(), key=lambda x: datetime.fromisoformat(x[0]))
    return [{"date": d, "count": c} for d, c in sorted_days]


def get_heat_points(db: Session, max_points: int = 2000) -> list[dict]:
    rows = (
        db.query(Incident.longitude, Incident.latitude, Incident.id)
        .order_by(Incident.dispatch_time.desc())
        .limit(max_points)
        .all()
    )
    return [{"longitude": float(r[0]), "latitude": float(r[1]), "weight": 1} for r in rows]
