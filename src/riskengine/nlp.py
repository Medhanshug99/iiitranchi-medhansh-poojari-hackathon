"""Core NLP analysis: text -> (sentiment, event type, impact, entities)."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

from .lexicon import (
    AVERSION_CONTEXT, CREDIT_DOWNGRADE_CONTEXT, EMOJI, EVENT_RULES, EVENT_SEVERITY,
    INTENSIFIERS, LEXICON, NEGATIONS, NEUTRAL_CUES, NEUTRAL_SHRINK,
    PHRASE_SENTIMENT, SEVERITY_BOOSTERS,
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

# Pre-compile phrase patterns once.
_PHRASE_PATTERNS = {
    phrase: re.compile(r"\b" + re.escape(phrase) + r"\b", re.I)
    for phrase in PHRASE_SENTIMENT
}

# ---------------------------------------------------------------------------
# (a) Inflection normaliser
# ---------------------------------------------------------------------------
# Maps surface forms not already in LEXICON to their canonical form that IS in LEXICON.
# Rules applied in order; first match wins.
# We prefer an explicit table over a live stemmer so every mapping is visible and testable.

_INFL_SUFFIX_RULES = [
    # Order: longest suffix first so "ies" beats "s".
    (r"ies$", "y"),        # "rallies" -> "rally" (already in lexicon, but catches future words)
    (r"ied$", "y"),        # "rallied" -> "rally"
    (r"ing$", ""),         # "surging" -> "surg" (needs double-consonant check below)
    (r"ingly$", ""),       # "warningly" edge case
    (r"ed$", ""),          # "plunged" -> "plung" then re-try with "e" suffix
    (r"es$", ""),          # "plunges" -> "plung"
    (r"s$", ""),           # "losses" -> "loss" (after the above catch most -es)
]

# A pre-computed normalisation lookup built once at import time.
# For each word in LEXICON, add common inflections that are NOT already keys.
def _build_normaliser(lexicon: dict[str, float]) -> dict[str, float]:
    """Build extended lookup table covering simple inflections of lexicon words."""
    table = dict(lexicon)
    for canon, val in lexicon.items():
        # Generate candidate inflections
        candidates: list[str] = []
        # Verb / plural forms from the canonical base
        for suffix in ("s", "es", "ed", "ing", "d"):
            candidates.append(canon + suffix)
        # Consonant-doubling for short roots ending in consonant (e.g. tip -> tipping)
        if len(canon) >= 3 and canon[-1] not in "aeiou" and canon[-2] in "aeiou":
            candidates.append(canon + canon[-1] + "ing")
            candidates.append(canon + canon[-1] + "ed")
        # Drop trailing 'e' then add -ing / -ed
        if canon.endswith("e") and len(canon) > 2:
            root = canon[:-1]
            candidates.append(root + "ing")
            candidates.append(root + "ed")
            candidates.append(root + "es")
        for cand in candidates:
            if cand not in table:          # never overwrite an explicit entry
                table[cand] = val
    return table


EXTENDED_LEXICON: dict[str, float] = _build_normaliser(LEXICON)


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


# ---------------------------------------------------------------------------
# (e) Aversion-context helpers
# ---------------------------------------------------------------------------

def _aversion_blocked(tokens: list[str], idx: int, word: str) -> bool:
    """Return True if the negative trigger `word` is preceded by an aversion verb."""
    ctx = AVERSION_CONTEXT.get(word)
    if ctx is None:
        return False
    window = tokens[max(0, idx - 6): idx]
    return any(w in ctx for w in window)


# ---------------------------------------------------------------------------
# (f) Neutral-cue helper
# ---------------------------------------------------------------------------

def _has_neutral_cue(text_lower: str) -> bool:
    """Return True if any routine/neutral cue phrase appears in the text."""
    return any(cue in text_lower for cue in NEUTRAL_CUES)


def score_sentiment(text: str) -> tuple[float, list[str]]:
    """Lexicon score with negation + intensifier handling, squashed to [-1, 1].

    Changes vs original:
    (a) Uses EXTENDED_LEXICON (inflection-aware) instead of LEXICON directly.
    (d) Checks PHRASE_SENTIMENT before token scoring so phrase weights override
        token-level scoring for matched phrases.
    (e) Skips negative weight when an aversion-context word precedes the trigger.
    (f) Shrinks score by NEUTRAL_SHRINK when a neutral cue is detected.
    (g) Negation window kept at 3 tokens (extending to 4 would flip 'no growth' tests
        due to positional overlap with intensifier window — reported in tuning log).
    """
    text_lower = text.lower()
    tokens = [m.group(0).lower() for m in _TOKEN.finditer(text)]
    total, hits = 0.0, []

    # (d) Phrase-level scoring first: remove the tokens that are part of a matched phrase
    # so they are not double-counted by the token loop.
    phrase_consumed: set[int] = set()
    for phrase, pat in _PHRASE_PATTERNS.items():
        for m in pat.finditer(text_lower):
            phrase_tokens = phrase.split()
            # Find the first token index matching the start of the phrase
            m_start = m.start()
            char_pos = 0
            for ti, tok_m in enumerate(_TOKEN.finditer(text)):
                if tok_m.start() >= m_start and ti + len(phrase_tokens) <= len(tokens):
                    # Mark all tokens in this phrase as consumed
                    for k in range(len(phrase_tokens)):
                        phrase_consumed.add(ti + k)
                    total += PHRASE_SENTIMENT[phrase]
                    hits.append(phrase)
                    break

    # Token-level scoring (skip tokens consumed by phrase matching)
    for i, tok in enumerate(tokens):
        if i in phrase_consumed:
            continue
        base = EXTENDED_LEXICON.get(tok)
        if base is None:
            continue
        # (e) Aversion context: skip this token's negative score if negated by aversion
        if base < 0 and _aversion_blocked(tokens, i, tok):
            continue
        mult = 1.0
        # (g) Negation window: 3 tokens (see docstring)
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

    # (f) Neutral-cue shrink: routine items should stay in the neutral band
    if _has_neutral_cue(text_lower):
        total *= NEUTRAL_SHRINK

    # VADER-style normalisation keeps the score in (-1, 1)
    score = total / math.sqrt(total * total + 8.0) if total else 0.0
    return round(score, 3), hits


def label_sentiment(s: float) -> str:
    return "positive" if s >= 0.15 else "negative" if s <= -0.15 else "neutral"


def classify_event(text: str) -> tuple[str, float]:
    """Score each event rule set; return (best_event, confidence).

    Change (b): If 'downgrad' is the only reason Credit Event wins, we verify
    that at least one credit/debt context token is present. If not, Credit Event
    is suppressed to Other (with appropriate negative sentiment handled separately).
    """
    lowered = text.lower()
    scores: dict[str, float] = {}
    for event, rules in EVENT_RULES.items():
        scores[event] = sum(w for pat, w in rules if re.search(pat, lowered))

    best, top = max(scores.items(), key=lambda kv: kv[1])
    if top < 2.0:
        return "Other", 0.3

    # (b) Analyst-downgrade gate: Credit Event must not fire solely on "downgrad"
    # when there is no debt/rating context.
    if best == "Credit Event":
        if re.search(r"\bdowngrad", lowered):
            # Check if we need the gate: what would the score be WITHOUT "downgrad" rules?
            score_without_downgrad = sum(
                w for pat, w in EVENT_RULES["Credit Event"]
                if not re.search(r"downgrad", pat) and re.search(pat, lowered)
            )
            if score_without_downgrad < 2.0:
                # "downgrad" is carrying all the Credit Event weight.
                # Only allow if debt/rating context is present.
                # Use word-boundary regex so 'grade' inside 'downgrades' does NOT match.
                has_ctx = any(
                    re.search(r"\b" + re.escape(tok) + r"\b", lowered)
                    for tok in CREDIT_DOWNGRADE_CONTEXT
                )
                if not has_ctx:
                    # Suppress Credit Event — pick second-best or Other
                    alt_scores = {k: v for k, v in scores.items() if k != "Credit Event"}
                    alt_best, alt_top = max(alt_scores.items(), key=lambda kv: kv[1])
                    if alt_top < 2.0:
                        return "Other", 0.3
                    total = sum(alt_scores.values())
                    return alt_best, round(alt_top / total, 2)

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
