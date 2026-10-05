"""Flask app: Risk Engine REST API + dashboard for Module A and Module B.

Run:  python app.py            (http://localhost:5000)
      python app.py --live     (try live RSS/Reddit, fall back to samples)
"""
from __future__ import annotations

import argparse
from dataclasses import asdict

from flask import Flask, jsonify, render_template, request

from src.riskengine import pipeline
from src.riskengine.nlp import analyze, UNIVERSE
from src.riskengine.rebalancer import SentimentRebalancer, summarize, SECTOR
from src.riskengine.stress import (
    DEFAULT_TRIGGER, SCENARIOS, load_portfolio, run_stress, stress_from_signals,
)

app = Flask(__name__)
STATE: dict = {"signals": [], "live": False, "live_requested": False, "sources": {"news": "sample", "social": "sample"}}


def refresh(live: bool = False):
    sigs, prov = pipeline.run(live=live)
    STATE["signals"] = [s.to_dict() for s in sigs]
    STATE["live_requested"] = live
    STATE["sources"] = prov
    STATE["live"] = any(v == "live" for v in prov.values())


@app.get("/")
def index():
    return render_template("dashboard.html")


# ---- Risk Engine API ------------------------------------------------------
@app.get("/api/signals")
def api_signals():
    sigs = STATE["signals"]
    if t := request.args.get("ticker"):
        sigs = [s for s in sigs if t.upper() in s["entities"]]
    if e := request.args.get("event_type"):
        sigs = [s for s in sigs if s["event_type"].lower() == e.lower()]
    if m := request.args.get("min_impact", type=float):
        sigs = [s for s in sigs if s["impact"] >= m]
    limit = request.args.get("limit", type=int)
    return jsonify(sigs[-limit:] if limit else sigs)


@app.post("/api/analyze")
def api_analyze():
    body = request.get_json(silent=True) or {}
    text = (body.get("text") or "").strip()
    if not text:
        return jsonify({"error": "field 'text' is required"}), 400
    a = analyze(text, body.get("source_type", "news"), int(body.get("engagement", 0)))
    return jsonify(a.to_dict())


@app.post("/api/refresh")
def api_refresh():
    live = bool((request.get_json(silent=True) or {}).get("live", False))
    refresh(live)
    return jsonify({"signals": len(STATE["signals"]), "live": live})


# ---- Module A -------------------------------------------------------------
@app.get("/api/rebalance")
def api_rebalance():
    reb = SentimentRebalancer()
    hist = reb.replay(STATE["signals"])
    return jsonify({"tickers": reb.tickers, "sectors": SECTOR, "history": hist,
                    "summary": summarize(hist)})


# ---- Module B -------------------------------------------------------------
@app.get("/api/stress")
def api_stress():
    thr = request.args.get("threshold", DEFAULT_TRIGGER, type=float)
    return jsonify({"threshold": thr, "runs": stress_from_signals(STATE["signals"], thr)})


@app.post("/api/stress/run")
def api_stress_run():
    name = (request.get_json(silent=True) or {}).get("scenario")
    if name not in SCENARIOS:
        return jsonify({"error": "unknown scenario", "available": list(SCENARIOS)}), 400
    return jsonify(run_stress(load_portfolio(), SCENARIOS[name]))


@app.get("/api/scenarios")
def api_scenarios():
    return jsonify({k: asdict(v) for k, v in SCENARIOS.items()})


@app.get("/api/summary")
def api_summary():
    sigs = STATE["signals"]
    by_event: dict = {}
    for s in sigs:
        by_event[s["event_type"]] = by_event.get(s["event_type"], 0) + 1
    return jsonify({
        "total": len(sigs),
        "by_source": {k: sum(1 for s in sigs if s["source_type"] == k) for k in ("news", "social")},
        "by_event": by_event,
        "avg_sentiment": round(sum(s["sentiment"] for s in sigs) / max(len(sigs), 1), 3),
        "high_impact": sum(1 for s in sigs if s["impact"] > DEFAULT_TRIGGER),
        "live": STATE["live"],
        "live_requested": STATE["live_requested"],
        "sources": STATE["sources"],
    })


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--port", type=int, default=5000)
    args = ap.parse_args()
    refresh(args.live)
    app.run(host="0.0.0.0", port=args.port, debug=False)
