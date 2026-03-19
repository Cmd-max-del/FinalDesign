from pydantic import BaseModel


class TypeCountItem(BaseModel):
    incident_type: str
    count: int


class HourDistributionItem(BaseModel):
    hour: int
    count: int


class DailyTrendItem(BaseModel):
    date: str
    count: int


class HeatPointItem(BaseModel):
    longitude: float
    latitude: float
    weight: int


class OverviewStats(BaseModel):
    total_incidents: int
    avg_duration_min: float
    avg_police_unit_count: float
