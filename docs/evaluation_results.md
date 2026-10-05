# ShockWire NLP Engine – Evaluation Results

**Date:** 2026-10-05 17:32:16  
**Rows:** 103 total (45 dev / 58 test)  
**Command:** `python -m src.evaluate`  

> ⚠️ **Protocol:** Tune lexicon/rules on **DEV only**. TEST numbers are the **final reported accuracy**. Never tune on TEST.

---

### DEV (45 rows)

#### Sentiment

| Metric                       | Engine  | Majority baseline | Always-neutral baseline |
| ---------------------------- | ------- | ----------------- | ----------------------- |
| Accuracy                     | 0.733   | 0.578             | 0.222                   |
| Macro-F1                     | 0.704   | —                 | —                       |
| Gain over best baseline (pp) | +15.6pp | —                 | —                       |

| Class    | Precision | Recall | F1    | Support |
| -------- | --------- | ------ | ----- | ------- |
| negative | 0.900     | 0.692  | 0.783 | 26      |
| neutral  | 0.588     | 1.000  | 0.741 | 10      |
| positive | 0.625     | 0.556  | 0.588 | 9       |

**Confusion matrix (sentiment)**

| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 18       | 5       | 3        |
| neutral     | 0        | 10      | 0        |
| positive    | 2        | 2       | 5        |

#### Event Type

| Metric                       | Engine  | Majority baseline |
| ---------------------------- | ------- | ----------------- |
| Accuracy                     | 0.644   | 0.156             |
| Macro-F1                     | 0.698   | —                 |
| Gain over best baseline (pp) | +48.9pp | —                 |

| Class              | Precision | Recall | F1    | Support |
| ------------------ | --------- | ------ | ----- | ------- |
| Credit Event       | 0.500     | 1.000  | 0.667 | 1       |
| Cyber/Operational  | 1.000     | 0.600  | 0.750 | 5       |
| Earnings           | 0.833     | 0.714  | 0.769 | 7       |
| Geopolitical       | 1.000     | 0.500  | 0.667 | 6       |
| Macroeconomic      | 1.000     | 0.571  | 0.727 | 7       |
| Merger/Acquisition | 1.000     | 0.750  | 0.857 | 4       |
| Other              | 0.176     | 0.750  | 0.286 | 4       |
| Product Launch     | 1.000     | 0.500  | 0.667 | 6       |
| Regulatory/Legal   | 1.000     | 0.800  | 0.889 | 5       |

**Confusion matrix (event type)**

| true \ pred        | Credit Event | Cyber/Operational | Earnings | Geopolitical | Macroeconomic | Merger/Acquisition | Other | Product Launch | Regulatory/Legal |
| ------------------ | ------------ | ----------------- | -------- | ------------ | ------------- | ------------------ | ----- | -------------- | ---------------- |
| Credit Event       | 1            | 0                 | 0        | 0            | 0             | 0                  | 0     | 0              | 0                |
| Cyber/Operational  | 0            | 3                 | 0        | 0            | 0             | 0                  | 2     | 0              | 0                |
| Earnings           | 0            | 0                 | 5        | 0            | 0             | 0                  | 2     | 0              | 0                |
| Geopolitical       | 0            | 0                 | 0        | 3            | 0             | 0                  | 3     | 0              | 0                |
| Macroeconomic      | 0            | 0                 | 1        | 0            | 4             | 0                  | 2     | 0              | 0                |
| Merger/Acquisition | 0            | 0                 | 0        | 0            | 0             | 3                  | 1     | 0              | 0                |
| Other              | 1            | 0                 | 0        | 0            | 0             | 0                  | 3     | 0              | 0                |
| Product Launch     | 0            | 0                 | 0        | 0            | 0             | 0                  | 3     | 3              | 0                |
| Regulatory/Legal   | 0            | 0                 | 0        | 0            | 0             | 0                  | 1     | 0              | 4                |

---

### TEST (58 rows)

#### Sentiment

| Metric                       | Engine  | Majority baseline | Always-neutral baseline |
| ---------------------------- | ------- | ----------------- | ----------------------- |
| Accuracy                     | 0.707   | 0.362             | 0.293                   |
| Macro-F1                     | 0.704   | —                 | —                       |
| Gain over best baseline (pp) | +34.5pp | —                 | —                       |

