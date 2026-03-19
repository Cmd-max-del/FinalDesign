from datetime import datetime, timedelta
import random

from app.db.session import SessionLocal
from app.models.incident import Incident


INCIDENT_TYPES = [
    "Theft",
    "Traffic Accident",
    "Dispute",
    "Fraud",
    "Public Order",
    "Fire Alarm",
    "Emergency Help",
]

ADDRESSES = [
    "Xuancheng Road A",
    "Nanmen Street B",
    "Jingting Avenue C",
    "Industrial Park D",
    "Railway Station E",
    "Hospital F",
    "School G",
]


def run(count: int = 500):
    db = SessionLocal()
    base = datetime(2025, 1, 1, 0, 0, 0)

    for _ in range(count):
        dt = base + timedelta(hours=random.randint(0, 24 * 400))
        incident = Incident(
            incident_type=random.choice(INCIDENT_TYPES),
            dispatch_time=dt,
            address=random.choice(ADDRESSES),
            longitude=118.74 + random.uniform(-0.08, 0.08),
            latitude=30.95 + random.uniform(-0.08, 0.08),
            handling_duration_min=random.randint(8, 180),
            police_unit_count=random.randint(1, 5),
            status=random.choice(["closed", "closed", "closed", "processing"]),
        )
        db.add(incident)

    db.commit()
    db.close()


if __name__ == "__main__":
    run()
    print("Sample data inserted.")
