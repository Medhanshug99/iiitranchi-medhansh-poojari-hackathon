"""Evaluation script for the NLP risk engine.

Usage:
    python -m src.evaluate

Input:  data/labeled_eval.csv
        Required columns: id, text, sentiment, event_type, source_type
        Optional column:  impact_label  (values: low | medium | high)

Output: docs/evaluation_results.md  AND  console print of the same.

Design notes
------------
- Split is deterministic: hash(id) % 2 -> dev (0) / test (1).
- Engine thresholds used exactly as in nlp.label_sentiment (±0.15).
- No sklearn, no pandas; pure standard library.
- Tuning the lexicon or rules MUST be done on DEV only; TEST is for final numbers.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import textwrap
from collections import Counter
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT     = Path(__file__).resolve().parent.parent
DATA_DIR      = REPO_ROOT / "data"
LABELED_CSV   = DATA_DIR / "labeled_eval.csv"
RESULTS_MD    = REPO_ROOT / "docs" / "evaluation_results.md"

VALID_SENTIMENTS = {"positive", "negative", "neutral"}
VALID_EVENTS     = {
    "Geopolitical", "Macroeconomic", "Credit Event", "Merger/Acquisition",
    "Product Launch", "Earnings", "Regulatory/Legal", "Cyber/Operational", "Other",
}
VALID_IMPACT = {"low", "medium", "high"}


# ---------------------------------------------------------------------------
# Metric helpers  (pure functions, testable in isolation)
# ---------------------------------------------------------------------------

def accuracy(y_true: list, y_pred: list) -> float:
    """Fraction of elements where y_true[i] == y_pred[i]."""
    if not y_true:
        return 0.0
    return sum(a == b for a, b in zip(y_true, y_pred)) / len(y_true)


def confusion_matrix(y_true: list, y_pred: list, labels: list) -> list[list[int]]:
    """Row = true class, column = predicted class, ordered by `labels`."""
    idx = {l: i for i, l in enumerate(labels)}
    n = len(labels)
    mat = [[0] * n for _ in range(n)]
    for t, p in zip(y_true, y_pred):
        if t in idx and p in idx:
            mat[idx[t]][idx[p]] += 1
    return mat


def per_class_metrics(y_true: list, y_pred: list, labels: list
                      ) -> dict[str, dict[str, float]]:
    """Return precision, recall, F1 for every label."""
    result = {}
    for lbl in labels:
        tp = sum(t == lbl and p == lbl for t, p in zip(y_true, y_pred))
        fp = sum(t != lbl and p == lbl for t, p in zip(y_true, y_pred))
        fn = sum(t == lbl and p != lbl for t, p in zip(y_true, y_pred))
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec  = tp / (tp + fn) if (tp + fn) else 0.0
        f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        result[lbl] = {"precision": prec, "recall": rec, "f1": f1,
                       "support": sum(t == lbl for t in y_true)}
    return result


def macro_f1(y_true: list, y_pred: list, labels: list) -> float:
    """Unweighted mean F1 across all labels that appear in y_true."""
    pc = per_class_metrics(y_true, y_pred, labels)
    active = [l for l in labels if pc[l]["support"] > 0]
    if not active:
        return 0.0
    return sum(pc[l]["f1"] for l in active) / len(active)


def majority_baseline(y_true: list) -> str:
    """Most frequent class."""
    return Counter(y_true).most_common(1)[0][0] if y_true else ""


# ---------------------------------------------------------------------------
# Deterministic split
# ---------------------------------------------------------------------------

def split_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Stable dev/test split by hash(id) % 2 == 0 -> dev, else -> test."""
    dev, test = [], []
    for r in rows:
        bucket = int(hashlib.md5(r["id"].encode()).hexdigest(), 16) % 2
        (dev if bucket == 0 else test).append(r)
    return dev, test


# ---------------------------------------------------------------------------
# Engine runner
# ---------------------------------------------------------------------------

def _run_engine(rows: list[dict]) -> list[dict]:
    """Run each row through the engine, return rows augmented with predictions."""
    from src.riskengine.nlp import analyze, label_sentiment
    out = []
    for r in rows:
        a = analyze(r["text"], r.get("source_type", "news"))
        out.append({
            **r,
            "pred_sentiment": a.sentiment_label,
            "pred_event":     a.event_type,
            "pred_impact":    a.impact,
            "matched_terms":  a.matched_terms,
        })
    return out


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _fmt(x: float) -> str:
    return f"{x:.3f}"


