# ShockWire NLP Engine – Evaluation Results

**Date:** 2026-10-16 10:23:40  
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

## Final independent holdout (holdout #2)

**45 rows, completely unseen during all development and tuning. Evaluated exactly once; no tuning afterwards.**

### How to read these numbers

- **Holdout #1** (data/labeled_holdout.csv, 45 rows) was used as development data for Round 2 tuning. Its accuracy numbers are therefore **not independent**.
- **The TEST split** of the 103-row main set (data/labeled_eval.csv, 58 rows) was inspected at baseline, so its post-tuning numbers are **not independent** either.
- **Holdout #2** (data/labeled_holdout2.csv, 45 rows) is the **only fully independent estimate**. It was never seen by the developer until evaluation.
- With 45 rows, each row is worth about 2.2 percentage points of accuracy, so small-sample noise is substantial.

---

### HOLDOUT #2 (45 rows)

#### Sentiment (45 rows)

| Metric                       | Engine  | Majority baseline | Always-neutral baseline |
| ---------------------------- | ------- | ----------------- | ----------------------- |
| Accuracy                     | 0.622   | 0.444             | 0.267                   |
| Macro-F1                     | 0.624   | —                 | —                       |
| Gain over best baseline (pp) | +17.8pp | —                 | —                       |

| Class    | Precision | Recall | F1    | Support |
| -------- | --------- | ------ | ----- | ------- |
| negative | 0.909     | 0.500  | 0.645 | 20      |
| neutral  | 0.455     | 0.833  | 0.588 | 12      |
| positive | 0.667     | 0.615  | 0.640 | 13      |

**Confusion matrix (sentiment, 45 rows)**

| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 10       | 7       | 3        |
| neutral     | 1        | 10      | 1        |
| positive    | 0        | 5       | 8        |

#### Event Type (45 rows)

| Metric                       | Engine  | Majority baseline |
| ---------------------------- | ------- | ----------------- |
| Accuracy                     | 0.622   | 0.111             |
| Macro-F1                     | 0.658   | —                 |
| Gain over best baseline (pp) | +51.1pp | —                 |

| Class              | Precision | Recall | F1    | Support |
| ------------------ | --------- | ------ | ----- | ------- |
| Credit Event       | 1.000     | 0.800  | 0.889 | 5       |
| Cyber/Operational  | 0.500     | 0.200  | 0.286 | 5       |
| Earnings           | 1.000     | 0.800  | 0.889 | 5       |
| Geopolitical       | 1.000     | 0.600  | 0.750 | 5       |
| Macroeconomic      | 0.667     | 0.400  | 0.500 | 5       |
| Merger/Acquisition | 1.000     | 0.400  | 0.571 | 5       |
| Other              | 0.250     | 1.000  | 0.400 | 5       |
| Product Launch     | 1.000     | 0.600  | 0.750 | 5       |
| Regulatory/Legal   | 1.000     | 0.800  | 0.889 | 5       |

**Confusion matrix (event type, 45 rows)**

| true \ pred        | Credit Event | Cyber/Operational | Earnings | Geopolitical | Macroeconomic | Merger/Acquisition | Other | Product Launch | Regulatory/Legal |
| ------------------ | ------------ | ----------------- | -------- | ------------ | ------------- | ------------------ | ----- | -------------- | ---------------- |
| Credit Event       | 4            | 0                 | 0        | 0            | 0             | 0                  | 1     | 0              | 0                |
| Cyber/Operational  | 0            | 1                 | 0        | 0            | 0             | 0                  | 4     | 0              | 0                |
| Earnings           | 0            | 1                 | 4        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Geopolitical       | 0            | 0                 | 0        | 3            | 0             | 0                  | 2     | 0              | 0                |
| Macroeconomic      | 0            | 0                 | 0        | 0            | 2             | 0                  | 3     | 0              | 0                |
| Merger/Acquisition | 0            | 0                 | 0        | 0            | 0             | 2                  | 3     | 0              | 0                |
| Other              | 0            | 0                 | 0        | 0            | 0             | 0                  | 5     | 0              | 0                |
| Product Launch     | 0            | 0                 | 0        | 0            | 0             | 0                  | 2     | 3              | 0                |
| Regulatory/Legal   | 0            | 0                 | 0        | 0            | 1             | 0                  | 0     | 0              | 4                |

