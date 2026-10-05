"""Data ingestion: multiple sources -> a common `RawItem` stream.

Sources
  * news   : RSS feeds (Google News / Yahoo Finance) or a local JSONL file
  * social : Reddit JSON API (free, no key) or a local JSONL file shaped like
             X/Twitter posts ({"text", "ts", "likes", "retweets"})
Every live source degrades gracefully to its bundled sample file so the demo
never fails because of the network.
"""
from __future__ import annotations

import html
import json
import logging
import re
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable, Iterator

log = logging.getLogger("riskengine.ingest")
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
UA = {"User-Agent": "risk-engine-hackathon/1.0"}


@dataclass
class RawItem:
    id: str
    ts: str            # ISO-8601 UTC
    source: str        # e.g. "reuters-sample", "google-news", "reddit/stocks"
    source_type: str   # "news" | "social"
    text: str
    engagement: int = 0


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def _http_get(url: str, timeout: int = 8) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


class FileSource:
    def __init__(self, path: Path, source_type: str):
        self.path, self.source_type = Path(path), source_type

    def fetch(self) -> Iterator[RawItem]:
        with open(self.path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if not line.strip():
                    continue
                d = json.loads(line)
                yield RawItem(
                    id=d.get("id") or f"{self.path.stem}-{i}",
                    ts=d["ts"],
                    source=d.get("source", self.path.stem),
                    source_type=self.source_type,
                    text=_clean(d["text"]),
                    engagement=int(d.get("likes", 0)) + 2 * int(d.get("retweets", 0)),
                )


class RSSSource:
    """Financial news over RSS (stdlib XML parsing, no feedparser needed)."""
    DEFAULT_FEEDS = {
        "google-news/markets": "https://news.google.com/rss/search?q=stock+market+when:1d&hl=en-US&gl=US&ceid=US:en",
        "yahoo-finance": "https://finance.yahoo.com/news/rssindex",
    }

    def __init__(self, feeds: dict | None = None, limit: int = 40):
        self.feeds, self.limit = feeds or self.DEFAULT_FEEDS, limit

    def fetch(self) -> Iterator[RawItem]:
        for name, url in self.feeds.items():
            root = ET.fromstring(_http_get(url))
            for i, it in enumerate(root.iter("item")):
                if i >= self.limit:
                    break
                title, desc = it.findtext("title", ""), it.findtext("description", "")
                pub = it.findtext("pubDate")
                try:
                    ts = parsedate_to_datetime(pub).astimezone(timezone.utc).isoformat()
                except Exception:
                    ts = datetime.now(timezone.utc).isoformat()
                yield RawItem(
                    id=it.findtext("guid") or f"{name}-{i}", ts=ts, source=name,
                    source_type="news", text=_clean(f"{title}. {desc}"),
                )


class RedditSource:
    """Social posts from finance subreddits (free JSON endpoint; X/Twitter's free
    tier is too restrictive for streaming, so Reddit stands in as 'social')."""

    def __init__(self, subs=("stocks", "wallstreetbets", "investing"), limit: int = 40):
        self.subs, self.limit = subs, limit

    def fetch(self) -> Iterator[RawItem]:
        for sub in self.subs:
            data = json.loads(_http_get(f"https://www.reddit.com/r/{sub}/new.json?limit={self.limit}"))
            for ch in data["data"]["children"]:
                d = ch["data"]
                ts = datetime.fromtimestamp(d["created_utc"], tz=timezone.utc).isoformat()
                yield RawItem(
                    id=d["id"], ts=ts, source=f"reddit/{sub}", source_type="social",
                    text=_clean(f"{d.get('title', '')}. {d.get('selftext', '')[:300]}"),
                    engagement=int(d.get("ups", 0)) + 2 * int(d.get("num_comments", 0)),
                )


def _safe(source, fallback: FileSource) -> tuple[list[RawItem], str]:
    try:
        items = list(source.fetch())
        if items:
            return items, "live"
        log.warning("%s returned nothing; using sample data", type(source).__name__)
    except Exception as e:  # network blocked, rate limited, schema change...
        log.warning("%s failed (%s); using sample data", type(source).__name__, e)
    return list(fallback.fetch()), "sample"


def gather(live: bool = False) -> tuple[list[RawItem], dict[str, str]]:
    """Collect items from >= 2 sources (news + social), sorted by time."""
    news_sample = FileSource(DATA_DIR / "sample_news.jsonl", "news")
    social_sample = FileSource(DATA_DIR / "sample_social.jsonl", "social")
    if live:
        n_items, n_prov = _safe(RSSSource(), news_sample)
        s_items, s_prov = _safe(RedditSource(), social_sample)
        items = n_items + s_items
        prov = {"news": n_prov, "social": s_prov}
    else:
        items = list(news_sample.fetch()) + list(social_sample.fetch())
        prov = {"news": "sample", "social": "sample"}
    return sorted(items, key=lambda x: x.ts), prov
