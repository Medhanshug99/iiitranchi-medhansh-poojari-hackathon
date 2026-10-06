# ShockWire NLP Engine – Evaluation Results

## 1. Method and split
- **Date:** 2026-10-06 (after tuning)
- **Rows:** 103 total (45 dev / 58 test) + 45 fresh holdout rows
- **Command:** python -m src.evaluate
- **Protocol:** Tune lexicon/rules on **DEV only**. The test split was used for final verification. A fresh holdout set was evaluated exactly once with no further tuning.

## 2. Baseline vs Tuned on DEV and TEST (corrected tables)

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

## 3. Tuning Log

All changes are in src/riskengine/lexicon.py and src/riskengine/nlp.py. No test-split rows were examined to decide these changes. Each change is justified by a DEV error pattern or general finance-newswire vocabulary knowledge.

### (a) Inflection normaliser — KEPT
**Justification (DEV evidence):** E024 (downgrades scored 0), E068 (ines not in lexicon). Many surface forms of lexicon words were missed entirely.
**Implementation:** 
lp._build_normaliser() generates an EXTENDED_LEXICON at import time by appending s, es, ed, ing, d and consonant-doubling / trailing-e variants for every canonical lexicon entry. Explicit entries are never overwritten.
**DEV effect:** Fixed downgrades (now negative), ines (now negative). No DEV row regressed.

### (b) Analyst-downgrade gate — KEPT
**Justification (DEV evidence):** E101 — broker stock downgrade to underperform was classified as Credit Event because the downgrad rule fired without any debt/rating context.
**Implementation:** In classify_event(), if Credit Event wins solely via the downgrad rule, require at least one context word from CREDIT_DOWNGRADE_CONTEXT to match at a word boundary. If absent, suppress to second-best or Other.
**DEV effect:** E101 now correctly classified as Other. Rating-agency downgrades with debt/rating context still correctly fire as Credit Event.

### (c) Broadened event-rule vocabulary — KEPT
**Justification (DEV evidence + general finance vocabulary):** E007/E008/E009 (Geopolitical), E014/E019/E022 (Macroeconomic), E042 (M&A), E049 (Product Launch), E063/E064 (Earnings), E082 (Cyber/Operational). Each event class was missing standard newswire vocabulary.
**DEV effect:** Event accuracy DEV: 0.778 → 0.933. No DEV event-class recall dropped > 0.05.

### (d) Sentiment lexicon additions — KEPT
**Justification (DEV evidence):** E050 (impressive absent → neutral), E051 (disappoints/lukewarm absent), E067 (profit warning phrase cancels to zero), E006 (	hreatens too weak).
**DEV effect:** E050, E051 (sentiment), E067 now correctly negative. E006 now correctly negative. No DEV row regressed.

### (e) Aversion context for "default" and "attack" — KEPT
**Justification (DEV evidence):** E021 context — verting default should be positive not negative. 	hwarts attack similarly.
**Implementation:** AVERSION_CONTEXT dict maps trigger words (default, ttack) to a set of prevention verbs. In score_sentiment(), if a negative trigger is found and any prevention verb appears in the preceding 6-token window, the token's negative weight is skipped.
**DEV effect:** Improves sentences where bad events are averted. No DEV row regressed.

