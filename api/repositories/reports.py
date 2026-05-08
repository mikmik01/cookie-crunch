import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from api.models_db import QueryReport


def _parse_created_at(value) -> datetime:
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    return datetime.now(timezone.utc)


def save_query_report(db: Session, result: dict) -> QueryReport:
    report = QueryReport(
        id=result["report_id"],
        query=result["query"],
        plan_json=json.dumps(result.get("plan", {}), ensure_ascii=False),
        analyst_output_json=json.dumps(result.get("analyst_output", {}), ensure_ascii=False),
        report_md=result.get("report_md"),
        hero_count=int(result.get("hero_count", 0)),
        issue_count=int(result.get("issue_count", 0)),
        created_at=_parse_created_at(result.get("generated_at")),
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def get_report_by_id(db: Session, report_id: str) -> QueryReport | None:
    return db.get(QueryReport, report_id)


def list_reports(db: Session, limit: int = 20) -> list[QueryReport]:
    return (
        db.query(QueryReport)
        .order_by(QueryReport.created_at.desc())
        .limit(limit)
        .all()
    )