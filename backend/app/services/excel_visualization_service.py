from pathlib import Path

import pandas as pd

from app.core.config import settings

_REQUIRED_COLUMNS = [
    "序号",
    "事件单编号",
    "报警人",
    "联系电话",
    "报警时间",
    "所属分局",
    "辖区单位",
    "警情类别",
    "警情类型",
    "警情细类",
    "警情明细",
    "处理结果",
    "风险等级",
    "事发地址",
    "事件详情",
]


_cache_df: pd.DataFrame | None = None
_cache_mtime: float | None = None


def _resolve_excel_path() -> Path:
    if settings.source_excel_path:
        return Path(settings.source_excel_path)
    return Path(__file__).resolve().parents[3] / "测试数据.xlsx"


def _load_df() -> pd.DataFrame:
    global _cache_df, _cache_mtime

    excel_path = _resolve_excel_path()
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    mtime = excel_path.stat().st_mtime
    if _cache_df is not None and _cache_mtime == mtime:
        return _cache_df.copy()

    df = pd.read_excel(excel_path, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    missing = [c for c in _REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    df["报警时间"] = pd.to_datetime(df["报警时间"], errors="coerce")
    for col in ["所属分局", "辖区单位", "警情类别", "警情类型", "风险等级", "处理结果", "事发地址", "事件单编号"]:
        df[col] = df[col].fillna("未知").astype(str).str.strip()

    _cache_df = df
    _cache_mtime = mtime
    return df.copy()


def _name_count(df: pd.DataFrame, field: str, top_n: int = 15) -> list[dict]:
    series = df[field].fillna("未知").astype(str).str.strip()
    vc = series.value_counts().head(top_n)
    return [{"name": str(k), "count": int(v)} for k, v in vc.items()]


def get_dashboard_data() -> dict:
    df = _load_df()

    min_time = df["报警时间"].min()
    max_time = df["报警时间"].max()

    by_hour = (
        df.dropna(subset=["报警时间"])
        .assign(hour=df["报警时间"].dt.hour)
        .groupby("hour")
        .size()
        .reindex(range(24), fill_value=0)
    )

    trend = (
        df.dropna(subset=["报警时间"])
        .assign(date=df["报警时间"].dt.date.astype(str))
        .groupby("date")
        .size()
        .reset_index(name="count")
        .sort_values("date")
    )

    return {
        "overview": {
            "total": int(len(df)),
            "date_start": min_time.strftime("%Y-%m-%d %H:%M") if pd.notna(min_time) else None,
            "date_end": max_time.strftime("%Y-%m-%d %H:%M") if pd.notna(max_time) else None,
        },
        "by_category": _name_count(df, "警情类别"),
        "by_type": _name_count(df, "警情类型"),
        "by_branch": _name_count(df, "辖区单位"),
        "by_risk": _name_count(df, "风险等级"),
        "by_hour": [{"hour": int(h), "count": int(c)} for h, c in by_hour.items()],
        "trend_daily": trend.to_dict(orient="records"),
    }


def get_details(field: str | None, value: str | None, page: int, page_size: int, keyword: str | None) -> dict:
    df = _load_df()

    field_map = {
        "警情类别": "警情类别",
        "警情类型": "警情类型",
        "辖区单位": "辖区单位",
        "风险等级": "风险等级",
        "所属分局": "所属分局",
    }

    filtered = df
    if field and value:
        mapped = field_map.get(field)
        if mapped:
            filtered = filtered[filtered[mapped].astype(str) == value]

    if keyword:
        kw = str(keyword).strip()
        if kw:
            mask = (
                filtered["事件详情"].fillna("").astype(str).str.contains(kw, case=False)
                | filtered["警情明细"].fillna("").astype(str).str.contains(kw, case=False)
                | filtered["事发地址"].fillna("").astype(str).str.contains(kw, case=False)
            )
            filtered = filtered[mask]

    total = int(len(filtered))
    start = (page - 1) * page_size
    end = start + page_size
    page_df = filtered.iloc[start:end].copy()

    records = []
    for _, row in page_df.iterrows():
        alarm_time = row["报警时间"]
        records.append(
            {
                "event_id": str(row.get("事件单编号", "")),
                "alarm_time": alarm_time.strftime("%Y-%m-%d %H:%M") if pd.notna(alarm_time) else None,
                "branch": str(row.get("所属分局", "")),
                "unit": str(row.get("辖区单位", "")),
                "category": str(row.get("警情类别", "")),
                "incident_type": str(row.get("警情类型", "")),
                "risk_level": str(row.get("风险等级", "")),
                "address": str(row.get("事发地址", "")),
                "result": str(row.get("处理结果", "")),
            }
        )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "records": records,
    }
