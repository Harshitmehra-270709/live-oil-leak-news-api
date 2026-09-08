import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.cache import get_top_news
from app.models import TopNewsResponse

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Live Ocean Oil Leak News Feed API",
    description="Top 5 latest, deduplicated ocean oil leak/spill news items, "
    "clustered and summarized from trusted RSS sources.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/oil-leaks/top", response_model=TopNewsResponse)
async def top_oil_leak_news():
    items, generated_at, cached = await get_top_news()
    if not items:
        raise HTTPException(
            status_code=503,
            detail="No news data available yet. Please retry shortly.",
        )
    return TopNewsResponse(
        generated_at=generated_at,
        cached=cached,
        count=len(items),
        items=items,
    )
