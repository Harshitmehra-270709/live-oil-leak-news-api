import re
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

from app.config import settings
from app.models import ScrapedItem
from app.sources import SOURCES

_GENERAL_SOURCES = {name for name, _url, is_general in SOURCES if is_general}

_OIL_TERMS = re.compile(
    r"\b(oil|crude|petroleum|diesel|bunker fuel|fuel oil)\b", re.IGNORECASE
)
# A "strong" term (spill/leak/slick/...) is, combined with an oil term, good
# evidence of an actual spill/leak event on its own - local reporting often
# names a specific place (an estuary, a harbour) rather than saying
# "ocean"/"sea" outright, so these don't need a water-term match too.
_STRONG_LEAK_TERMS = re.compile(
    r"\b(spill(ed|ing)?|leak(ed|ing|age)?|slick|discharge(d)?|seep(ed|ing|age)?|"
    r"gusher|rupture(d)?)\b",
    re.IGNORECASE,
)
# A "weak" term describes an incident that only sometimes involves an oil
# release (a collision, a grounding...) - these need a water-term match too
# when the source isn't inherently maritime, to cut down on noise.
_WEAK_LEAK_TERMS = re.compile(
    r"\b(collision|collide(d|s)?|(run|ran)\s+aground|aground|grounding|"
    r"capsiz(e|ed|ing)|sink(ing)?|sank|sunk|explosion|explod(e|ed|ing)|"
    r"contaminat(e|ed|ing|ion)|disaster)\b",
    re.IGNORECASE,
)
_WATER_TERMS = re.compile(
    r"\b(ocean|sea|coast(al|line)?|offshore|gulf|strait|marine|tanker|vessel|"
    r"ship|port|harbo(u)?r|bay|reef|beach|waterway|river mouth)\b",
    re.IGNORECASE,
)


def _is_relevant(item: ScrapedItem) -> bool:
    text = f"{item.title} {item.summary}"
    if not _OIL_TERMS.search(text):
        return False

    if _STRONG_LEAK_TERMS.search(text):
        return True

    if _WEAK_LEAK_TERMS.search(text):
        if item.source in _GENERAL_SOURCES:
            return bool(_WATER_TERMS.search(text))
        return True

    return False


def _is_recent(item: ScrapedItem, cutoff: datetime) -> bool:
    if item.published_at is None:
        return True
    return item.published_at >= cutoff


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip()


def _dedupe(items: list[ScrapedItem]) -> list[ScrapedItem]:
    kept: list[ScrapedItem] = []
    kept_norms: list[str] = []
    for item in items:
        norm = _normalize_title(item.title)
        is_dup = any(SequenceMatcher(None, norm, existing).ratio() > 0.72 for existing in kept_norms)
        if not is_dup:
            kept.append(item)
            kept_norms.append(norm)
    return kept


def filter_and_dedupe(items: list[ScrapedItem]) -> list[ScrapedItem]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.lookback_hours)

    relevant = [item for item in items if item.title and _is_relevant(item) and _is_recent(item, cutoff)]

    relevant.sort(key=lambda i: i.published_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    deduped = _dedupe(relevant)

    return deduped[: settings.max_items_to_gemini]