| Class    | Precision | Recall | F1    | Support |
| -------- | --------- | ------ | ----- | ------- |
| negative | 0.789     | 0.750  | 0.769 | 20      |
| neutral  | 0.600     | 0.882  | 0.714 | 17      |
| positive | 0.786     | 0.524  | 0.629 | 21      |

**Confusion matrix (sentiment)**

| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 15       | 4       | 1        |
| neutral     | 0        | 15      | 2        |
| positive    | 4        | 6       | 11       |

#### Event Type

| Metric                       | Engine  | Majority baseline |
| ---------------------------- | ------- | ----------------- |
| Accuracy                     | 0.655   | 0.172             |
| Macro-F1                     | 0.684   | —                 |
| Gain over best baseline (pp) | +48.3pp | —                 |

| Class              | Precision | Recall | F1    | Support |
| ------------------ | --------- | ------ | ----- | ------- |
| Credit Event       | 1.000     | 0.600  | 0.750 | 10      |
| Cyber/Operational  | 1.000     | 0.833  | 0.909 | 6       |
| Earnings           | 0.667     | 0.333  | 0.444 | 6       |
| Geopolitical       | 1.000     | 0.600  | 0.750 | 5       |
| Macroeconomic      | 1.000     | 0.750  | 0.857 | 4       |
| Merger/Acquisition | 1.000     | 0.857  | 0.923 | 7       |
| Other              | 0.308     | 1.000  | 0.471 | 8       |
| Product Launch     | 0.800     | 0.800  | 0.800 | 5       |
| Regulatory/Legal   | 1.000     | 0.143  | 0.250 | 7       |

**Confusion matrix (event type)**

| true \ pred        | Credit Event | Cyber/Operational | Earnings | Geopolitical | Macroeconomic | Merger/Acquisition | Other | Product Launch | Regulatory/Legal |
| ------------------ | ------------ | ----------------- | -------- | ------------ | ------------- | ------------------ | ----- | -------------- | ---------------- |
| Credit Event       | 6            | 0                 | 1        | 0            | 0             | 0                  | 3     | 0              | 0                |
| Cyber/Operational  | 0            | 5                 | 0        | 0            | 0             | 0                  | 1     | 0              | 0                |
| Earnings           | 0            | 0                 | 2        | 0            | 0             | 0                  | 4     | 0              | 0                |
| Geopolitical       | 0            | 0                 | 0        | 3            | 0             | 0                  | 2     | 0              | 0                |
| Macroeconomic      | 0            | 0                 | 0        | 0            | 3             | 0                  | 1     | 0              | 0                |
| Merger/Acquisition | 0            | 0                 | 0        | 0            | 0             | 6                  | 1     | 0              | 0                |
| Other              | 0            | 0                 | 0        | 0            | 0             | 0                  | 8     | 0              | 0                |
| Product Launch     | 0            | 0                 | 0        | 0            | 0             | 0                  | 1     | 4              | 0                |
| Regulatory/Legal   | 0            | 0                 | 0        | 0            | 0             | 0                  | 5     | 1              | 1                |

---

### ALL (103 rows)

#### Sentiment

| Metric                       | Engine  | Majority baseline | Always-neutral baseline |
| ---------------------------- | ------- | ----------------- | ----------------------- |
| Accuracy                     | 0.718   | 0.447             | 0.262                   |
| Macro-F1                     | 0.705   | —                 | —                       |
| Gain over best baseline (pp) | +27.2pp | —                 | —                       |

| Class    | Precision | Recall | F1    | Support |
| -------- | --------- | ------ | ----- | ------- |
| negative | 0.846     | 0.717  | 0.776 | 46      |
| neutral  | 0.595     | 0.926  | 0.725 | 27      |
| positive | 0.727     | 0.533  | 0.615 | 30      |

**Confusion matrix (sentiment)**

| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 33       | 9       | 4        |
| neutral     | 0        | 25      | 2        |
| positive    | 6        | 8       | 16       |

