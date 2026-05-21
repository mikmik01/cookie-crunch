from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes import query
from backend.app.db.db_migrations import run_migrations

from contextlib import asynccontextmanager

from backend.app.routes import reports, stats

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
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