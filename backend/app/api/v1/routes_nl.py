import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.nl_query import NLQueryRequest, NLQueryResponse, NLStatusResponse
from app.services.analytics_service import get_overview, get_type_distribution

router = APIRouter()


def _local_answer(question: str, db: Session) -> NLQueryResponse:
    q = question.lower()
    if "overall" in q or "summary" in q or "total" in q:
        overview = get_overview(db)
        answer = (
            f"Total incidents: {overview['total_incidents']}, average handling duration: "
            f"{overview['avg_duration_min']} minutes, average police units: {overview['avg_police_unit_count']}."
        )
        return NLQueryResponse(answer=answer, source="rule-based")

    if "type" in q or "category" in q:
        top_types = get_type_distribution(db, top_n=5)
        text = ", ".join([f"{x['incident_type']}({x['count']})" for x in top_types])
        return NLQueryResponse(answer=f"Top 5 incident types: {text}.", source="rule-based")

    return NLQueryResponse(
        answer="Please ask about overview, totals, or incident type distribution.",
        source="rule-based",
    )


@router.get("/status", response_model=NLStatusResponse)
def nl_status():
    return NLStatusResponse(
        llm_enabled=bool(settings.openai_api_key and settings.openai_base_url),
        model=settings.openai_model,
        base_url_configured=bool(settings.openai_base_url),
        api_key_configured=bool(settings.openai_api_key),
    )


async def _remote_llm_answer(question: str) -> str | None:
    if not settings.openai_api_key or not settings.openai_base_url:
        return None

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": "You are a police incident analytics assistant."},
            {"role": "user", "content": question},
        ],
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(f"{settings.openai_base_url}/chat/completions", headers=headers, json=payload)
        if resp.status_code >= 400:
            return None
        data = resp.json()
        return data["choices"][0]["message"]["content"]


@router.post("/query", response_model=NLQueryResponse)
async def nl_query(payload: NLQueryRequest, db: Session = Depends(get_db)):
    remote_answer = await _remote_llm_answer(payload.question)
    if remote_answer:
        return NLQueryResponse(answer=remote_answer, source="llm")
    return _local_answer(payload.question, db)
