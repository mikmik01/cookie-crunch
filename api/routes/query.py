from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import QueryRequest, QueryResponse
from api.pipeline import run_pipeline
from api.repositories.reports import save_query_report

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        final_result = None

        for step, message, result in run_pipeline(request.query):
            if step == "done":
                final_result = result

        if final_result is None:
            raise HTTPException(
                status_code=500,
                detail="Pipeline completed without a report.",
            )

        save_query_report(db, final_result)

        return QueryResponse(
            report_id=final_result["report_id"],
            query=final_result["query"],
            plan=final_result["plan"],
            analyst_output=final_result["analyst_output"],
            report_md=final_result["report_md"],
            generated_at=final_result["generated_at"],
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))