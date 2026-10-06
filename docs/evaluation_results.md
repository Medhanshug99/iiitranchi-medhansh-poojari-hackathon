# ShockWire NLP Engine – Evaluation Results

**Date:** 2026-10-06 17:20:31  
**Rows:** 103 total (45 dev / 58 test)  
**Command:** `python -m src.evaluate`  

> ⚠️ **Protocol:** Tune lexicon/rules on **DEV only**. TEST numbers are the **final reported accuracy**. Never tune on TEST.

---

### DEV (45 rows)

#### Sentiment (45 rows)

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

**Confusion matrix (sentiment, 45 rows)**

| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 23       | 2       | 1        |
| neutral     | 0        | 10      | 0        |
| positive    | 2        | 1       | 6        |

#### Event Type (45 rows)

| Metric                       | Engine  | Majority baseline |
| ---------------------------- | ------- | ----------------- |
| Accuracy                     | 0.956   | 0.156             |
| Macro-F1                     | 0.957   | —                 |
| Gain over best baseline (pp) | +80.0pp | —                 |

| Class              | Precision | Recall | F1    | Support |
| ------------------ | --------- | ------ | ----- | ------- |
| Credit Event       | 1.000     | 1.000  | 1.000 | 1       |
| Cyber/Operational  | 1.000     | 0.800  | 0.889 | 5       |
| Earnings           | 1.000     | 1.000  | 1.000 | 7       |
| Geopolitical       | 0.857     | 1.000  | 0.923 | 6       |
| Macroeconomic      | 1.000     | 1.000  | 1.000 | 7       |
| Merger/Acquisition | 1.000     | 1.000  | 1.000 | 4       |
| Other              | 0.800     | 1.000  | 0.889 | 4       |
| Product Launch     | 1.000     | 0.833  | 0.909 | 6       |
| Regulatory/Legal   | 1.000     | 1.000  | 1.000 | 5       |

**Confusion matrix (event type, 45 rows)**

| true \ pred        | Credit Event | Cyber/Operational | Earnings | Geopolitical | Macroeconomic | Merger/Acquisition | Other | Product Launch | Regulatory/Legal |
| ------------------ | ------------ | ----------------- | -------- | ------------ | ------------- | ------------------ | ----- | -------------- | ---------------- |
| Credit Event       | 1            | 0                 | 0        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Cyber/Operational  | 0            | 4                 | 0        | 1            | 0             | 0                  | 0     | 0              | 0                |
| Earnings           | 0            | 0                 | 7        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Geopolitical       | 0            | 0                 | 0        | 6            | 0             | 0                  | 0     | 0              | 0                |
| Macroeconomic      | 0            | 0                 | 0        | 0            | 7             | 0                  | 0     | 0              | 0                |
| Merger/Acquisition | 0            | 0                 | 0        | 0            | 0             | 4                  | 0     | 0              | 0                |
| Other              | 0            | 0                 | 0        | 0            | 0             | 0                  | 4     | 0              | 0                |
| Product Launch     | 0            | 0                 | 0        | 0            | 0             | 0                  | 1     | 5              | 0                |
| Regulatory/Legal   | 0            | 0                 | 0        | 0            | 0             | 0                  | 0     | 0              | 5                |

---

### TEST (58 rows)

#### Sentiment (58 rows)

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

**Confusion matrix (sentiment, 58 rows)**

| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 16       | 4       | 0        |
| neutral     | 0        | 15      | 2        |
| positive    | 2        | 7       | 12       |

#### Event Type (58 rows)

| Metric                       | Engine  | Majority baseline |
| ---------------------------- | ------- | ----------------- |
| Accuracy                     | 1.000   | 0.172             |
| Macro-F1                     | 1.000   | —                 |
| Gain over best baseline (pp) | +82.8pp | —                 |

| Class              | Precision | Recall | F1    | Support |
| ------------------ | --------- | ------ | ----- | ------- |
| Credit Event       | 1.000     | 1.000  | 1.000 | 10      |
| Cyber/Operational  | 1.000     | 1.000  | 1.000 | 6       |
| Earnings           | 1.000     | 1.000  | 1.000 | 6       |
| Geopolitical       | 1.000     | 1.000  | 1.000 | 5       |
| Macroeconomic      | 1.000     | 1.000  | 1.000 | 4       |
| Merger/Acquisition | 1.000     | 1.000  | 1.000 | 7       |
| Other              | 1.000     | 1.000  | 1.000 | 8       |
| Product Launch     | 1.000     | 1.000  | 1.000 | 5       |
| Regulatory/Legal   | 1.000     | 1.000  | 1.000 | 7       |

**Confusion matrix (event type, 58 rows)**

| true \ pred        | Credit Event | Cyber/Operational | Earnings | Geopolitical | Macroeconomic | Merger/Acquisition | Other | Product Launch | Regulatory/Legal |
| ------------------ | ------------ | ----------------- | -------- | ------------ | ------------- | ------------------ | ----- | -------------- | ---------------- |
| Credit Event       | 10           | 0                 | 0        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Cyber/Operational  | 0            | 6                 | 0        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Earnings           | 0            | 0                 | 6        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Geopolitical       | 0            | 0                 | 0        | 5            | 0             | 0                  | 0     | 0              | 0                |
| Macroeconomic      | 0            | 0                 | 0        | 0            | 4             | 0                  | 0     | 0              | 0                |
| Merger/Acquisition | 0            | 0                 | 0        | 0            | 0             | 7                  | 0     | 0              | 0                |
| Other              | 0            | 0                 | 0        | 0            | 0             | 0                  | 8     | 0              | 0                |
| Product Launch     | 0            | 0                 | 0        | 0            | 0             | 0                  | 0     | 5              | 0                |
| Regulatory/Legal   | 0            | 0                 | 0        | 0            | 0             | 0                  | 0     | 0              | 7                |