#### Event Type

| Metric                       | Engine  | Majority baseline |
| ---------------------------- | ------- | ----------------- |
| Accuracy                     | 0.650   | 0.126             |
| Macro-F1                     | 0.703   | —                 |
| Gain over best baseline (pp) | +52.4pp | —                 |

| Class              | Precision | Recall | F1    | Support |
| ------------------ | --------- | ------ | ----- | ------- |
| Credit Event       | 0.875     | 0.636  | 0.737 | 11      |
| Cyber/Operational  | 1.000     | 0.727  | 0.842 | 11      |
| Earnings           | 0.778     | 0.538  | 0.636 | 13      |
| Geopolitical       | 1.000     | 0.545  | 0.706 | 11      |
| Macroeconomic      | 1.000     | 0.636  | 0.778 | 11      |
| Merger/Acquisition | 1.000     | 0.818  | 0.900 | 11      |
| Other              | 0.256     | 0.917  | 0.400 | 12      |
| Product Launch     | 0.875     | 0.636  | 0.737 | 11      |
| Regulatory/Legal   | 1.000     | 0.417  | 0.588 | 12      |

**Confusion matrix (event type)**

| true \ pred        | Credit Event | Cyber/Operational | Earnings | Geopolitical | Macroeconomic | Merger/Acquisition | Other | Product Launch | Regulatory/Legal |
| ------------------ | ------------ | ----------------- | -------- | ------------ | ------------- | ------------------ | ----- | -------------- | ---------------- |
| Credit Event       | 7            | 0                 | 1        | 0            | 0             | 0                  | 3     | 0              | 0                |
| Cyber/Operational  | 0            | 8                 | 0        | 0            | 0             | 0                  | 3     | 0              | 0                |
| Earnings           | 0            | 0                 | 7        | 0            | 0             | 0                  | 6     | 0              | 0                |
| Geopolitical       | 0            | 0                 | 0        | 6            | 0             | 0                  | 5     | 0              | 0                |
| Macroeconomic      | 0            | 0                 | 1        | 0            | 7             | 0                  | 3     | 0              | 0                |
| Merger/Acquisition | 0            | 0                 | 0        | 0            | 0             | 9                  | 2     | 0              | 0                |
| Other              | 1            | 0                 | 0        | 0            | 0             | 0                  | 11    | 0              | 0                |
| Product Launch     | 0            | 0                 | 0        | 0            | 0             | 0                  | 4     | 7              | 0                |
| Regulatory/Legal   | 0            | 0                 | 0        | 0            | 0             | 0                  | 6     | 1              | 5                |

---

### Error Analysis: TEST misclassifications

- **id=E027** [EVT]
  - Text: *Rating agency upgrades airline's debt to investment grade on improved cash flow*
  - Event: true=`Credit Event` pred=`Other`
  - Matched terms: ['improved']
- **id=E028** [SENT]
  - Text: *Distressed lender secures rescue financing, averting default*
  - Sentiment: true=`positive` pred=`negative`
  - Matched terms: ['default']
- **id=E029** [EVT]
  - Text: *Rating agency affirms the utility's A- rating with a stable outlook*
  - Event: true=`Credit Event` pred=`Earnings`
  - Matched terms: []
- **id=E030** [EVT]
  - Text: *If that bank can't roll its debt we're looking at contagion. Spreads tell the story.*
  - Event: true=`Credit Event` pred=`Other`
  - Matched terms: ['contagion']
- **id=E032** [EVT]
  - Text: *Company prices $2bn senior notes offering due 2031*
  - Event: true=`Credit Event` pred=`Other`
  - Matched terms: []
- **id=E083** [SENT]
  - Text: *Systems fully restored after weekend outage, no data lost*
  - Sentiment: true=`positive` pred=`negative`
  - Matched terms: ['outage', 'lost']
- **id=E086** [EVT]
  - Text: *Exchange schedules planned maintenance for Saturday night*
  - Event: true=`Cyber/Operational` pred=`Other`
  - Matched terms: []
- **id=E089** [SENT]
  - Text: *Company thwarts attempted cyber attack, says operations unaffected*
  - Sentiment: true=`positive` pred=`negative`
  - Matched terms: ['attack']
