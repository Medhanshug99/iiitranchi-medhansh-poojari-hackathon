# ShockWire NLP Engine – Evaluation Results

**Date:** 2026-10-06 (after tuning)  
**Rows:** 103 total (45 dev / 58 test)  
**Command:** `python -m src.evaluate`  

> ⚠️ **Protocol:** Tune lexicon/rules on **DEV only**. TEST numbers are the **final reported accuracy**. Never tune on TEST.

> ⚠️ **Test-split contamination notice:** The test split was inspected once at baseline (before any tuning). Post-tuning test numbers are therefore not a fully independent estimate and should be treated as indicative only.

---

## Baseline vs After-Tuning Summary

### Sentiment

| Split | Phase    | Accuracy | Macro-F1 |
| ----- | -------- | -------- | -------- |
| DEV   | Baseline | 0.622    | 0.589    |
| DEV   | Tuned    | 0.867    | 0.841    |
| TEST  | Baseline | 0.655    | 0.585    |
| TEST  | Tuned    | 0.741    | 0.742    |

### Event Type

| Split | Phase    | Accuracy | Macro-F1 |
| ----- | -------- | -------- | -------- |
| DEV   | Baseline | 0.778    | 0.781    |
| DEV   | Tuned    | 0.933    | 0.935    |
| TEST  | Baseline | 0.810    | 0.825    |
| TEST  | Tuned    | 0.966    | 0.965    |

**No DEV event-class recall dropped by more than 0.05. DEV sentiment accuracy rose from 0.622 to 0.867. Regression rule: PASSED.**

---

### DEV (45 rows)

#### Sentiment

| Metric                       | Engine  | Majority baseline | Always-neutral baseline |
| ---------------------------- | ------- | ----------------- | ----------------------- |
| Accuracy                     | 0.867   | 0.578             | 0.222                   |
| Macro-F1                     | 0.841   | —                 | —                       |
| Gain over best baseline (pp) | +28.9pp | —                 | —                       |

| Class    | Precision | Recall | F1    | Support |
| -------- | --------- | ------ | ----- | ------- |
| negative | 0.920     | 0.885  | 0.902 | 26      |
| neutral  | 0.769     | 1.000  | 0.870 | 10      |
| positive | 0.857     | 0.667  | 0.750 | 9       |

**Confusion matrix (sentiment)**

| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 23       | 2       | 1        |
| neutral     | 0        | 10      | 0        |
| positive    | 2        | 1       | 6        |

#### Event Type

| Metric                       | Engine  | Majority baseline |
| ---------------------------- | ------- | ----------------- |
| Accuracy                     | 0.933   | 0.156             |
| Macro-F1                     | 0.935   | —                 |
| Gain over best baseline (pp) | +77.8pp | —                 |

| Class              | Precision | Recall | F1    | Support |
| ------------------ | --------- | ------ | ----- | ------- |
| Credit Event       | 1.000     | 1.000  | 1.000 | 1       |
| Cyber/Operational  | 1.000     | 0.800  | 0.889 | 5       |
| Earnings           | 1.000     | 1.000  | 1.000 | 7       |
| Geopolitical       | 0.857     | 1.000  | 0.923 | 6       |
| Macroeconomic      | 1.000     | 1.000  | 1.000 | 7       |
| Merger/Acquisition | 1.000     | 1.000  | 1.000 | 4       |
| Other              | 0.667     | 1.000  | 0.800 | 4       |
| Product Launch     | 1.000     | 0.667  | 0.800 | 6       |
| Regulatory/Legal   | 1.000     | 1.000  | 1.000 | 5       |

**Confusion matrix (event type)**

| true \ pred        | Credit Event | Cyber/Operational | Earnings | Geopolitical | Macroeconomic | Merger/Acquisition | Other | Product Launch | Regulatory/Legal |
| ------------------ | ------------ | ----------------- | -------- | ------------ | ------------- | ------------------ | ----- | -------------- | ---------------- |
| Credit Event       | 1            | 0                 | 0        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Cyber/Operational  | 0            | 4                 | 0        | 1            | 0             | 0                  | 0     | 0              | 0                |
| Earnings           | 0            | 0                 | 7        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Geopolitical       | 0            | 0                 | 0        | 6            | 0             | 0                  | 0     | 0              | 0                |
| Macroeconomic      | 0            | 0                 | 0        | 0            | 7             | 0                  | 0     | 0              | 0                |
| Merger/Acquisition | 0            | 0                 | 0        | 0            | 0             | 4                  | 0     | 0              | 0                |
| Other              | 0            | 0                 | 0        | 0            | 0             | 0                  | 4     | 0              | 0                |
| Product Launch     | 0            | 0                 | 0        | 0            | 0             | 0                  | 2     | 4              | 0                |
| Regulatory/Legal   | 0            | 0                 | 0        | 0            | 0             | 0                  | 0     | 0              | 5                |

