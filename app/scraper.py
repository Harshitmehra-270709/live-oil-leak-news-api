import logging
import re
from calendar import timegm
from datetime import datetime, timezone

import feedparser
import requests

from app.config import settings
from app.models import ScrapedItem
from app.sources import SOURCES

logger = logging.getLogger(__name__)

_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _clean_text(raw: str) -> str:
    no_tags = _TAG_RE.sub(" ", raw or "")
    return _WHITESPACE_RE.sub(" ", no_tags).strip()


def _parsed_time_to_utc(struct_time) -> datetime | None:
    if not struct_time:
        return None
    return datetime.fromtimestamp(timegm(struct_time), tz=timezone.utc)


def fetch_source(name: str, url: str) -> list[ScrapedItem]:
    """Fetch and parse one RSS feed. Never raises - logs and returns [] on failure."""
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": settings.user_agent},
            timeout=settings.fetch_timeout_seconds,
        )
        resp.raise_for_status()
        parsed = feedparser.parse(resp.content)
    except Exception as exc:
        logger.warning("Failed to fetch source %r (%s): %s", name, url, exc)
        return []

    if parsed.bozo and not parsed.entries:
        logger.warning("Source %r returned unparsable feed: %s", name, parsed.get("bozo_exception"))
        return []

    items = []
    for entry in parsed.entries:
        published = _parsed_time_to_utc(getattr(entry, "published_parsed", None)) or _parsed_time_to_utc(
            getattr(entry, "updated_parsed", None)
        )
        items.append(
            ScrapedItem(
                title=_clean_text(getattr(entry, "title", "")),
                summary=_clean_text(getattr(entry, "summary", ""))[:500],
                link=getattr(entry, "link", "").strip(),
                source=name,
                published_at=published,
            )
        )
    return items


def fetch_all_sources() -> list[ScrapedItem]:
    all_items: list[ScrapedItem] = []
    for name, url, _is_general in SOURCES:
        items = fetch_source(name, url)
        logger.info("Fetched %d item(s) from %r", len(items), name)
        all_items.extend(items)
    return all_items
