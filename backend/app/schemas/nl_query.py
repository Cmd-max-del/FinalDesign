from pydantic import BaseModel


class NLQueryRequest(BaseModel):
    question: str


class NLQueryResponse(BaseModel):
    answer: str
    generated_sql: str | None = None
    source: str = "rule-based"


class NLStatusResponse(BaseModel):
    llm_enabled: bool
    model: str
    base_url_configured: bool
    api_key_configured: bool
