"""Trusted RSS sources for ocean oil leak / oil spill news.

Each entry is (name, feed_url, is_general). `is_general=True` marks
sources that aren't maritime-specific (e.g. Al Jazeera's firehose, or
a broad Google News query) so the relevance filter can require a
water/maritime keyword in addition to the oil+leak keywords for those.
Maritime trade-press feeds are inherently on-topic, so they only need
the oil+leak match.
"""

SOURCES = [
    ("gCaptain", "https://gcaptain.com/feed/", False),
    ("Marine Insight", "https://www.marineinsight.com/feed", False),
    ("Offshore Energy", "https://www.offshore-energy.biz/feed/", False),
    ("Splash247", "https://splash247.com/feed/", False),
    ("Hellenic Shipping News", "https://www.hellenicshippingnews.com/feed/", False),
    ("Seatrade Maritime News", "https://www.seatrade-maritime.com/rss.xml", False),
    ("OilPrice.com", "https://oilprice.com/rss/main", True),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", True),
    (
        "Google News: oil spill ocean",
        "https://news.google.com/rss/search?q=oil%20spill%20ocean%20when:7d&hl=en-US&gl=US&ceid=US:en",
        True,
    ),
    (
        "Google News: oil leak tanker/pipeline/vessel",
        "https://news.google.com/rss/search?q=%22oil%20leak%22%20tanker%20OR%20pipeline%20OR%20vessel%20when:7d&hl=en-US&gl=US&ceid=US:en",
        True,
    ),
    (
        "Google News: pipeline leak offshore/coast/sea",
        "https://news.google.com/rss/search?q=%22pipeline%20leak%22%20offshore%20OR%20coast%20OR%20sea%20when:7d&hl=en-US&gl=US&ceid=US:en",
        True,
    ),
    (
        "Google News: crude oil spill sea/coast/ocean",
        "https://news.google.com/rss/search?q=%22crude%20oil%22%20spill%20sea%20OR%20coast%20OR%20ocean%20when:7d&hl=en-US&gl=US&ceid=US:en",
        True,
    ),
    (
        "Google News: tanker spill / oil slick",
        "https://news.google.com/rss/search?q=%22tanker%20spill%22%20OR%20%22oil%20slick%22%20when:7d&hl=en-US&gl=US&ceid=US:en",
        True,
    ),
]