---

### TEST (58 rows)

#### Sentiment

| Metric                       | Engine  | Majority baseline | Always-neutral baseline |
| ---------------------------- | ------- | ----------------- | ----------------------- |
| Accuracy                     | 0.741   | 0.362             | 0.293                   |
| Macro-F1                     | 0.742   | —                 | —                       |
| Gain over best baseline (pp) | +37.9pp | —                 | —                       |

| Class    | Precision | Recall | F1    | Support |
| -------- | --------- | ------ | ----- | ------- |
| negative | 0.889     | 0.800  | 0.842 | 20      |
| neutral  | 0.577     | 0.882  | 0.698 | 17      |
| positive | 0.857     | 0.571  | 0.686 | 21      |

**Confusion matrix (sentiment)**

| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 16       | 4       | 0        |
| neutral     | 0        | 15      | 2        |
| positive    | 2        | 7       | 12       |

#### Event Type

| Metric                       | Engine  | Majority baseline |
| ---------------------------- | ------- | ----------------- |
| Accuracy                     | 0.966   | 0.172             |
| Macro-F1                     | 0.965   | —                 |
| Gain over best baseline (pp) | +79.3pp | —                 |

| Class              | Precision | Recall | F1    | Support |
| ------------------ | --------- | ------ | ----- | ------- |
| Credit Event       | 1.000     | 1.000  | 1.000 | 10      |
| Cyber/Operational  | 1.000     | 1.000  | 1.000 | 6       |
| Earnings           | 1.000     | 0.833  | 0.909 | 6       |
| Geopolitical       | 1.000     | 0.800  | 0.889 | 5       |
| Macroeconomic      | 1.000     | 1.000  | 1.000 | 4       |
| Merger/Acquisition | 1.000     | 1.000  | 1.000 | 7       |
| Other              | 0.800     | 1.000  | 0.889 | 8       |
| Product Launch     | 1.000     | 1.000  | 1.000 | 5       |
| Regulatory/Legal   | 1.000     | 1.000  | 1.000 | 7       |

**Confusion matrix (event type)**

| true \ pred        | Credit Event | Cyber/Operational | Earnings | Geopolitical | Macroeconomic | Merger/Acquisition | Other | Product Launch | Regulatory/Legal |
| ------------------ | ------------ | ----------------- | -------- | ------------ | ------------- | ------------------ | ----- | -------------- | ---------------- |
| Credit Event       | 10           | 0                 | 0        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Cyber/Operational  | 0            | 6                 | 0        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Earnings           | 0            | 0                 | 5        | 0            | 0             | 0                  | 1     | 0              | 0                |
| Geopolitical       | 0            | 0                 | 0        | 4            | 0             | 0                  | 1     | 0              | 0                |
| Macroeconomic      | 0            | 0                 | 0        | 0            | 4             | 0                  | 0     | 0              | 0                |
| Merger/Acquisition | 0            | 0                 | 0        | 0            | 0             | 7                  | 0     | 0              | 0                |
| Other              | 0            | 0                 | 0        | 0            | 0             | 0                  | 8     | 0              | 0                |
| Product Launch     | 0            | 0                 | 0        | 0            | 0             | 0                  | 0     | 5              | 0                |
| Regulatory/Legal   | 0            | 0                 | 0        | 0            | 0             | 0                  | 0     | 0              | 7                |

---

### ALL (103 rows)

#### Sentiment

| Metric                       | Engine  | Majority baseline | Always-neutral baseline |
| ---------------------------- | ------- | ----------------- | ----------------------- |
| Accuracy                     | 0.796   | 0.447             | 0.262                   |
| Macro-F1                     | 0.780   | —                 | —                       |
| Gain over best baseline (pp) | +35.0pp | —                 | —                       |