def _md_table(headers: list[str], rows: list[list]) -> str:
    widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=0))
              for i, h in enumerate(headers)]
    def row_str(r):
        return "| " + " | ".join(str(r[i]).ljust(widths[i]) for i in range(len(headers))) + " |"
    sep = "| " + " | ".join("-" * w for w in widths) + " |"
    return "\n".join([row_str(headers), sep] + [row_str(r) for r in rows])


def _confusion_md(mat: list[list[int]], labels: list[str]) -> str:
    header = ["true \\ pred"] + labels
    rows   = [[labels[i]] + mat[i] for i in range(len(labels))]
    return _md_table(header, rows)


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def _build_report(split_name: str, rows: list[dict],
                  sent_labels: list[str], evt_labels: list[str]) -> list[str]:
    lines: list[str] = []

    if not rows:
        lines.append(f"### {split_name}: *no rows*\n")
        return lines

    y_sent_true = [r["sentiment"]   for r in rows]
    y_sent_pred = [r["pred_sentiment"] for r in rows]
    y_evt_true  = [r["event_type"]  for r in rows]
    y_evt_pred  = [r["pred_event"]  for r in rows]

    # ---------- baselines ----------
    maj_sent = majority_baseline(y_sent_true)
    maj_evt  = majority_baseline(y_evt_true)
    acc_sent = accuracy(y_sent_true, y_sent_pred)
    acc_evt  = accuracy(y_evt_true,  y_evt_pred)
    mf1_sent = macro_f1(y_sent_true, y_sent_pred, sent_labels)
    mf1_evt  = macro_f1(y_evt_true,  y_evt_pred,  evt_labels)
    acc_maj_sent   = accuracy(y_sent_true, [maj_sent] * len(rows))
    acc_neutral    = accuracy(y_sent_true, ["neutral"] * len(rows))
    acc_maj_evt    = accuracy(y_evt_true,  [maj_evt]  * len(rows))
    best_sent_base = max(acc_maj_sent, acc_neutral)
    gain_sent      = acc_sent - best_sent_base
    gain_evt       = acc_evt  - acc_maj_evt

    lines.append(f"### {split_name} ({len(rows)} rows)\n")

    # ---------- sentiment ----------
    lines.append(f"#### Sentiment ({len(rows)} rows)\n")
    lines.append(_md_table(
        ["Metric", "Engine", "Majority baseline", "Always-neutral baseline"],
        [
            ["Accuracy", _fmt(acc_sent),    _fmt(acc_maj_sent),  _fmt(acc_neutral)],
            ["Macro-F1", _fmt(mf1_sent),    "—",                 "—"],
            ["Gain over best baseline (pp)", f"+{gain_sent*100:.1f}pp", "—", "—"],
        ]
    ))
    lines.append("")

    pc_sent = per_class_metrics(y_sent_true, y_sent_pred, sent_labels)
    lines.append(_md_table(
        ["Class", "Precision", "Recall", "F1", "Support"],
        [[lbl, _fmt(v["precision"]), _fmt(v["recall"]), _fmt(v["f1"]), v["support"]]
         for lbl, v in pc_sent.items()]
    ))
    lines.append("")
    lines.append(f"**Confusion matrix (sentiment, {len(rows)} rows)**\n")
    lines.append(_confusion_md(confusion_matrix(y_sent_true, y_sent_pred, sent_labels), sent_labels))
    lines.append("")

    # ---------- event type ----------
    lines.append(f"#### Event Type ({len(rows)} rows)\n")
    lines.append(_md_table(
        ["Metric", "Engine", "Majority baseline"],
        [
            ["Accuracy", _fmt(acc_evt),  _fmt(acc_maj_evt)],
            ["Macro-F1", _fmt(mf1_evt),  "—"],
            ["Gain over best baseline (pp)", f"+{gain_evt*100:.1f}pp", "—"],
        ]
    ))
    lines.append("")

    present_evts = sorted({r["event_type"] for r in rows})
    pc_evt = per_class_metrics(y_evt_true, y_evt_pred, present_evts)
    lines.append(_md_table(
        ["Class", "Precision", "Recall", "F1", "Support"],
        [[lbl, _fmt(v["precision"]), _fmt(v["recall"]), _fmt(v["f1"]), v["support"]]
         for lbl, v in pc_evt.items()]
    ))
    lines.append("")
    lines.append(f"**Confusion matrix (event type, {len(rows)} rows)**\n")
    lines.append(_confusion_md(confusion_matrix(y_evt_true, y_evt_pred, present_evts), present_evts))
    lines.append("")

    # ---------- impact ordering (optional) ----------
    if "impact_label" in rows[0]:
        lines.append("#### Impact Label Ordering\n")
        groups: dict[str, list[float]] = {}
        for r in rows:
            if r["impact_label"] in VALID_IMPACT:
                groups.setdefault(r["impact_label"], []).append(r["pred_impact"])
        means = {k: sum(v)/len(v) for k, v in groups.items() if v}
        table_rows = [[k, f"{means[k]:.2f}"] for k in ("low", "medium", "high") if k in means]
        lines.append(_md_table(["impact_label", "mean engine impact"], table_rows))
        monotonic = (means.get("low", 0) <= means.get("medium", 0) <= means.get("high", 0))
        lines.append(f"\nOrdering monotonic (low ≤ medium ≤ high): **{'YES' if monotonic else 'NO'}**\n")

    return lines


