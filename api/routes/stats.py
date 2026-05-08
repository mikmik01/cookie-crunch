from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import HeroStat, StatsResponse
from api.repositories.stats import get_latest_stats
 
router = APIRouter()
 
FIELDS = {"win_rate", "ban_rate", "pick_rate", "rank"}


def filter_by_lane(heroes: list[dict], lane: Optional[str]) -> list[dict]:
    if not lane:
        return heroes

    return [
        hero
        for hero in heroes
        if (hero.get("lane") or "").lower() == lane.lower()
    ]


def sort_heroes(heroes: list[dict], sort_by: Optional[str], order: str) -> list[dict]:
    if not sort_by:
        return heroes

    if sort_by not in FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by '{sort_by}'. Allowed: {', '.join(sorted(FIELDS))}.",
        )

    heroes_with_value = [hero for hero in heroes if hero.get(sort_by) is not None]
    heroes_without_value = [hero for hero in heroes if hero.get(sort_by) is None]

    heroes_with_value = sorted(
        heroes_with_value,
        key=lambda hero: hero[sort_by],
        reverse=order == "desc",
    )

    return heroes_with_value + heroes_without_value


def build_stats_response(data: dict, heroes: list[dict]) -> StatsResponse:
    return StatsResponse(
        date=data["date"],
        hero_count=len(heroes),
        issue_count=data["issue_count"],
        heroes=[HeroStat(**hero) for hero in heroes],
    )


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    data = get_latest_stats(db)

    if data is None:
        raise HTTPException(status_code=404, detail="No stats found.")

    return build_stats_response(data, data["heroes"])


@router.get("/stats/latest", response_model=StatsResponse)
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
    db: Session = Depends(get_db),
):
    data = get_latest_stats(db)

    if data is None:
        raise HTTPException(status_code=404, detail="No stats found.")

    heroes = data["heroes"]
    heroes = filter_by_lane(heroes, lane)
    heroes = sort_heroes(heroes, sort_by, order)

    if top_n:
        heroes = heroes[:top_n]

    return build_stats_response(data, heroes)