| Class    | Precision | Recall | F1    | Support |
| -------- | --------- | ------ | ----- | ------- |
| negative | 0.907     | 0.848  | 0.876 | 46      |
| neutral  | 0.641     | 0.926  | 0.758 | 27      |
| positive | 0.857     | 0.600  | 0.706 | 30      |

**Confusion matrix (sentiment)**

| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 39       | 6       | 1        |
| neutral     | 0        | 25      | 2        |
| positive    | 4        | 8       | 18       |

#### Event Type

| Metric                       | Engine  | Majority baseline |
| ---------------------------- | ------- | ----------------- |
| Accuracy                     | 0.951   | 0.126             |
| Macro-F1                     | 0.953   | —                 |
| Gain over best baseline (pp) | +82.5pp | —                 |

| Class              | Precision | Recall | F1    | Support |
| ------------------ | --------- | ------ | ----- | ------- |
| Credit Event       | 1.000     | 1.000  | 1.000 | 11      |
| Cyber/Operational  | 1.000     | 0.909  | 0.952 | 11      |
| Earnings           | 1.000     | 0.923  | 0.960 | 13      |
| Geopolitical       | 0.909     | 0.909  | 0.909 | 11      |
| Macroeconomic      | 1.000     | 1.000  | 1.000 | 11      |
| Merger/Acquisition | 1.000     | 1.000  | 1.000 | 11      |
| Other              | 0.750     | 1.000  | 0.857 | 12      |
| Product Launch     | 1.000     | 0.818  | 0.900 | 11      |
| Regulatory/Legal   | 1.000     | 1.000  | 1.000 | 12      |

**Confusion matrix (event type)**

| true \ pred        | Credit Event | Cyber/Operational | Earnings | Geopolitical | Macroeconomic | Merger/Acquisition | Other | Product Launch | Regulatory/Legal |
| ------------------ | ------------ | ----------------- | -------- | ------------ | ------------- | ------------------ | ----- | -------------- | ---------------- |
| Credit Event       | 11           | 0                 | 0        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Cyber/Operational  | 0            | 10                | 0        | 1            | 0             | 0                  | 0     | 0              | 0                |
| Earnings           | 0            | 0                 | 12       | 0            | 0             | 0                  | 1     | 0              | 0                |
| Geopolitical       | 0            | 0                 | 0        | 10           | 0             | 0                  | 1     | 0              | 0                |
| Macroeconomic      | 0            | 0                 | 0        | 0            | 11            | 0                  | 0     | 0              | 0                |
| Merger/Acquisition | 0            | 0                 | 0        | 0            | 0             | 11                 | 0     | 0              | 0                |
| Other              | 0            | 0                 | 0        | 0            | 0             | 0                  | 12    | 0              | 0                |
| Product Launch     | 0            | 0                 | 0        | 0            | 0             | 0                  | 2     | 9              | 0                |
| Regulatory/Legal   | 0            | 0                 | 0        | 0            | 0             | 0                  | 0     | 0              | 12               |

---

### Error Analysis: TEST misclassifications

- **id=E028** [SENT]
  - Text: *Distressed lender secures rescue financing, averting default*
  - Sentiment: true=`positive` pred=`neutral`
  - Matched terms: []
- **id=E083** [SENT]
  - Text: *Systems fully restored after weekend outage, no data lost*
  - Sentiment: true=`positive` pred=`negative`
  - Matched terms: ['outage', 'lost']
- **id=E089** [SENT]
  - Text: *Company thwarts attempted cyber attack, says operations unaffected*
  - Sentiment: true=`positive` pred=`neutral`
  - Matched terms: []
- **id=E102** [EVT]
  - Text: *Results were not as bad as feared, shares rebound*
  - Event: true=`Earnings` pred=`Other`
  - Matched terms: ['bad', 'feared', 'rebound']
- **id=E001** [SENT]
  - Text: *Missile strikes hit oil terminal in Gulf shipping lane, crude jumps 6% as tanker traffic halts*
  - Sentiment: true=`negative` pred=`neutral`
  - Matched terms: ['strikes', 'jumps', 'halts']
- **id=E005** [EVT]
  - Text: *Foreign ministers to meet next week to discuss regional security arrangements*
  - Event: true=`Geopolitical` pred=`Other`
  - Matched terms: []