def _error_analysis(test_rows: list[dict], title: str = "TEST") -> list[str]:
    lines = [f"### Error Analysis: {title} misclassifications\n"]
    misses = [r for r in test_rows
              if r["sentiment"] != r["pred_sentiment"] or r["event_type"] != r["pred_event"]]
    misses.sort(key=lambda r: r["event_type"])
    if not misses:
        lines.append("*No misclassifications in TEST set.*\n")
        return lines

    for r in misses:
        s_wrong = " [SENT]" if r["sentiment"] != r["pred_sentiment"] else ""
        e_wrong = " [EVT]"  if r["event_type"] != r["pred_event"]   else ""
        lines.append(f"- **id={r['id']}**{s_wrong}{e_wrong}")
        lines.append(f"  - Text: *{r['text'][:100]}*")
        if s_wrong:
            lines.append(f"  - Sentiment: true=`{r['sentiment']}` pred=`{r['pred_sentiment']}`")
        if e_wrong:
            lines.append(f"  - Event: true=`{r['event_type']}` pred=`{r['pred_event']}`")
        lines.append(f"  - Matched terms: {r['matched_terms']}")
    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(args=None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate NLP risk engine.")
    parser.add_argument("--file", type=Path, default=LABELED_CSV,
                        help="Path to labeled CSV file (default: data/labeled_eval.csv)")
    parser.add_argument("--holdout", action="store_true",
                        help="Run in holdout mode (no dev/test split, report all rows together)")
    parsed_args = parser.parse_args(args)

    # ---- 1. File existence ----
    if not parsed_args.file.exists():
        msg = textwrap.dedent(f"""
            ERROR: labeled evaluation file not found.

            Expected: {parsed_args.file}

            Please create it as a CSV with these columns:
              id,text,sentiment,event_type,source_type[,impact_label]

            sentiment values : positive | negative | neutral
            event_type values: Geopolitical | Macroeconomic | Credit Event |
                               Merger/Acquisition | Product Launch | Earnings |
                               Regulatory/Legal | Cyber/Operational | Other
            source_type      : news | social
            impact_label     : low | medium | high  (optional)

            Example row:
              eval-001,"Markets crash as bank defaults spread",negative,Credit Event,news,high
        """).strip()
        print(msg)
        return 1

    # ---- 2. Load & validate ----
    with open(parsed_args.file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    required = {"id", "text", "sentiment", "event_type", "source_type"}
    missing_cols = required - set(fieldnames)
    if missing_cols:
        print(f"ERROR: Missing required columns: {missing_cols}")
        return 1

    has_impact = "impact_label" in fieldnames

    errors: list[str] = []
    seen_ids:  set[str] = set()
    seen_texts: set[str] = set()

    for i, r in enumerate(rows, 1):
        if r["sentiment"] not in VALID_SENTIMENTS:
            errors.append(f"Row {i} (id={r['id']}): invalid sentiment '{r['sentiment']}'")
        if r["event_type"] not in VALID_EVENTS:
            errors.append(f"Row {i} (id={r['id']}): invalid event_type '{r['event_type']}'")
        if r["source_type"] not in ("news", "social"):
            errors.append(f"Row {i} (id={r['id']}): invalid source_type '{r['source_type']}'")
        if has_impact and r.get("impact_label") and r["impact_label"] not in VALID_IMPACT:
            errors.append(f"Row {i} (id={r['id']}): invalid impact_label '{r['impact_label']}'")
        if r["id"] in seen_ids:
            errors.append(f"Row {i}: duplicate id '{r['id']}'")
        if r["text"].strip() in seen_texts:
            errors.append(f"Row {i} (id={r['id']}): duplicate text")
        seen_ids.add(r["id"])
        seen_texts.add(r["text"].strip())

    sent_counts = Counter(r["sentiment"]   for r in rows)
    evt_counts  = Counter(r["event_type"]  for r in rows)

    print(f"Loaded {len(rows)} rows from {parsed_args.file}")
    print(f"Sentiment counts: {dict(sorted(sent_counts.items()))}")
    print(f"Event type counts: {dict(sorted(evt_counts.items()))}")
    if has_impact:
        print(f"Impact label counts: {dict(Counter(r['impact_label'] for r in rows))}")

    if errors:
        print("\nValidation ERRORS:")
        for e in errors:
            print(" ", e)
        return 1

    print("Validation: OK\n")

    # ---- 3. Run engine ----
    print("Running engine on all rows... ", end="", flush=True)
    all_rows = _run_engine(rows)
    print("done.\n")

    sent_labels = sorted(VALID_SENTIMENTS)
    evt_labels  = sorted(VALID_EVENTS)

    # ---- 4. Build report ----
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cmd_args = f" --file {parsed_args.file} --holdout" if parsed_args.holdout else ""
    cmd = f"python -m src.evaluate{cmd_args}"

    report_lines: list[str] = [
        "# ShockWire NLP Engine – Evaluation Results\n",
        f"**Date:** {now}  ",
    ]
    
    if parsed_args.holdout:
        report_lines.append(f"**Rows:** {len(rows)} total (holdout)  ")
        report_lines.append(f"**Command:** `{cmd}`  \n")
        report_lines.append("---\n")
        report_lines.extend(_build_report("HOLDOUT", all_rows, sent_labels, evt_labels))
        report_lines.append("---\n")
        report_lines.extend(_error_analysis(all_rows, "HOLDOUT"))
    else:
        dev_rows, test_rows = split_rows(rows)
        print(f"Split: DEV={len(dev_rows)}, TEST={len(test_rows)} (stable hash(id)%2)\n")
        dev_pred  = [r for r in all_rows if r["id"] in {x["id"] for x in dev_rows}]
        test_pred = [r for r in all_rows if r["id"] in {x["id"] for x in test_rows}]
        
        report_lines.append(f"**Rows:** {len(rows)} total ({len(dev_rows)} dev / {len(test_rows)} test)  ")
        report_lines.append(f"**Command:** `{cmd}`  \n")
        report_lines.append("> ⚠️ **Protocol:** Tune lexicon/rules on **DEV only**. "
                            "TEST numbers are the **final reported accuracy**. Never tune on TEST.\n")
        report_lines.append("---\n")
        for name, subset in [("DEV", dev_pred), ("TEST", test_pred), ("ALL", all_rows)]:
            report_lines.extend(_build_report(name, subset, sent_labels, evt_labels))
            report_lines.append("---\n")
        report_lines.extend(_error_analysis(test_pred, "TEST"))

    report_text = "\n".join(report_lines)

    # ---- 5. Write + print ----
    # If not holdout, save to standard RESULTS_MD
    if not parsed_args.holdout and parsed_args.file == LABELED_CSV:
        RESULTS_MD.parent.mkdir(parents=True, exist_ok=True)
        RESULTS_MD.write_text(report_text, encoding="utf-8")
    
    print(report_text)
    if not parsed_args.holdout and parsed_args.file == LABELED_CSV:
        print(f"\nResults written to: {RESULTS_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
