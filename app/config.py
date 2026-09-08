import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    gemini_api_key: str = os.environ.get("GEMINI_API_KEY", "")
    gemini_model: str = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    cache_ttl_seconds: int = int(os.environ.get("CACHE_TTL_SECONDS", "3600"))
    lookback_hours: int = int(os.environ.get("LOOKBACK_HOURS", "168"))
    fetch_timeout_seconds: int = int(os.environ.get("FETCH_TIMEOUT_SECONDS", "10"))
    max_items_to_gemini: int = int(os.environ.get("MAX_ITEMS_TO_GEMINI", "90"))
    user_agent: str = os.environ.get(
        "SCRAPER_USER_AGENT",
        "Mozilla/5.0 (compatible; OceanOilLeakNewsBot/1.0; "
        "+https://github.com/Harshitmehra-270709)",
    )


settings = Settings()
