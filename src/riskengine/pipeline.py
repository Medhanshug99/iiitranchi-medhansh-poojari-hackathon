"""Risk Engine pipeline: ingest -> analyze -> structured signals (JSONL / API)."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

from .ingest import RawItem, gather
from .nlp import analyze

SIGNALS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "signals.jsonl"


@dataclass
class Signal:
    id: str
    ts: str
    source: str
    source_type: str
    entities: list          # tickers (empty list => market-wide event)
    sentiment: float        # -1.0 .. 1.0
    sentiment_label: str
    event_type: str
    event_confidence: float
    impact: float           # 1 .. 10
    text: str

    def to_dict(self):
        return asdict(self)


def to_signal(item: RawItem) -> Signal:
    a = analyze(item.text, item.source_type, item.engagement)
    return Signal(
        id=item.id, ts=item.ts, source=item.source, source_type=item.source_type,
        entities=a.tickers, sentiment=a.sentiment, sentiment_label=a.sentiment_label,
        event_type=a.event_type, event_confidence=a.event_confidence, impact=a.impact,
        text=item.text,
    )


def build_signals(items: Iterable[RawItem]) -> list[Signal]:
    return [to_signal(i) for i in items]


def write_signals(signals: list[Signal], path: Path = SIGNALS_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for s in signals:
            f.write(json.dumps(s.to_dict(), ensure_ascii=False) + "\n")
    return path


def load_signals(path: Path = SIGNALS_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run(live: bool = False, path: Path = SIGNALS_PATH) -> list[Signal]:
    signals = build_signals(gather(live=live))
    write_signals(signals, path)
    return signals


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Run the NLP risk engine and write signals.jsonl")
    ap.add_argument("--live", action="store_true", help="fetch live RSS/Reddit (falls back to samples)")
    args = ap.parse_args()
    sigs = run(live=args.live)
    print(f"wrote {len(sigs)} signals -> {SIGNALS_PATH}")
    for s in sigs[:8]:
        print(f"{s.ts[11:16]} {s.source_type:6} {s.event_type:20} sent={s.sentiment:+.2f} impact={s.impact:4.1f} {s.entities} | {s.text[:60]}")