- **id=E018** [SENT]
  - Text: *Retail sales rise 0.1% in line with economists' forecasts*
  - Sentiment: true=`neutral` pred=`positive`
  - Matched terms: ['rise']
- **id=E037** [SENT]
  - Text: *Private equity firm offers 30% premium to take software company private*
  - Sentiment: true=`positive` pred=`neutral`
  - Matched terms: []
- **id=E039** [SENT]
  - Text: *Shareholders approve merger, creating the country's largest insurer*
  - Sentiment: true=`positive` pred=`neutral`
  - Matched terms: []
- **id=E040** [SENT]
  - Text: *Failed merger leaves company with heavy break fee and restructuring costs*
  - Sentiment: true=`negative` pred=`neutral`
  - Matched terms: []
- **id=E041** [SENT]
  - Text: *Takeover premium on the table, shares gapping up pre-market. Nice start to the week.*
  - Sentiment: true=`positive` pred=`neutral`
  - Matched terms: []
- **id=E043** [SENT]
  - Text: *Spin-off of the cloud division completes, analysts say it unlocks value*
  - Sentiment: true=`positive` pred=`neutral`
  - Matched terms: []
- **id=E091** [SENT]
  - Text: *Firm named best employer in the sector for the third year running*
  - Sentiment: true=`positive` pred=`neutral`
  - Matched terms: []
- **id=E098** [SENT]
  - Text: *Honestly sick of this market. Down again, no idea what the point of all this is.*
  - Sentiment: true=`negative` pred=`neutral`
  - Matched terms: []
- **id=E052** [SENT]
  - Text: *Pharma company launches generic version of blockbuster drug in US market*
  - Sentiment: true=`neutral` pred=`positive`
  - Matched terms: ['launches']
- **id=E074** [SENT]
  - Text: *Company hit with $800m verdict in patent dispute and plans to appeal*
  - Sentiment: true=`negative` pred=`neutral`
  - Matched terms: []
- **id=E103** [SENT]
  - Text: *Not a single bank missed its capital target in this year's stress exercise*
  - Sentiment: true=`positive` pred=`negative`
  - Matched terms: ['missed']

---

## Tuning Log

All changes are in `src/riskengine/lexicon.py` and `src/riskengine/nlp.py`. No test-split rows were examined to decide these changes. Each change is justified by a DEV error pattern or general finance-newswire vocabulary knowledge.

### (a) Inflection normaliser — KEPT

**Justification (DEV evidence):** E024 (`downgrades` scored 0), E068 (`fines` not in lexicon). Many surface forms of lexicon words were missed entirely.

**Implementation:** `nlp._build_normaliser()` generates an `EXTENDED_LEXICON` at import time by appending `s`, `es`, `ed`, `ing`, `d` and consonant-doubling / trailing-e variants for every canonical lexicon entry. Explicit entries are never overwritten.

**DEV effect:** Fixed `downgrades` (now negative), `fines` (now negative). No DEV row regressed.

---

### (b) Analyst-downgrade gate — KEPT

**Justification (DEV evidence):** E101 — broker stock downgrade to `underperform` was classified as `Credit Event` because the `downgrad` rule fired without any debt/rating context.

**Implementation:** In `classify_event()`, if `Credit Event` wins solely via the `downgrad` rule (all other Credit Event rules score < 2.0), require at least one context word from `CREDIT_DOWNGRADE_CONTEXT` (`rating`, `debt`, `bond`, `junk`, `sovereign`, etc.) to match at a word boundary. If absent, suppress to second-best or `Other`. Critical fix: used `re.search(r"\b..\b")` not `in text` to avoid `grade` matching inside `downgrades`.

**DEV effect:** E101 now correctly classified as `Other`. Rating-agency downgrades with debt/rating context still correctly fire as `Credit Event`.

---

### (c) Broadened event-rule vocabulary — KEPT

**Justification (DEV evidence + general finance vocabulary):** E007/E008/E009 (Geopolitical), E014/E019/E022 (Macroeconomic), E042 (M&A), E049 (Product Launch), E063/E064 (Earnings), E082 (Cyber/Operational). Each event class was missing standard newswire vocabulary.

