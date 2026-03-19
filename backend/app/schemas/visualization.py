from pydantic import BaseModel


class NameCountItem(BaseModel):
    name: str
    count: int


class HourCountItem(BaseModel):
    hour: int
    count: int


class TrendItem(BaseModel):
    date: str
    count: int


class DashboardOverview(BaseModel):
    total: int
    date_start: str | None
    date_end: str | None


class DashboardResponse(BaseModel):
    overview: DashboardOverview
    by_category: list[NameCountItem]
    by_type: list[NameCountItem]
    by_branch: list[NameCountItem]
    by_risk: list[NameCountItem]
    by_hour: list[HourCountItem]
    trend_daily: list[TrendItem]


class DetailItem(BaseModel):
    event_id: str
    alarm_time: str | None
    branch: str
    unit: str
    category: str
    incident_type: str
    risk_level: str
    address: str
    result: str


class DetailResponse(BaseModel):
    total: int
    page: int
    page_size: int
    records: list[DetailItem]
