from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.db import get_db
from backend.app.models.models import QueryRequest, QueryResponse
from backend.app.db.repositories.reports import save_query_report

router = APIRouter()


def execute_pipeline(user_query: str, db: Session):
    from backend.app.services.pipeline import run_pipeline

    return run_pipeline(user_query, db=db)


@router.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        final_result = None

        for step, message, result in execute_pipeline(request.query, db):
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