from fastapi import APIRouter, HTTPException

from backend.app.services.agent import answer_query

router = APIRouter()

@router.post("/query")
def query_agent(request: str):
    try:
        return answer_query(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e