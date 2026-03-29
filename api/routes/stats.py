from fastapi import APIRouter, HTTPException, Query
from typing import Optional

import json
 
from api.models import StatsResponse, HeroStat
from api.pipeline import load_latest_stats
 
router = APIRouter()
 
FIELDS = {"win_rate", "ban_rate", "pick_rate", "rank"}


def make_event(
    step: str,
    message: str,
    done: bool = False,
    error: str = None,
    data: dict = None,
) -> str:
    payload = {"step": step, "message": message, "done": done}
    if error:
        payload["error"] = error
    if data:
        payload["data"] = data
    return f"data: {json.dumps(payload)}\n\n"


@router.get("/stats/latest")
def get_latest_stats(
    lane: Optional[str] = Query(
        default=None,
        description="Filter by lane. One of: Mid, Gold, Exp, Jungle, Roam.",
        examples=["Mid", "Gold", "Jungle"],
    ),
    sort_by: Optional[str] = Query(
        default=None,
        description=f"Sort by field. Allowed: {', '.join(sorted(FIELDS))}.",
    ),
    order: str = Query(
        default="desc",
        description="Sort order: 'asc' or 'desc'.",
        pattern="^(asc|desc)$",
    ),
    top_n: Optional[int] = Query(
        default=None,
        ge=1,
        le=200,
        description="Limit results to top N heroes after sorting.",
    ),
):
    data = load_latest_stats()

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="No stats available"
        )
    
    heroes = data["heroes"]

    if lane:
        heroes = [h for h in heroes if (h.get("lane") or "").lower() == lane.lower()]

    if sort_by:
        if sort_by not in FIELDS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort_by '{sort_by}'. Allowed: {', '.join(sorted(FIELDS))}.",
            )
        reverse = order == "desc"
        heroes = sorted(
            heroes,
            key=lambda h: (h.get(sort_by) is None, h.get(sort_by)),
            reverse=reverse,
        )
    
    if top_n:
        heroes = heroes[:top_n]
 
    return StatsResponse(
        date=data["date"],
        hero_count=len(heroes),
        issue_count=data["issue_count"],
        heroes=[HeroStat(**h) for h in heroes],
    )