from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ScrapedItem(BaseModel):
    title: str
    summary: str
    link: str
    source: str
    published_at: Optional[datetime] = None


class TopNewsItem(BaseModel):
    title: str
    description: str
    source: str
    url: str
    published_at: Optional[datetime] = None


class TopNewsResponse(BaseModel):
    generated_at: datetime
    cached: bool
    count: int
    items: list[TopNewsItem]
