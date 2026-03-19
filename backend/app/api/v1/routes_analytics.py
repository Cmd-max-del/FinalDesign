from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import (
    DailyTrendItem,
    HeatPointItem,
    HourDistributionItem,
    OverviewStats,
    TypeCountItem,
)
from app.services.analytics_service import (
    get_daily_trend,
    get_heat_points,
    get_hour_distribution,
    get_overview,
    get_type_distribution,
)

router = APIRouter()


@router.get("/overview", response_model=OverviewStats)
def overview(db: Session = Depends(get_db)):
    return get_overview(db)


@router.get("/type-distribution", response_model=list[TypeCountItem])
def type_distribution(top_n: int = Query(default=10, ge=1, le=50), db: Session = Depends(get_db)):
    return get_type_distribution(db, top_n=top_n)


@router.get("/hour-distribution", response_model=list[HourDistributionItem])
def hour_distribution(db: Session = Depends(get_db)):
    return get_hour_distribution(db)


@router.get("/daily-trend", response_model=list[DailyTrendItem])
def daily_trend(db: Session = Depends(get_db)):
    return get_daily_trend(db)


@router.get("/heat-points", response_model=list[HeatPointItem])
def heat_points(max_points: int = Query(default=2000, ge=100, le=10000), db: Session = Depends(get_db)):
    return get_heat_points(db, max_points=max_points)