---

### Error Analysis: HOLDOUT #2 misclassifications

- **id=G011** [SENT] [EVT]
  - Text: *Property group fails to repay maturing notes, trustees demand immediate payment*
  - Sentiment: true=`negative` pred=`positive` — "demand" is keyed as positive (demand for product); here it means a legal demand, which the lexicon cannot distinguish.
  - Event: true=`Credit Event` pred=`Other` — no credit-event keyword matched; "fails to repay" is not in the vocabulary.
- **id=G014** [SENT]
  - Text: *Utility sells $1bn of ten-year bonds to refinance existing debt*
  - Sentiment: true=`neutral` pred=`negative` — "sells" is negative in the lexicon; in debt-issuance context it is neutral. Contextual flip needed.
- **id=G036** [SENT]
  - Text: *Hackers steal customer data from payments processor, regulators demand answers*
  - Sentiment: true=`negative` pred=`positive` — same "demand" mismatch as G011; "steal" is not in the lexicon.
- **id=G037** [EVT]
  - Text: *Exchange says it will suspend trading for a short technical test on Saturday*
  - Event: true=`Cyber/Operational` pred=`Other` — no cyber/operational keyword matched; "suspend trading" is not in the vocabulary.
- **id=G038** [EVT]
  - Text: *Warehouse fire halts distribution for the retailer ahead of peak season*
  - Event: true=`Cyber/Operational` pred=`Other` — "halts" matched but mapped to Geopolitical; physical-event vocabulary is missing for Cyber/Operational.
- **id=G039** [SENT] [EVT]
  - Text: *Bank completes migration to new core system with no service disruption*
  - Sentiment: true=`positive` pred=`neutral` — no positive keyword matched; "completes migration" is not in the lexicon.
  - Event: true=`Cyber/Operational` pred=`Other` — "migration" and "core system" are not in the event vocabulary.
- **id=G040** [SENT] [EVT]
  - Text: *Mobile banking has been down since this morning. Can't pay anything. Awful.*
  - Sentiment: true=`negative` pred=`neutral` — "Awful" and "down" are not in the lexicon.
  - Event: true=`Cyber/Operational` pred=`Other` — no cyber/operational keyword matched; informal language misses the rules.
- **id=G029** [EVT]
  - Text: *Automaker's operating profit slumps 40% as price cuts and recall costs weigh*
  - Event: true=`Earnings` pred=`Cyber/Operational` — "recall" matched Cyber/Operational; "profit slumps" was not strong enough for Earnings to win.
- **id=G001** [SENT]
  - Text: *Airstrikes hit port facilities as the conflict widens, shipping insurers raise war-risk premiums*
  - Sentiment: true=`negative` pred=`neutral` — "raise" is positive in the lexicon; it cancelled out the negative direction-flip context. "Airstrikes" is not in the lexicon.
- **id=G003** [EVT]
  - Text: *Rival governments sign pact to reopen the main trade corridor, shipping stocks rise*
  - Event: true=`Geopolitical` pred=`Other` — "pact" and "trade corridor" are not in the event vocabulary.
- **id=G004** [SENT] [EVT]
  - Text: *Government freezes foreign assets and expels diplomats as dispute over contested waters deepens*
  - Sentiment: true=`negative` pred=`neutral` — "freezes", "expels" not in the lexicon.
  - Event: true=`Geopolitical` pred=`Other` — "diplomats", "contested waters" are not in the event vocabulary.
- **id=G006** [SENT]
  - Text: *Core inflation reaccelerates to 5.8%, leaving the central bank no room to cut*
  - Sentiment: true=`negative` pred=`neutral` — "inflation" and "cut" matched but "cut" flipped positive (cost-cutting context); net score was too close to zero.
- **id=G007** [EVT]
  - Text: *Hiring surges as employers add 310,000 jobs, wage growth stays moderate*
  - Event: true=`Macroeconomic` pred=`Other` — "surges" matched but scored higher for another class; "hiring" and "jobs" are not in the vocabulary.
