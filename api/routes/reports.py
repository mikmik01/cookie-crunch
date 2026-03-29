from fastapi import APIRouter, HTTPException
from datetime import datetime

from api.models import ReportListResponse, ReportDetailResponse, ReportSummary

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import REPORT_DIR
 
router = APIRouter()


def report_summary(path) -> ReportSummary:
    stat = path.stat()
    return ReportSummary(
        report_id=path.stem,
        filename=path.name,
        created_at=datetime.fromtimestamp(stat.st_mtime),
    )


@router.get("/reports")
def list_reports():
    if not REPORT_DIR.exists():
        return ReportListResponse(reports=[])
    
    paths = sorted(
        REPORT_DIR.glob("report_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    return ReportListResponse(reports=[report_summary(p) for p in paths])


@router.get("/reports/{report_id}")
def get_report(report_id: str):
    if "/" in report_id or "\\" in report_id or ".." in report_id:
        return HTTPException(status_code=400, detail="Invalid report ID")

    path = REPORT_DIR / f"{report_id}.md"
 
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Report '{report_id}' not found.",
        )
 
    stat = path.stat()
    content = path.read_text(encoding="utf-8")
 
    return ReportDetailResponse(
        report_id=report_id,
        filename=path.name,
        created_at=datetime.fromtimestamp(stat.st_mtime),
        content=content,
    )