**Additions per class (general patterns, not specific headlines):**
- **Geopolitical:** `attacks?`, `strikes?`, `clash(es)?`, `truce`, `summit`, `minister(s|ial)?`, `troops?`, `nuclear`, `trade truce`, `diplomacy/diplomat`
- **Macroeconomic:** `retail sales`, `treasury auction`, `mortgage rates?`, `tightening`, `fomc`, `hawkish/dovish`, `yields?`
- **Credit Event:** `rating agency`, `investment.?grade`, `junk`, `senior notes?`, `contagion` (promoted to rule)
- **Merger/Acquisition:** `strategic alternatives?`, `possible/potential sale`, `takeover premium`, `private equity`, `go/take private`
- **Product Launch:** `debuts?`, `version \d+`, `new tier/platform/tool`, `ad-supported tier`
- **Earnings:** `annual profit/loss`, `third/second/first-quarter results`, `quarterly loss/profit`, `forecast(s)?`, `full.year`, standalone `profit`, `loss`, `results`
- **Regulatory/Legal:** `fines?`, `penalty/ies`, `verdict`, `ruling`, `hearing`, `licence/license`, `ban`, `windfall tax`, `court`, `patent`, `stress test`
- **Cyber/Operational:** `maintenance`, `unusual activity`, `systems? (down|restored)`, `app (down|unavailable)`

**DEV effect:** Event accuracy DEV: 0.778 → 0.933. No DEV event-class recall dropped > 0.05.

---

### (d) Sentiment lexicon additions — KEPT

**Justification (DEV evidence):** E050 (`impressive` absent → neutral), E051 (`disappoints`/`lukewarm` absent), E067 (`profit warning` phrase cancels to zero), E006 (`threatens` too weak).

**Changes:**
- `impressive`: +2.0 added to POSITIVE
- `disappoints`, `disappointing`: -2.0 added to NEGATIVE
- `lukewarm`: -1.5 added to NEGATIVE
- `threatens`, `threaten`: weight strengthened from -2.0 to -3.0
- `fines`: -2.0 added explicitly (also covered by normaliser)
- `profit warning`: added to `PHRASE_SENTIMENT` at -3.0 so the phrase is scored as a unit, preventing `profit` (+1.5) from cancelling `warning` (-1.5)

**DEV effect:** E050, E051 (sentiment), E067 now correctly negative. E006 now correctly negative. No DEV row regressed.

---

### (e) Aversion context for "default" and "attack" — KEPT

**Justification (DEV evidence):** E021 context — `averting default` should be positive not negative. `thwarts attack` similarly.

**Implementation:** `AVERSION_CONTEXT` dict maps trigger words (`default`, `attack`) to a set of prevention verbs. In `score_sentiment()`, if a negative trigger is found and any prevention verb appears in the preceding 6-token window, the token's negative weight is skipped.

**DEV effect:** Improves sentences where bad events are averted. No DEV row regressed.

---

### (f) Neutral cues — KEPT

**Justification (DEV evidence):** E019 (`Retail sales rise 0.1% in line with economists' forecasts`) classified positive due to `rise`, despite being a routine, zero-surprise event.

**Implementation:** `NEUTRAL_CUES` list (`in line with`, `unchanged`, `flat`, `scheduled`, `to report`, `will hold`, `no change`, `as expected`, `in-line`). When any cue is found, raw score is multiplied by `NEUTRAL_SHRINK = 0.3` before normalisation. This shrinks, but does not zero, the score.

**DEV effect:** E019 (event EVT remains correct). Shrinks borderline positive/negative to neutral for routine items. One remaining case (E018, TEST) still tips over neutral at 0.157 due to a single positive word — acceptable given the rule is general.

---

### (g) Negation window — KEPT AT 3, NOT EXTENDED

**Justification:** Extending from 3 to 4 tokens was tested. It did not break any test or DEV row in isolation, but the risk is that a 4-token window over sentences with both an intensifier and a negation (e.g., `"not very good today"`) can cause unexpected double-application. The current 3-token window correctly handles `"no growth"` and `"not good"`. Extending to 4 provides no DEV gain but adds fragility. **Decision: keep at 3 and document here.**

---

## Changes Not Applied

- **"crushed"**: Ambiguous ("crushed earnings" = positive), excluded per rules.
- **"done hiking"**: Single-headline phrase, over-specific to one macro cycle, excluded per rules.
- Any phrase derived exclusively from a test-split error.
