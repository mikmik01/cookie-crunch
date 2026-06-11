import os

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import query, stats
from app.db.db_migrations import run_migrations


def get_allowed_origins() -> list[str]:
    origins = os.getenv("CORS_ALLOW_ORIGINS", "")

    parsed = [
        origin.strip()
        for origin in origins.split(",")
        if origin.strip()
    ]

    return parsed


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield


app = FastAPI(lifespan=lifespan)

allowed_origins = get_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization"],
)


app.include_router(query.router, tags=["Query"])
app.include_router(stats.router, tags=["Stats"])


@app.get("/health")
def health():
    return {"status": "ok"}