- **id=G009** [EVT]
  - Text: *Housing starts collapse 18% as mortgage costs climb, builders warn of a slump*
  - Event: true=`Macroeconomic` pred=`Other` — "housing starts", "mortgage" are not in the event vocabulary.
- **id=G010** [EVT]
  - Text: *Waiting on the rate decision at 2pm. Positioning light, nothing to do until then.*
  - Event: true=`Macroeconomic` pred=`Other` — "rate decision" is too informal/indirect; no keyword matched.
- **id=G016** [SENT]
  - Text: *Software firm agrees to be taken private in $11bn leveraged buyout*
  - Sentiment: true=`positive` pred=`neutral` — "leveraged buyout" is not in the lexicon; no positive keyword matched.
- **id=G017** [EVT]
  - Text: *Bidder withdraws offer for rival grocer after shareholder opposition, shares drop*
  - Event: true=`Merger/Acquisition` pred=`Other` — "withdraws offer" is not in the event vocabulary; "drop" matched but not for M&A.
- **id=G018** [EVT]
  - Text: *Two shipping lines confirm they are in preliminary discussions about combining operations*
  - Event: true=`Merger/Acquisition` pred=`Other` — "combining operations" and "preliminary discussions" are not in the event vocabulary.
- **id=G019** [SENT] [EVT]
  - Text: *Chemical maker completes sale of its coatings unit at a higher price than analysts expected*
  - Sentiment: true=`positive` pred=`neutral` — no positive keyword matched; "completes sale" is not in the lexicon.
  - Event: true=`Merger/Acquisition` pred=`Other` — "sale of its … unit" is a divestiture; not in the vocabulary.
- **id=G042** [SENT]
  - Text: *Insurer lifts shareholder payout and announces a $3bn share repurchase*
  - Sentiment: true=`positive` pred=`neutral` — "lifts" and "repurchase" are not in the lexicon.
- **id=G043** [SENT]
  - Text: *Founder resigns from the board after a dispute with management*
  - Sentiment: true=`negative` pred=`neutral` — "resigns" and "dispute" are not in the lexicon.
- **id=G022** [SENT]
  - Text: *Launch of delivery drone service postponed after safety testing setbacks*
  - Sentiment: true=`negative` pred=`positive` — "launch" is keyed as positive; "postponed" and "setbacks" are not in the lexicon to counteract it.
- **id=G023** [SENT] [EVT]
  - Text: *Cloud company expands its AI toolkit with new developer features*
  - Sentiment: true=`neutral` pred=`positive` — "expands" is positive in the lexicon; in a product announcement context it is neutral.
  - Event: true=`Product Launch` pred=`Other` — "AI toolkit" and "developer features" are not in the event vocabulary.
- **id=G024** [EVT]
  - Text: *Beverage group's new zero-sugar range tops supermarket sales charts in first month*
  - Event: true=`Product Launch` pred=`Other` — "zero-sugar range" and "sales charts" are not in the event vocabulary.
- **id=G025** [SENT]
  - Text: *The new release is full of bugs. Rolled back to the old version, wasted my morning.*
  - Sentiment: true=`negative` pred=`neutral` — informal language; "bugs", "wasted" are not in the lexicon.
- **id=G032** [SENT]
  - Text: *Competition authority closes probe into the grocer, finding no breach of rules*
  - Sentiment: true=`positive` pred=`neutral` — "probe" and "breach" are negative in the lexicon; "finding no breach" is a positive outcome but the negation is not handled.
- **id=G033** [EVT]
  - Text: *Central bank consults on updated disclosure requirements for listed lenders*
  - Event: true=`Regulatory/Legal` pred=`Macroeconomic` — "central bank" matched Macroeconomic; "disclosure requirements" is not in the Regulatory vocabulary.
- **id=G034** [SENT]
  - Text: *Court rules against the pharmaceutical maker in patent case, ordering $500m in damages*
  - Sentiment: true=`negative` pred=`neutral` — "rules against" and "damages" (legal sense) are not in the lexicon.
