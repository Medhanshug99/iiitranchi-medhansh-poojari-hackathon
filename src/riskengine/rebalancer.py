"""Module A - tactical, sentiment-driven rebalancer for a 15-stock mock index.

Method
  1. Each signal updates a per-ticker sentiment state:
        state_t = state_{t-1} * exp(-dt / half_life) + sentiment * conviction
     where conviction = impact/10 (a high-impact story moves weights more) and
     news is trusted more than social chatter (see SOURCE_WEIGHT).
  2. Market-wide signals (no ticker) shift every name by its sector beta to that
     event (e.g. a geopolitical shock hurts tech, helps energy).
  3. Target weight_i  ∝  base_i * exp(TILT * tanh(state_i))
  4. Weights are floored/capped (MIN_W..MAX_W) and renormalised so the index
     stays investable and diversified.
"""
from __future__ import annotations

import math
from datetime import datetime

from .nlp import UNIVERSE

TICKERS = list(UNIVERSE)
SECTOR = {
    "AAPL": "Tech", "MSFT": "Tech", "AMZN": "Tech", "GOOGL": "Tech", "META": "Tech",
    "NVDA": "Tech", "TSLA": "Tech", "JPM": "Financials", "BAC": "Financials",
    "GS": "Financials", "XOM": "Energy", "CVX": "Energy", "JNJ": "Health",
    "PFE": "Health", "WMT": "Staples",
}
# Sensitivity of each sector to market-wide shocks (+1 = benefits when news is positive,
# for Geopolitical shocks the sign flips for energy which benefits from supply fears).
MARKET_EVENT_BETA = {
    "Geopolitical":  {"Tech": 1.0, "Financials": 1.0, "Energy": -1.2, "Health": 0.4, "Staples": 0.2},
    "Credit Event":  {"Tech": 0.5, "Financials": 1.5, "Energy": 0.6, "Health": 0.3, "Staples": 0.2},
    "Macroeconomic": {"Tech": 1.0, "Financials": 0.7, "Energy": 0.6, "Health": 0.4, "Staples": 0.3},
}
SOURCE_WEIGHT = {"news": 1.0, "social": 0.5}
HALF_LIFE_MIN = 90.0
TILT = 1.2
MIN_W, MAX_W = 0.02, 0.15


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def apply_bounds(raw: dict[str, float], lo: float = MIN_W, hi: float = MAX_W) -> dict[str, float]:
    """Normalise to 1.0 with a per-name floor/cap (iterative water-filling)."""
    total = sum(raw.values())
    w = {k: v / total for k, v in raw.items()}
    fixed: dict[str, float] = {}
    for _ in range(len(w) + 1):
        free = [k for k in w if k not in fixed]
        if not free:
            break
        remaining = 1.0 - sum(fixed.values())
        s = sum(w[k] for k in free)
        scaled = {k: w[k] / s * remaining for k in free}
        over = [k for k, v in scaled.items() if v > hi + 1e-12]
        under = [k for k, v in scaled.items() if v < lo - 1e-12]
        if not over and not under:
            return {**fixed, **scaled}
        for k in over or under:           # resolve cap breaches first, then floors
            fixed[k] = hi if over else lo
    total = sum(fixed.values())
    return {k: v / total for k, v in fixed.items()}


class SentimentRebalancer:
    def __init__(self, tickers=None, min_w=MIN_W, max_w=MAX_W, tilt=TILT, half_life_min=HALF_LIFE_MIN):
        self.tickers = list(tickers or TICKERS)
        self.base = {t: 1.0 / len(self.tickers) for t in self.tickers}
        self.min_w, self.max_w, self.tilt, self.half_life = min_w, max_w, tilt, half_life_min
        self.state = {t: 0.0 for t in self.tickers}
        self.last_ts: datetime | None = None
        self.history: list[dict] = []

    def _decay(self, now: datetime):
        if self.last_ts is not None:
            dt = max(0.0, (now - self.last_ts).total_seconds() / 60.0)
            f = math.exp(-math.log(2) * dt / self.half_life)
            self.state = {t: s * f for t, s in self.state.items()}
        self.last_ts = now

    def weights(self) -> dict[str, float]:
        raw = {t: self.base[t] * math.exp(self.tilt * math.tanh(self.state[t])) for t in self.tickers}
        return apply_bounds(raw, self.min_w, self.max_w)

    def update(self, signal: dict) -> dict[str, float]:
        self._decay(_parse(signal["ts"]))
        conviction = signal["impact"] / 10.0 * SOURCE_WEIGHT.get(signal["source_type"], 0.5)
        push = signal["sentiment"] * conviction * 1.5
        names = [t for t in signal["entities"] if t in self.state]
        if names:
            for t in names:
                self.state[t] += push / math.sqrt(len(names))
        else:
            beta = MARKET_EVENT_BETA.get(signal["event_type"])
            if beta:
                for t in self.tickers:
                    self.state[t] += push * beta.get(SECTOR.get(t, ""), 0.3) * 0.6
        w = self.weights()
        self.history.append({"ts": signal["ts"], "trigger": signal["id"],
                             "event_type": signal["event_type"], "sentiment": signal["sentiment"],
                             "impact": signal["impact"], "weights": w})
        return w

    def replay(self, signals: list[dict]) -> list[dict]:
        self.__init__(self.tickers, self.min_w, self.max_w, self.tilt, self.half_life)
        for s in sorted(signals, key=lambda x: x["ts"]):
            if s["entities"] or s["event_type"] in MARKET_EVENT_BETA:
                self.update(s)
        return self.history


def summarize(history: list[dict]) -> dict:
    if not history:
        return {"movers_up": [], "movers_down": [], "turnover": 0.0}
    first = {t: 1 / len(TICKERS) for t in TICKERS}
    last = history[-1]["weights"]
    delta = {t: last[t] - first[t] for t in TICKERS}
    turnover = 0.0
    prev = first
    for h in history:
        turnover += 0.5 * sum(abs(h["weights"][t] - prev[t]) for t in TICKERS)
        prev = h["weights"]
    ranked = sorted(delta.items(), key=lambda kv: kv[1])
    return {
        "movers_up": [(t, round(d, 4)) for t, d in ranked[::-1][:3]],
        "movers_down": [(t, round(d, 4)) for t, d in ranked[:3]],
        "turnover": round(turnover, 3),
        "final_weights": last,
    }
