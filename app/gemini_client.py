import logging

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.config import settings
from app.models import ScrapedItem, TopNewsItem

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = """You are a news editor covering ocean and marine oil leaks/spills \
(tankers, pipelines, offshore rigs, ports, coastal waters).

Below is a numbered list of recent news items scraped from RSS feeds. Several items \
may describe the same real-world incident from different outlets.

Task:
1. Ignore any item that is not genuinely about an actual oil leak, oil spill, or oil \
   discharge into or near an ocean, sea, gulf, strait, bay, harbour, or other \
   coastal/marine waters. Discard unrelated items: oil market/price news, tanker \
   military strikes or geopolitics that don't mention an actual leak/spill, and \
   spills that are clearly inland (a city street, a factory, a river, an urban \
   canal) with no marine/coastal connection.
2. Group the remaining items into distinct real-world incidents (same spill/leak \
   event covered by multiple outlets = one group).
3. Pick the 5 groups representing the most significant and most recent distinct \
   incidents. If fewer than 5 distinct genuine incidents exist, return fewer - do not \
   invent items.
4. For each of the 5, write:
   - "title": a clear, concise news headline (your own wording is fine, base it on \
     the source items).
   - "description": a factual summary of 30 to 40 words, plain English, no \
     speculation beyond what the items say.
   - "id": the number of the single best representative source item for that group \
     (the most detailed/informative one), from the numbered list below.

Return ONLY items you are confident are real, distinct ocean oil leak/spill incidents.

Numbered items:
{items_block}
"""


class _ClusterItem(BaseModel):
    id: int
    title: str
    description: str


def _build_items_block(items: list[ScrapedItem]) -> str:
    lines = []
    for idx, item in enumerate(items, start=1):
        published = item.published_at.isoformat() if item.published_at else "unknown"
        lines.append(
            f"{idx}. [{item.source} | published {published}] {item.title} — {item.summary}"
        )
    return "\n".join(lines)


def cluster_and_summarize(items: list[ScrapedItem]) -> list[TopNewsItem]:
    if not items:
        return []

    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = _PROMPT_TEMPLATE.format(items_block=_build_items_block(items))

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[_ClusterItem],
            temperature=0.2,
        ),
    )

    clusters: list[_ClusterItem] = response.parsed or []

    results: list[TopNewsItem] = []
    for cluster in clusters[:5]:
        if not (1 <= cluster.id <= len(items)):
            logger.warning("Gemini returned out-of-range id %d, skipping", cluster.id)
            continue
        source_item = items[cluster.id - 1]
        results.append(
            TopNewsItem(
                title=cluster.title.strip(),
                description=cluster.description.strip(),
                source=source_item.source,
                url=source_item.link,
                published_at=source_item.published_at,
            )
        )
    return results
