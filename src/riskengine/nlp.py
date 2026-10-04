"""Core NLP analysis: text -> (sentiment, event type, impact, entities)."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

from .lexicon import (
    EMOJI, EVENT_RULES, EVENT_SEVERITY, INTENSIFIERS, LEXICON, NEGATIONS, SEVERITY_BOOSTERS,
)

# Mock-index universe (15 large caps from the S&P 100) with aliases for entity linking.
UNIVERSE = {
    "AAPL": ["iphone", "tim cook", "apple inc"],
    "MSFT": ["microsoft", "azure"],
    "AMZN": ["amazon", "aws"],
    "GOOGL": ["alphabet", "google", "youtube", "waymo"],
    "META": ["meta platforms", "facebook", "instagram", "zuckerberg"],
    "NVDA": ["nvidia", "jensen huang"],
    "TSLA": ["tesla", "elon musk", "cybertruck"],
    "JPM": ["jpmorgan", "jp morgan", "jamie dimon"],
    "BAC": ["bank of america"],
    "GS": ["goldman sachs", "goldman"],
    "XOM": ["exxon", "exxonmobil"],
    "CVX": ["chevron"],
    "JNJ": ["johnson & johnson", "johnson and johnson", "j&j"],
    "PFE": ["pfizer"],
    "WMT": ["walmart"],
}

# Ambiguous aliases that must be case-sensitive to avoid false positives.
# Limitation: a sentence starting with "Apple" the fruit will still false-positive.
CS_ALIASES = {
    "AAPL": ["Apple"],
    "META": ["Meta"],
}

_ALIAS_PATTERNS = {
    t: re.compile(r"\b(?:" + "|".join(re.escape(a) for a in al) + r")\b", re.I)
    for t, al in UNIVERSE.items()
}
_CS_PATTERNS = {
    t: re.compile(r"\b(?:" + "|".join(re.escape(a) for a in al) + r")\b")
    for t, al in CS_ALIASES.items()
}
_TICKER_PATTERNS = {t: re.compile(rf"(?:\$|\b){t}\b") for t in UNIVERSE}
_TOKEN = re.compile(r"[a-z][a-z'\-&]*|\d+(?:\.\d+)?%?", re.I)


@dataclass
class Analysis:
    sentiment: float
    sentiment_label: str
    event_type: str
    event_confidence: float
    impact: float
    tickers: list = field(default_factory=list)
    matched_terms: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def extract_tickers(text: str) -> list[str]:
    found = []
    for t in UNIVERSE:
        if _TICKER_PATTERNS[t].search(text) or _ALIAS_PATTERNS[t].search(text) or (t in _CS_PATTERNS and _CS_PATTERNS[t].search(text)):
            found.append(t)
    return found


def score_sentiment(text: str) -> tuple[float, list[str]]:
    """Lexicon score with negation + intensifier handling, squashed to [-1, 1]."""
    tokens = [m.group(0).lower() for m in _TOKEN.finditer(text)]
    total, hits = 0.0, []
    for i, tok in enumerate(tokens):
        base = LEXICON.get(tok)
        if base is None:
            continue
        mult = 1.0
        window = tokens[max(0, i - 3): i]
        for w in window:
            if w in INTENSIFIERS:
                mult *= INTENSIFIERS[w]
        if any(w in NEGATIONS or w.endswith("n't") for w in window):
            mult *= -0.74
        total += base * mult
        hits.append(tok)
    for emo, val in EMOJI.items():
        n = text.count(emo)
        if n:
            total += val * min(n, 3)
            hits.append(emo)
    # percentage-move heuristics: "down 8%" / "up 5%"
    for m in re.finditer(r"\b(down|up|falls?|drops?|jumps?|rises?)\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%", text, re.I):
        sign = 1 if m.group(1).lower() in ("up", "jumps", "jump", "rises", "rise") else -1
        total += sign * min(float(m.group(2)) / 4, 2.5)
    # VADER-style normalisation keeps the score in (-1, 1)
    score = total / math.sqrt(total * total + 8.0) if total else 0.0
    return round(score, 3), hits


def label_sentiment(s: float) -> str:
    return "positive" if s >= 0.15 else "negative" if s <= -0.15 else "neutral"


def classify_event(text: str) -> tuple[str, float]:
    lowered = text.lower()
    scores = {}
    for event, rules in EVENT_RULES.items():
        scores[event] = sum(w for pat, w in rules if re.search(pat, lowered))
    best, top = max(scores.items(), key=lambda kv: kv[1])
    if top < 2.0:
        return "Other", 0.3
    total = sum(scores.values())
    return best, round(top / total, 2)


def estimate_impact(event_type: str, sentiment: float, text: str,
                    source_type: str = "news", engagement: int = 0) -> float:
    """Predicted market-impact severity on a 1-10 scale."""
    base = EVENT_SEVERITY.get(event_type, 2.0)
    magnitude = 0.6 + 0.4 * min(1.0, abs(sentiment) * 1.5)
    lowered = text.lower()
    boost = min(2.5, sum(w for k, w in SEVERITY_BOOSTERS.items() if k in lowered))
    # Positive events rarely carry tail-risk, so damp the catastrophic-language boost.
    if sentiment > 0:
        boost *= 0.3
    impact = base * magnitude + boost
    # Source credibility: social posts are noisier than wire/news copy.
    if source_type == "social":
        impact *= 0.7
        impact += min(1.0, math.log10(1 + max(engagement, 0)) / 4)
    return round(max(1.0, min(10.0, impact)), 1)


def analyze(text: str, source_type: str = "news", engagement: int = 0) -> Analysis:
    sentiment, hits = score_sentiment(text)
    event, conf = classify_event(text)
    impact = estimate_impact(event, sentiment, text, source_type, engagement)
    return Analysis(
        sentiment=sentiment,
        sentiment_label=label_sentiment(sentiment),
        event_type=event,
        event_confidence=conf,
        impact=impact,
        tickers=extract_tickers(text),
        matched_terms=hits,
    )
