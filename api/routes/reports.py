from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import ReportDetailResponse, ReportListResponse, ReportSummary
from api.repositories.reports import get_report_by_id, list_reports


router = APIRouter()


@router.get("/reports", response_model=ReportListResponse)
def get_reports(db: Session = Depends(get_db)):
    rows = list_reports(db)

    return ReportListResponse(
        reports=[
            ReportSummary(
                report_id=row.id,
                filename=f"{row.id}.md",
                created_at=row.created_at,
            )
            for row in rows
        ]
    )


@router.get("/reports/{report_id}", response_model=ReportDetailResponse)
def get_report(report_id: str, db: Session = Depends(get_db)):
    row = get_report_by_id(db, report_id)

    if row is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    return ReportDetailResponse(
        report_id=row.id,
        filename=f"{row.id}.md",
        content=row.report_md,
        created_at=row.created_at,
    )