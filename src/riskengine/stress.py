"""Module B - event-driven stress testing of a synthetic wholesale-banking book.

Pipeline: a high-impact signal (default: impact > 7) selects a shock scenario by
event type; shocks are applied position-by-position with simple, transparent
sensitivities and the book is re-valued before/after.

Revaluation (all P&L in portfolio currency, USD):
  Equity      dV = MV * beta * equity_shock (+ sector override)
  Bond        dV = -MV * (dur * dY + spread_dur * dS)     (spread only on non-govt)
  Loan        dV = -MV * spread_dur * dS  -  EAD * LGD * (PD_stressed - PD)
  IR swap     dV = DV01 * dY(bp)           (DV01 signed by position)
  CDS         dV = CS01 * dS(bp)           (CS01 signed by position)
  FX forward  dV = Notional * direction * fx_shock
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

PORTFOLIO_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "sample_portfolio.csv"
DEFAULT_TRIGGER = 7.0


@dataclass
class Scenario:
    name: str
    description: str
    equity_shock: float            # e.g. -0.10
    rate_shock_bp: float           # parallel shift in govt yields
    spread_shock_bp: float         # credit-spread widening
    fx_shock: float                # change in EUR/JPY vs USD (negative = USD strengthens)
    pd_multiplier: float           # stress multiplier on default probabilities
    sector_equity_override: dict = field(default_factory=dict)
    sector_pd_multiplier: dict = field(default_factory=dict)


SCENARIOS = {
    "Geopolitical": Scenario(
        "Geopolitical shock", "Armed conflict: risk-off, flight to quality, oil spike.",
        equity_shock=-0.10, rate_shock_bp=-50, spread_shock_bp=150, fx_shock=-0.04, pd_multiplier=1.6,
        sector_equity_override={"Energy": 0.08, "Financials": -0.14},
        sector_pd_multiplier={"Transport": 2.2, "Energy": 0.9, "Consumer": 1.8},
    ),
    "Credit Event": Scenario(
        "Credit event / bank contagion", "Systemic credit scare: spreads gap wider, financials sell off.",
        equity_shock=-0.12, rate_shock_bp=-30, spread_shock_bp=250, fx_shock=-0.02, pd_multiplier=2.2,
        sector_equity_override={"Financials": -0.25},
        sector_pd_multiplier={"Financials": 3.0, "Real Estate": 2.8},
    ),
    "Macroeconomic": Scenario(
        "Macro / rates shock", "Hawkish surprise: +200bp parallel rate move, moderate spread widening.",
        equity_shock=-0.08, rate_shock_bp=200, spread_shock_bp=60, fx_shock=-0.03, pd_multiplier=1.4,
        sector_equity_override={"Tech": -0.14, "Real Estate": -0.10},
        sector_pd_multiplier={"Real Estate": 2.0},
    ),
    "Regulatory/Legal": Scenario(
        "Regulatory / legal shock", "Sector enforcement action: equity de-rating, mild credit impact.",
        equity_shock=-0.04, rate_shock_bp=0, spread_shock_bp=30, fx_shock=0.0, pd_multiplier=1.1,
        sector_equity_override={"Tech": -0.08},
    ),
    "Cyber/Operational": Scenario(
        "Cyber / operational disruption", "Major outage or cyber event: equity & operational stress.",
        equity_shock=-0.05, rate_shock_bp=0, spread_shock_bp=40, fx_shock=0.0, pd_multiplier=1.2,
        sector_equity_override={"Tech": -0.09, "Financials": -0.07},
    ),
}
# Supply a plain "equity -10%, rates +2%" scenario exactly as in the case-study prompt.
SCENARIOS["Custom: equity -10%, rates +200bp"] = Scenario(
    "Custom: equity -10%, rates +200bp", "Textbook shock from the brief.",
    equity_shock=-0.10, rate_shock_bp=200, spread_shock_bp=0, fx_shock=0.0, pd_multiplier=1.0)


def load_portfolio(path: Path = PORTFOLIO_PATH) -> list[dict]:
    numeric = ("market_value", "notional", "duration", "spread_dur", "beta", "pd", "lgd", "dv01", "cs01", "fx_direction")
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in numeric:
            r[k] = float(r[k])
    return rows


def position_pnl(p: dict, sc: Scenario) -> float:
    t, sector = p["asset_type"], p["sector"]
    mv, dy, ds = p["market_value"], sc.rate_shock_bp / 1e4, sc.spread_shock_bp / 1e4
    if t == "Equity":
        shock = sc.sector_equity_override.get(sector, sc.equity_shock * p["beta"])
        return mv * shock
    if t == "Bond":
        spread_part = 0.0 if sector in ("Government",) else p["spread_dur"] * ds
        return -mv * (p["duration"] * dy + spread_part)
    if t == "Loan":
        mult = sc.sector_pd_multiplier.get(sector, sc.pd_multiplier)
        stressed_pd = min(1.0, p["pd"] * mult)
        credit_loss = p["notional"] * p["lgd"] * (stressed_pd - p["pd"])
        return -mv * p["spread_dur"] * ds - credit_loss
    if t == "Derivative":
        sub = p["subtype"]
        if sub.startswith("IR Swap"):
            return p["dv01"] * sc.rate_shock_bp
        if sub.startswith("CDS"):
            return p["cs01"] * sc.spread_shock_bp
        if sub.startswith("FX"):
            return p["notional"] * p["fx_direction"] * sc.fx_shock
    return 0.0


def run_stress(portfolio: list[dict], sc: Scenario) -> dict:
    positions, by_type = [], {}
    for p in portfolio:
        pnl = position_pnl(p, sc)
        positions.append({"id": p["id"], "asset_type": p["asset_type"], "subtype": p["subtype"],
                          "counterparty": p["counterparty"], "sector": p["sector"],
                          "before": p["market_value"], "after": p["market_value"] + pnl, "pnl": pnl})
        d = by_type.setdefault(p["asset_type"], {"before": 0.0, "after": 0.0})
        d["before"] += p["market_value"]
        d["after"] += p["market_value"] + pnl
    before = sum(x["before"] for x in positions)
    after = sum(x["after"] for x in positions)
    worst = sorted(positions, key=lambda x: x["pnl"])[:5]
    return {
        "scenario": sc.name, "description": sc.description,
        "before": before, "after": after, "pnl": after - before, "pnl_pct": (after - before) / before,
        "by_asset_type": {k: {**v, "pnl": v["after"] - v["before"]} for k, v in by_type.items()},
        "worst_positions": worst,
        "shocks": {"equity": sc.equity_shock, "rates_bp": sc.rate_shock_bp, "spread_bp": sc.spread_shock_bp,
                   "fx": sc.fx_shock, "pd_multiplier": sc.pd_multiplier},
    }


def triggered_events(signals: list[dict], threshold: float = DEFAULT_TRIGGER) -> list[dict]:
    """High-impact signals that map to a scenario; consecutive duplicates of one
    event type within 60 minutes are collapsed so one crisis = one stress run."""
    out, last_seen = [], {}
    from datetime import datetime
    for s in sorted(signals, key=lambda x: x["ts"]):
        if s["impact"] > threshold and s["event_type"] in SCENARIOS and s["sentiment_label"] == "negative":
            ts = datetime.fromisoformat(s["ts"].replace("Z", "+00:00"))
            prev = last_seen.get(s["event_type"])
            if prev and (ts - prev).total_seconds() < 3600:
                continue
            last_seen[s["event_type"]] = ts
            out.append(s)
    return out


def stress_from_signals(signals: list[dict], threshold: float = DEFAULT_TRIGGER, portfolio=None) -> list[dict]:
    portfolio = portfolio or load_portfolio()
    results = []
    for s in triggered_events(signals, threshold):
        r = run_stress(portfolio, SCENARIOS[s["event_type"]])
        r["trigger"] = {"id": s["id"], "ts": s["ts"], "event_type": s["event_type"],
                        "impact": s["impact"], "text": s["text"]}
        results.append(r)
    return results
