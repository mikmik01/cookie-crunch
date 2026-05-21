from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(
        default="find the strongest heroes"
    )


class KeyFinding(BaseModel):
    claim: str
    evidence: str
    confidence: str


class AnalystOutput(BaseModel):
    headline: str
    key_findings: list[KeyFinding]
    meta_summary: str
    caveats: list[str] = []


class HeroRecommendation(BaseModel):
    hero: str
    lane: str | None = None
    tier: str | None = None
    win_rate: float | None = None
    pick_rate: float | None = None
    ban_rate: float | None = None


class RoleSummary(BaseModel):
    lane: str
    heroes: list[HeroRecommendation]


class QueryResponse(BaseModel):
    report_id: str
    query: str
    plan: dict[str, Any]
    recommendations: list[HeroRecommendation]
    role_summary: list[RoleSummary]
    generated_at: str


class HeroStat(BaseModel):
    rank: Optional[int] = None
    lane: Optional[str] = None
    hero: str
    tier: Optional[str] = None
    win_rate: Optional[float] = None
    ban_rate: Optional[float] = None
    pick_rate: Optional[float] = None
    roles: Optional[str] = None


class StatsResponse(BaseModel):
    date: str
    hero_count: int
    issue_count: int
    heroes: list[HeroStat]


class ReportSummary(BaseModel):
    report_id: str
    filename: str
    created_at: datetime


class ReportListResponse(BaseModel):
    reports: list[ReportSummary]


class ReportDetailResponse(BaseModel):
    report_id: str
    filename: str
    content: str
    created_at: datetime


class ProgressEvent(BaseModel):
    step: str
    message: str
    done: bool = False
    error: Optional[str] = None
    data: Optional[QueryResponse] = None