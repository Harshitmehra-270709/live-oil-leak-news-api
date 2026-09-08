import asyncio
import logging
from datetime import datetime, timezone

from app.config import settings
from app.filters import filter_and_dedupe
from app.gemini_client import cluster_and_summarize
from app.models import TopNewsItem
from app.scraper import fetch_all_sources

logger = logging.getLogger(__name__)

_lock = asyncio.Lock()
_cached_items: list[TopNewsItem] = []
_cached_at: datetime | None = None


def _run_pipeline() -> list[TopNewsItem]:
    raw_items = fetch_all_sources()
    relevant_items = filter_and_dedupe(raw_items)
    logger.info("Sending %d relevant item(s) to Gemini", len(relevant_items))
    return cluster_and_summarize(relevant_items)


def _is_stale() -> bool:
    if _cached_at is None:
        return True
    age = (datetime.now(timezone.utc) - _cached_at).total_seconds()
    return age >= settings.cache_ttl_seconds


async def get_top_news() -> tuple[list[TopNewsItem], datetime, bool]:
    """Returns (items, generated_at, served_from_cache). Refreshes when stale,
    falling back to the last good cache on refresh failure."""
    global _cached_items, _cached_at

    if not _is_stale():
        return _cached_items, _cached_at, True

    async with _lock:
        if not _is_stale():
            return _cached_items, _cached_at, True

        try:
            fresh_items = await asyncio.to_thread(_run_pipeline)
            if fresh_items:
                _cached_items = fresh_items
                _cached_at = datetime.now(timezone.utc)
                return _cached_items, _cached_at, False
            logger.warning("Pipeline returned no items this refresh; keeping previous cache")
        except Exception:
            logger.exception("Pipeline refresh failed; keeping previous cache")

        if _cached_at is not None:
            return _cached_items, _cached_at, True

        return [], datetime.now(timezone.utc), False