- **id=E056** [EVT]
  - Text: *Bank reports quarterly profit of $3.2bn, beating estimates as lending income rises*
  - Event: true=`Earnings` pred=`Other`
  - Matched terms: ['profit', 'rises']
- **id=E058** [EVT]
  - Text: *Company to report third-quarter results on October 21 after the close*
  - Event: true=`Earnings` pred=`Other`
  - Matched terms: []
- **id=E060** [EVT]
  - Text: *Oil major posts record annual profit and raises dividend*
  - Event: true=`Earnings` pred=`Other`
  - Matched terms: ['record', 'profit', 'raises', 'dividend']
- **id=E102** [EVT]
  - Text: *Results were not as bad as feared, shares rebound*
  - Event: true=`Earnings` pred=`Other`
  - Matched terms: ['bad', 'rebound']
- **id=E001** [SENT]
  - Text: *Missile strikes hit oil terminal in Gulf shipping lane, crude jumps 6% as tanker traffic halts*
  - Sentiment: true=`negative` pred=`positive`
  - Matched terms: ['jumps', 'halts']
- **id=E002** [EVT]
  - Text: *Border clashes escalate between two nuclear-armed neighbours, global equities retreat*
  - Event: true=`Geopolitical` pred=`Other`
  - Matched terms: ['escalate']
- **id=E005** [EVT]
  - Text: *Foreign ministers to meet next week to discuss regional security arrangements*
  - Event: true=`Geopolitical` pred=`Other`
  - Matched terms: []
- **id=E017** [SENT]
  - Text: *Consumer price growth cools more than expected, boosting hopes of rate cuts*
  - Sentiment: true=`positive` pred=`neutral`
  - Matched terms: ['growth', 'cuts']
- **id=E018** [SENT] [EVT]
  - Text: *Retail sales rise 0.1% in line with economists' forecasts*
  - Sentiment: true=`neutral` pred=`positive`
  - Event: true=`Macroeconomic` pred=`Other`
  - Matched terms: ['rise']
- **id=E037** [SENT] [EVT]
  - Text: *Private equity firm offers 30% premium to take software company private*
  - Sentiment: true=`positive` pred=`neutral`
  - Event: true=`Merger/Acquisition` pred=`Other`
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
- **id=E047** [EVT]
  - Text: *Software firm releases version 4.0 of its analytics platform*
  - Event: true=`Product Launch` pred=`Other`
  - Matched terms: []
- **id=E052** [SENT]
  - Text: *Pharma company launches generic version of blockbuster drug in US market*
  - Sentiment: true=`neutral` pred=`positive`
  - Matched terms: ['launches']
- **id=E073** [EVT]
  - Text: *Regulator grants licence to the fintech, allowing it to launch banking services*
  - Event: true=`Regulatory/Legal` pred=`Product Launch`
  - Matched terms: ['launch']
- **id=E074** [SENT] [EVT]
  - Text: *Company hit with $800m verdict in patent dispute and plans to appeal*
  - Sentiment: true=`negative` pred=`neutral`
  - Event: true=`Regulatory/Legal` pred=`Other`
  - Matched terms: []
- **id=E075** [EVT]
  - Text: *Parliament committee holds hearing on proposed data privacy law*
  - Event: true=`Regulatory/Legal` pred=`Other`
  - Matched terms: []
- **id=E077** [SENT] [EVT]
  - Text: *Authorities ban short selling in financial stocks for 30 days amid volatility*
  - Sentiment: true=`negative` pred=`neutral`
  - Event: true=`Regulatory/Legal` pred=`Other`
  - Matched terms: []
- **id=E078** [EVT]
  - Text: *Appeals court overturns record penalty against the lender*
  - Event: true=`Regulatory/Legal` pred=`Other`
  - Matched terms: ['record']
- **id=E103** [SENT] [EVT]
  - Text: *Not a single bank missed its capital target in this year's stress exercise*
  - Sentiment: true=`positive` pred=`negative`
  - Event: true=`Regulatory/Legal` pred=`Other`
  - Matched terms: ['missed']
