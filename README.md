# Live Ocean Oil Leak News Feed API

Scrapes trusted RSS sources for ocean oil leak / oil spill news, filters for
relevance and recency, deduplicates near-identical coverage, and uses a cheap
Gemini model to cluster the remaining stories into the 5 most significant,
most recent distinct incidents - each with a short editor-style description.

Results are cached in memory for `CACHE_TTL_SECONDS` (default 1 hour) so the
Gemini API isn't called on every request.

## Endpoint

`GET /api/oil-leaks/top`

```json
{
  "generated_at": "2026-09-09T12:00:00+00:00",
  "cached": true,
  "count": 5,
  "items": [
    {
      "title": "Tanker collision spills crude off the coast of ...",
      "description": "A 30-40 word factual summary of the incident.",
      "source": "gCaptain",
      "url": "https://...",
      "published_at": "2026-09-09T08:00:00+00:00"
    }
  ]
}
```

`GET /health` - simple health check for Render.

## Local setup

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your `GEMINI_API_KEY`:

```bash
cp .env.example .env
```

Run it:

```bash
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/api/oil-leaks/top

## Deploying on Render

1. Push this repo to GitHub (already done if you got this via the initial setup).
2. In the Render dashboard: **New > Web Service**, connect this GitHub repo.
   Render will detect `render.yaml` automatically (or set Build Command
   `pip install -r requirements.txt` and Start Command
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT` manually).
3. Add the environment variable `GEMINI_API_KEY` with your key in the Render
   dashboard (Environment tab) - it's intentionally not committed to the repo.
4. Deploy. Your endpoint will be at
   `https://<your-service-name>.onrender.com/api/oil-leaks/top`.

## Configuration (env vars)

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Your Gemini API key |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` | Cheap Gemini model used for clustering/summarizing |
| `CACHE_TTL_SECONDS` | `3600` | How long results are cached before re-scraping/re-summarizing |
| `LOOKBACK_HOURS` | `168` | How far back an article can be published and still be considered "live" |

## Adjusting sources

Edit [`app/sources.py`](app/sources.py) - each entry is
`(name, rss_url, is_general)`. `is_general=True` sources (e.g. Al Jazeera,
Google News queries) need a water/maritime keyword match in addition to the
oil+leak keywords, since they aren't maritime-specific outlets. If a feed
ever goes dead, replace its URL there; nothing else needs to change.