### (f) Neutral cues — KEPT
**Justification (DEV evidence):** E019 (Retail sales rise 0.1% in line with economists' forecasts) classified positive due to ise, despite being a routine, zero-surprise event. (Note: E018 was actually the row with this text).
**Implementation:** NEUTRAL_CUES list (in line with, unchanged, lat, scheduled, 	o report, will hold, 
o change, s expected, in-line). When any cue is found, raw score is multiplied by NEUTRAL_SHRINK = 0.3 before normalisation.
**DEV effect:** Shrinks borderline positive/negative to neutral for routine items.

### (g) Negation window — KEPT AT 3, NOT EXTENDED
**Justification:** Extending from 3 to 4 tokens was tested but adds fragility for sentences with both intensifier and negation. Decision: keep at 3.

## 4. Final Holdout Results
Tested on 45 unseen rows exactly once, with no tuning afterwards.

### Sentiment (45 rows)
| Metric                       | Engine  | Majority baseline | Always-neutral baseline |
| ---------------------------- | ------- | ----------------- | ----------------------- |
| Accuracy                     | 0.689   | 0.444             | 0.267                   |
| Macro-F1                     | 0.681   | —                 | —                       |

| Class    | Precision | Recall | F1    | Support |
| -------- | --------- | ------ | ----- | ------- |
| negative | 0.812     | 0.650  | 0.722 | 20      |
| neutral  | 0.600     | 0.750  | 0.667 | 12      |
| positive | 0.643     | 0.692  | 0.667 | 13      |

**Confusion matrix (sentiment, 45 rows)**
| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 13       | 4       | 3        |
| neutral     | 1        | 9       | 2        |
| positive    | 2        | 2       | 9        |

### Event Type (45 rows)
| Metric                       | Engine  | Majority baseline |
| ---------------------------- | ------- | ----------------- |
| Accuracy                     | 0.533   | 0.111             |
| Macro-F1                     | 0.576   | —                 |

| Class              | Precision | Recall | F1    | Support |
| ------------------ | --------- | ------ | ----- | ------- |
| Credit Event       | 1.000     | 0.400  | 0.571 | 5       |
| Cyber/Operational  | 1.000     | 0.200  | 0.333 | 5       |
| Earnings           | 0.750     | 0.600  | 0.667 | 5       |
| Geopolitical       | 1.000     | 0.600  | 0.750 | 5       |
| Macroeconomic      | 0.667     | 0.400  | 0.500 | 5       |
| Merger/Acquisition | 1.000     | 0.600  | 0.750 | 5       |
| Other              | 0.217     | 1.000  | 0.357 | 5       |
| Product Launch     | 1.000     | 0.600  | 0.750 | 5       |
| Regulatory/Legal   | 1.000     | 0.400  | 0.571 | 5       |

**Confusion matrix (event type, 45 rows)**
| true \ pred        | Credit Event | Cyber/Operational | Earnings | Geopolitical | Macroeconomic | Merger/Acquisition | Other | Product Launch | Regulatory/Legal |
| ------------------ | ------------ | ----------------- | -------- | ------------ | ------------- | ------------------ | ----- | -------------- | ---------------- |
| Credit Event       | 2            | 0                 | 0        | 0            | 1             | 0                  | 2     | 0              | 0                |
| Cyber/Operational  | 0            | 1                 | 0        | 0            | 0             | 0                  | 4     | 0              | 0                |
| Earnings           | 0            | 0                 | 3        | 0            | 0             | 0                  | 2     | 0              | 0                |
| Geopolitical       | 0            | 0                 | 0        | 3            | 0             | 0                  | 2     | 0              | 0                |
| Macroeconomic      | 0            | 0                 | 1        | 0            | 2             | 0                  | 2     | 0              | 0                |
| Merger/Acquisition | 0            | 0                 | 0        | 0            | 0             | 3                  | 2     | 0              | 0                |
| Other              | 0            | 0                 | 0        | 0            | 0             | 0                  | 5     | 0              | 0                |
| Product Launch     | 0            | 0                 | 1        | 0            | 0             | 0                  | 1     | 3              | 0                |
| Regulatory/Legal   | 0            | 0                 | 0        | 0            | 0             | 0                  | 3     | 0              | 2                |

### Misclassified Holdout Rows
- **H012 [EVT]**: *Lender halts withdrawals...* | true=Credit Event, pred=Macroeconomic (Matched: ['halts'])
- **H013 [SENT] [EVT]**: *Shipping firm refinances...* | Sent: true=positive, pred=
eutral | Evt: true=Credit Event, pred=Other (Matched: [])
- **H014 [EVT]**: *Company extends maturity of its revolving credit facility...* | Evt: true=Credit Event, pred=Other (Matched: [])
- **H015 [SENT]**: *Their bonds are trading at 60 cents...* | Sent: true=
egative, pred=
eutral (Matched: [])
- **H037 [SENT] [EVT]**: *Retailer says scheduled system upgrade...* | Sent: true=
eutral, pred=positive | Evt: true=Cyber/Operational, pred=Other (Matched: ['upgrade'])
- **H038 [EVT]**: *Refinery shutdown after pipeline leak...* | Evt: true=Cyber/Operational, pred=Other (Matched: ['shutdown', 'cuts'])
- **H039 [SENT] [EVT]**: *Airline resumes full schedule after technology glitch...* | Sent: true=positive, pred=
eutral | Evt: true=Cyber/Operational, pred=Other (Matched: [])
- **H040 [EVT]**: *Trading platform froze again during the open...* | Evt: true=Cyber/Operational, pred=Other (Matched: ['lost'])
- **H026 [EVT]**: *Chip equipment maker's third-quarter net income jumps...* | Evt: true=Earnings, pred=Other (Matched: ['jumps', 'strong', 'demand'])
- **H028 [EVT]**: *Conglomerate says quarterly sales were broadly flat...* | Evt: true=Earnings, pred=Other (Matched: [])
- **H003 [EVT]**: *Peace talks yield breakthrough as rival factions agree...* | Evt: true=Geopolitical, pred=Other (Matched: ['breakthrough'])
- **H005 [EVT]**: *Thread: why the escalation near the strait should worry...* | Evt: true=Geopolitical, pred=Other (Matched: ['escalation', 'worry'])
- **H006 [SENT]**: *Producer prices surge 1.4% in September... stoking fears...* | Sent: true=
egative, pred=positive (Matched: ['surge', 'fears'])
- **H007 [EVT]**: *Euro zone growth beats expectations as services activity rebounds* | Evt: true=Macroeconomic, pred=Earnings (Matched: ['growth', 'beats', 'rebounds'])
- **H008 [EVT]**: *Bank of Japan holds policy rate at 0.1%...* | Evt: true=Macroeconomic, pred=Other (Matched: [])
- **H009 [SENT] [EVT]**: *US jobless claims climb... labour market cooling fast* | Sent: true=
egative, pred=
eutral | Evt: true=Macroeconomic, pred=Other (Matched: [])
- **H010 [SENT]**: *CPI came in soft, yields are dropping, risk-on today...* | Sent: true=positive, pred=
eutral (Matched: ['dropping', 'good'])
- **H016 [EVT]**: *Pharma group to buy biotech for .5bn...* | Evt: true=Merger/Acquisition, pred=Other (Matched: ['buy'])
- **H018 [EVT]**: *Board of the media company reviews unsolicited proposal...* | Evt: true=Merger/Acquisition, pred=Other (Matched: [])
- **H019 [SENT]**: *Retailer finalises acquisition of rival chain... expects  annual cost savings* | Sent: true=positive, pred=
eutral (Matched: [])
- **H043 [SENT]**: *Executive team shake-up as two senior officers resign...* | Sent: true=
egative, pred=
eutral (Matched: [])
- **H022 [EVT]**: *Rollout of new payments app stumbles... users report crashes...* | Evt: true=Product Launch, pred=Earnings (Matched: ['crashes'])
- **H024 [SENT]**: *Social network debuts creator tools that analysts say could lift ad revenue* | Sent: true=positive, pred=
eutral (Matched: [])
- **H025 [EVT]**: *Just tried the new update from the app. Smoother and way faster. Good release.* | Evt: true=Product Launch, pred=Other (Matched: ['good'])
- **H031 [SENT] [EVT]**: *Watchdog sues exchange operator for alleged market manipulation* | Sent: true=
egative, pred=
eutral | Evt: true=Regulatory/Legal, pred=Other (Matched: [])
- **H032 [SENT] [EVT]**: *Judge throws out shareholder suit... saying claims lacked merit* | Sent: true=positive, pred=
eutral | Evt: true=Regulatory/Legal, pred=Other (Matched: [])
- **H033 [EVT]**: *Finance ministry circulates draft rules on crypto custody...* | Evt: true=Regulatory/Legal, pred=Other (Matched: [])
- **H034 [SENT]**: *Insurer ordered to pay  in settlement over mis-sold policies* | Sent: true=
egative, pred=
eutral (Matched: [])
- **H035 [SENT]**: *New capital rules for banks are going to squeeze lending. Regulators love moving goalposts.* | Sent: true=
egative, pred=positive (Matched: ['love'])

## 5. Known Limitations
- **Test set contamination**: The test split was inspected at baseline so its post-tuning numbers are not fully independent.
- **Small sample sizes**: Accuracy moves about 2 points per row on the 58 test rows, and 2.2 points per row on the 45-row holdout.
- **Data skew**: There are only 12 social rows in the main dataset.
- **Asymmetric sentiment errors**: Positives are sometimes predicted neutral due to lack of strong sentiment words in some positive financial actions.
- **Algorithm limits**: The word-list model has no understanding of sarcasm, irony, or long-range context.