---

### ALL (103 rows)

#### Sentiment (103 rows)

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

**Confusion matrix (sentiment, 103 rows)**

| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 39       | 6       | 1        |
| neutral     | 0        | 25      | 2        |
| positive    | 4        | 8       | 18       |

#### Event Type (103 rows)

| Metric                       | Engine  | Majority baseline |
| ---------------------------- | ------- | ----------------- |
| Accuracy                     | 0.981   | 0.126             |
| Macro-F1                     | 0.980   | —                 |
| Gain over best baseline (pp) | +85.4pp | —                 |

| Class              | Precision | Recall | F1    | Support |
| ------------------ | --------- | ------ | ----- | ------- |
| Credit Event       | 1.000     | 1.000  | 1.000 | 11      |
| Cyber/Operational  | 1.000     | 0.909  | 0.952 | 11      |
| Earnings           | 1.000     | 1.000  | 1.000 | 13      |
| Geopolitical       | 0.917     | 1.000  | 0.957 | 11      |
| Macroeconomic      | 1.000     | 1.000  | 1.000 | 11      |
| Merger/Acquisition | 1.000     | 1.000  | 1.000 | 11      |
| Other              | 0.923     | 1.000  | 0.960 | 12      |
| Product Launch     | 1.000     | 0.909  | 0.952 | 11      |
| Regulatory/Legal   | 1.000     | 1.000  | 1.000 | 12      |

**Confusion matrix (event type, 103 rows)**

| true \ pred        | Credit Event | Cyber/Operational | Earnings | Geopolitical | Macroeconomic | Merger/Acquisition | Other | Product Launch | Regulatory/Legal |
| ------------------ | ------------ | ----------------- | -------- | ------------ | ------------- | ------------------ | ----- | -------------- | ---------------- |
| Credit Event       | 11           | 0                 | 0        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Cyber/Operational  | 0            | 10                | 0        | 1            | 0             | 0                  | 0     | 0              | 0                |
| Earnings           | 0            | 0                 | 13       | 0            | 0             | 0                  | 0     | 0              | 0                |
| Geopolitical       | 0            | 0                 | 0        | 11           | 0             | 0                  | 0     | 0              | 0                |
| Macroeconomic      | 0            | 0                 | 0        | 0            | 11            | 0                  | 0     | 0              | 0                |
| Merger/Acquisition | 0            | 0                 | 0        | 0            | 0             | 11                 | 0     | 0              | 0                |
| Other              | 0            | 0                 | 0        | 0            | 0             | 0                  | 12    | 0              | 0                |
| Product Launch     | 0            | 0                 | 0        | 0            | 0             | 0                  | 1     | 10             | 0                |
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
- **id=E001** [SENT]
  - Text: *Missile strikes hit oil terminal in Gulf shipping lane, crude jumps 6% as tanker traffic halts*
  - Sentiment: true=`negative` pred=`neutral`
  - Matched terms: ['strikes', 'jumps', 'halts']
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

## Round 2 Tuning Log

**Note:** Holdout #1 (data/labeled_holdout.csv) was used for Round-2 tuning and thus became part of the development pool. A second, fresh holdout dataset will be used for the final, independent estimate. 

### Before Round 2 (Holdout #1 Baseline)
* **Sentiment Accuracy**: 68.9%
* **Event Type Accuracy**: 53.3%

### Changes Implemented
1. **Broadened Event Vocabulary & Regexes**
   * **Change:** Added standard newswire vocabulary per class (e.g. efinanc, extends maturity, peace talks, system upgrade, 
et income, unsolicited proposal).
   * **Justification:** (a) It is standard newswire vocabulary for those classes. (b) It fixes multiple fall-throughs to "Other".
   * **Effect:** Greatly improved Event Type recall for specific classes, raising holdout #1 event accuracy from 53.3% to 91.1%.
2. **Lower Minimum Score & Tie-break for Event Classification**
   * **Change:** Reduced 	op < 2.0 threshold to 1.5 and used EVENT_SEVERITY for tie-breaking.
   * **Justification:** (b) Fixes multiple development rows that fell through to "Other" due to weak signal weights.
   * **Effect:** Allowed correctly mapped, albeit lower-weighted cues, to win out over the generic "Other".
3. **Domain-Direction Flips for Sentiment**
   * **Change:** Flipped "surge/jump/climb/spike" to negative when appearing near inflation, yields, claims, costs, losses; flipped "cut/slash" to positive for costs, rates, inflation.
   * **Justification:** (a) Standard newswire knowledge (e.g. spiking inflation is bad). (b) Fixed multiple rows in DEV (e.g. H006, H009).
   * **Effect:** Sentiment accuracy increased from 68.9% to 71.1% on the development pool.
4. **Neutral Process Cues Expansion**
   * **Change:** Added "consults", "convenes", "discussions", "names", "appoints", "completes review" to NEUTRAL_CUES.
   * **Justification:** (a) Standard newswire vocabulary for routine/neutral corporate announcements.
   * **Effect:** Reduced false positives/negatives on purely administrative updates.

### After Round 2 (Holdout #1 / Development Pool Results)
* **Sentiment Accuracy**: 71.1%
* **Event Type Accuracy**: 91.1%
