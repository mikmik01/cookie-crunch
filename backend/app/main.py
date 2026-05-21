from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from backend.app.routes import query, reports, stats
from backend.app.db.db import SessionLocal
from backend.app.db.db_migrations import run_migrations
from backend.app.services.pipeline import ensure_today_stats


def seed_stats_on_startup() -> None:
    db = SessionLocal()
    try:
        ensure_today_stats(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    await run_in_threadpool(seed_stats_on_startup)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, tags=["Query"])
app.include_router(stats.router, tags=["Stats"])
app.include_router(reports.router, tags=["Reports"])


@app.get("/health")
def health():
    return {"status": "ok"}