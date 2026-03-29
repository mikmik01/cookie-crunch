from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import query, reports, stats

app = FastAPI()

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