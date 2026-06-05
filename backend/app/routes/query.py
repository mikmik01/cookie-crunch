import logging
import traceback


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.db import get_db
from backend.app.models.models import QueryRequest, QueryResponse

router = APIRouter()

logger = logging.getLogger("uvicorn.error")


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
            raise RuntimeError("Pipeline completed without a report.")

        return QueryResponse(
            report_id=final_result["report_id"],
            query=final_result["query"],
            plan=final_result["plan"],
            recommendations=final_result["recommendations"],
            role_summary=final_result["role_summary"],
            generated_at=final_result["generated_at"],
        )

    except Exception as exc:
        db.rollback()

        traceback.print_exc()

        logger.exception("Query route failed")

        raise HTTPException(
            status_code=500,
            detail="Query failed. Check backend console.",
        )