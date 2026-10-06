"""Finance-tuned sentiment lexicon and event-classification rules.

Weights are on a -3..+3 scale. Kept dependency-free on purpose so the engine
runs anywhere; `nlp.py` can optionally blend in VADER / a transformer if
installed (see README "Upgrade path").
"""

POSITIVE = {
    "good": 1.5, "better": 1.5, "improve": 1.5, "improves": 1.5, "improved": 1.5, "growing": 1.5,
    "beat": 2, "beats": 2, "surge": 2.5, "surges": 2.5, "surged": 2.5, "soar": 2.5,
    "soars": 2.5, "soared": 2.5, "rally": 2, "rallies": 2, "rallied": 2, "record": 1.5,
    "upgrade": 2, "upgraded": 2, "growth": 1.5, "profit": 1.5, "profits": 1.5,
    "profitable": 1.5, "strong": 1.5, "stronger": 1.5, "outperform": 2, "bullish": 2,
    "raises": 1.5, "raised": 1.5, "boost": 1.5, "boosts": 1.5, "gain": 1.5, "gains": 1.5,
    "gained": 1.5, "approval": 2, "approved": 2, "breakthrough": 2.5, "partnership": 1.5,
    "expands": 1.5, "expansion": 1.5, "win": 1.5, "wins": 1.5, "optimistic": 1.5,
    "recovery": 1.5, "rebound": 1.5, "rebounds": 1.5, "dividend": 1, "buyback": 1.5,
    "tops": 2, "exceeds": 2, "exceeded": 2, "jumps": 2, "jump": 2, "climbs": 1.5,
    "rises": 1.5, "rise": 1.5, "rose": 1.5, "demand": 1, "innovative": 1.5, "launch": 1,
    "launches": 1, "unveils": 1.5, "unveiled": 1.5, "resilient": 1.5, "upside": 1.5,
    "buy": 1.5, "love": 1.5, "great": 1.5, "amazing": 2, "winning": 1.5, "moon": 2,
    "calm": 1, "eases": 1.5, "ceasefire": 2, "deal": 1, "agreement": 1.5, "relief": 1.5,
    # (e) context words that help flip meaning — added for normalization
    "impressive": 2.0,
}

NEGATIVE = {
    "bad": -1.5, "worse": -1.5, "decline": -1.5, "declines": -1.5, "declined": -1.5, "loses": -1.5, "lost": -1.5,
    "miss": -2, "misses": -2, "missed": -2, "plunge": -3, "plunges": -3, "plunged": -3,
    "tumble": -2.5, "tumbles": -2.5, "tumbled": -2.5, "slump": -2.5, "slumps": -2.5,
    "crash": -3, "crashes": -3, "crashed": -3, "downgrade": -2, "downgraded": -2,
    "loss": -2, "losses": -2, "weak": -1.5, "weaker": -1.5, "weakness": -1.5,
    "bearish": -2, "cuts": -1.5, "cut": -1.5, "lawsuit": -2, "sued": -2, "probe": -2,
    "investigation": -2, "fraud": -3, "recall": -2, "recalls": -2, "default": -3,
    "defaults": -3, "defaulted": -3, "bankruptcy": -3, "bankrupt": -3, "layoffs": -2,
    "warning": -1.5, "warns": -2, "warned": -2, "fears": -1.5, "fear": -1.5,
    "selloff": -2.5, "sell-off": -2.5, "sanctions": -2, "war": -2.5, "attack": -2.5,
    "attacks": -2.5, "invasion": -3, "invade": -3, "shutdown": -2, "breach": -2.5,
    "hack": -2.5, "hacked": -2.5, "fine": -1.5, "fined": -2, "delay": -1.5,
    "delays": -1.5, "delayed": -1.5, "halt": -2, "halts": -2, "collapse": -3,
    "collapses": -3, "collapsed": -3, "crisis": -2.5, "bailout": -2.5, "downturn": -2,
    "recession": -2.5, "inflation": -1, "shortage": -1.5, "strike": -1.5, "drop": -1.5,
    "drops": -1.5, "fell": -1.5, "falls": -1.5, "fall": -1.5, "sink": -2, "sinks": -2,
    "slides": -1.5, "worst": -2, "risk": -1, "risks": -1, "threat": -2, "threatens": -3,
    "threaten": -3, "tensions": -1.5, "escalate": -2, "escalates": -2, "escalation": -2,
    "sell": -1.5, "bubble": -1.5, "terrible": -2, "scam": -3, "rekt": -2.5, "dump": -2,
    "dumping": -2, "concern": -1, "concerns": -1, "outage": -2, "blackout": -2,
    "turmoil": -2.5, "stubborn": -1.5, "hotter": -1.5, "sticky": -1.5, "disaster": -2.5,
    "worried": -1.5, "worry": -1.5, "bleeding": -2, "stagnant": -1.5, "headache": -1.5,
    "contagion": -3, "insolvency": -3, "insolvent": -3, "writedown": -2, "write-down": -2,
    # Change (d): add disappoint family and fines (verb form)
    "disappoints": -2, "disappointing": -2, "lukewarm": -1.5,
    "fines": -2,
}

LEXICON = {**POSITIVE, **NEGATIVE}

# Phrase-level sentiment overrides (checked before token lookup).
# Key: lowercase phrase (space-separated tokens as they appear in text).
# Value: float weight on the same -3..+3 scale.
PHRASE_SENTIMENT = {
    "profit warning": -3.0,   # (d): "profit" +1.5 must not cancel "warning" -1.5
}

EMOJI = {"🚀": 2.5, "📈": 2, "💰": 1.5, "🔥": 1, "📉": -2, "💀": -2, "🩸": -2, "🚨": -1.5, "⚠️": -1}

NEGATIONS = {"not", "no", "never", "without", "neither", "nor", "cannot", "hardly", "fails", "failed", "unlikely"}
INTENSIFIERS = {
    "very": 1.3, "extremely": 1.5, "massive": 1.4, "sharply": 1.4, "significantly": 1.3,
    "huge": 1.3, "major": 1.2, "severe": 1.4, "heavily": 1.3, "slightly": 0.7,
    "modestly": 0.7, "marginally": 0.6, "somewhat": 0.8,
}

# ---------------------------------------------------------------------------
# (e) Context words that neutralise "attack"/"default" when the action is thwarted/averted.
# ---------------------------------------------------------------------------
# Words meaning "the bad thing was prevented" (appear BEFORE the negative word)
AVERSION_CONTEXT = {
    "default": {"averting", "avert", "averted", "avoid", "avoiding", "avoided", "prevented",
                "preventing", "prevents"},
    "attack":  {"thwart", "thwarts", "thwarted", "foil", "foiled", "repel", "repelled",
                "repels", "counter", "countered"},
}

# ---------------------------------------------------------------------------
# (f) Routine/neutral cues: if any of these phrases are found the raw score is
# multiplied by NEUTRAL_SHRINK before the label is applied.
# ---------------------------------------------------------------------------
NEUTRAL_CUES = [
    "in line with", "unchanged", "flat", "scheduled", "to report",
    "will hold", "no change", "as expected", "in-line",
    "consults", "convenes", "discussions", "minutes", "names", "appoints", "completes review"
]
NEUTRAL_SHRINK = 0.3   # multiply raw sentiment magnitude when routine cue present

# ---------------------------------------------------------------------------
# (b) Context tokens that confirm a "downgrad" match is really about credit/debt.
# Without at least one of these, the Credit Event rule should not fire on "downgrad".
# ---------------------------------------------------------------------------
CREDIT_DOWNGRADE_CONTEXT = {
    "rating", "rated", "debt", "bond", "bonds", "notes", "sovereign", "credit",
    "outlook", "junk", "investment", "grade", "moody", "fitch", "s&p",
}

# ---------------------------------------------------------------------------
# (h) Domain-direction flips for words whose sign depends on the object.
# ---------------------------------------------------------------------------
DIRECTION_FLIPS = [
    ({"surge", "surges", "surged", "jump", "jumps", "jumped", "climb", "climbs", "climbed", "spike", "spikes", "spiked", "spiking"}, 
     {"inflation", "yield", "yields", "claim", "claims", "cost", "costs", "loss", "losses", "default", "defaults", "price", "prices"}, 
     -1.0),
    ({"cut", "cuts", "slash", "slashes", "slashed"}, 
     {"guidance", "forecast", "forecasts", "rating", "ratings"}, 
     1.0),  # cut is already negative, we want it to stay negative or flip? Wait, cut is -1.5. So 1.0 keeps it negative.
    # Ah, the prompt says: "cut/slash" are bad for guidance, forecasts, ratings (so keep negative)
    # and good for costs, rates and inflation (flip to positive).
    ({"cut", "cuts", "slash", "slashes", "slashed"}, 
     {"cost", "costs", "rate", "rates", "inflation"}, 
     -1.0), # Flips -1.5 to +1.5
]

# ---------------------------------------------------------------------------
# Event classification. Each rule is (regex, weight); highest total wins.
# ---------------------------------------------------------------------------
EVENT_RULES = {
    "Geopolitical": [
        (r"\bwar\b", 3), (r"\binvasion|\binvade", 3.5), (r"\bsanction", 2.5), (r"\bmissile", 3),
        (r"\bmilitary", 2.5), (r"\btensions?\b", 2), (r"\bconflict", 2), (r"\bceasefire", 2.5),
        (r"\bembargo", 3), (r"\btariffs?\b", 2), (r"\bcoup\b", 3), (r"\bterror", 3),
        (r"\bstrait\b|\bborder\b", 1.5), (r"\bgeopolitic", 3), (r"\bnato\b|\bopec\b", 2),
        (r"\btrade war", 3), (r"\bblockade", 3),
        (r"\battacks?\b", 2.5), (r"\bstrikes?\b", 2.5), (r"\bclash(es)?\b", 2.5),
        (r"\btruce\b", 2.5), (r"\bsummit\b", 2), (r"\bministe(r|rs|rial)\b", 1.5),
        (r"\btroops?\b", 2.5), (r"\bnuclear\b", 2.5), (r"\brefuge(e|es)?\b", 1.5),
        (r"\bdiplo(mat|macy|matic)\b", 1.5), (r"\bsanction(s|ed)?\b", 2.5),
        (r"\btrade truce\b", 3), (r"\btrade (deal|pact)\b", 2),
        (r"\bpeace talks\b", 2.5), (r"\bfactions\b", 2), (r"\bwithdraw forces\b", 2.5),
        (r"\bescalation\b", 2.5),
    ],
    "Macroeconomic": [
        (r"\binflation|\bcpi\b", 3), (r"\binterest rates?\b|\brate (hike|cut)s?\b", 3),
        (r"\bfed\b|\bfederal reserve|\becb\b|\bcentral bank", 3), (r"\bgdp\b", 3),
        (r"\brecession", 3), (r"\bunemployment|\bjobs report|\bpayrolls", 2.5),
        (r"\byield curve|\btreasury yields?", 2.5), (r"\bpmi\b", 2), (r"\bstagflation", 3),
        (r"\bbasis points?\b|\bbps\b", 1.5), (r"\bconsumer (spending|confidence)", 2),
        (r"\bretail sales\b", 2.5), (r"\btreasury auction\b", 2.5),
        (r"\bmortgage rates?\b", 2.5), (r"\btightening\b", 2),
        (r"\brate hike(s)?\b|\brate cut(s)?\b", 3),
        (r"\bond yields?\b|\b10-year\b|\b10 year\b", 2),
        (r"\bpayrolls?\b", 2.5), (r"\bfomc\b", 3), (r"\bhiking\b|\bhawkish\b|\bdovish\b", 2),
        (r"\byields?\b", 1.5),
        (r"\bpolicy rate\b", 2.5), (r"\bbond purchase\b", 2.5), (r"\bjobless claims\b", 2.5),
        (r"\blabour market\b", 2.5),
    ],
    "Credit Event": [
        (r"\bdefault", 3.5), (r"\bbankrupt", 3.5), (r"\bchapter 11\b", 3.5),
        (r"\bdowngrad", 2.5),
        (r"\bcredit rating|\bmoody|\bs&p global ratings|\bfitch", 2),
        (r"\binsolven", 3.5), (r"\bbailout", 3), (r"\bdebt restructuring|\brestructur", 2.5),
        (r"\bcredit spreads?\b|\bcds\b", 2.5), (r"\bbank run|\bliquidity (crisis|crunch)", 3.5),
        (r"\bnon-performing|\bloan losses|\bwrite-?downs?", 2.5), (r"\bcovenant", 2),
        (r"\brating agency\b|\brating (upgrade|downgrade|affirm|affirmation)\b", 2.5),
        (r"\bupgrade[sd]?\b.*\b(debt|bonds?|notes?|rating)\b", 2),
        (r"\binvestment.?grade\b|\bjunk\b|\bsenior notes?\b", 2.5),
        (r"\bcontagion\b", 3), (r"\bcredit\b", 1.5),
        (r"\brefinanc", 2.5), (r"\bmaturing debt\b", 2.5), (r"\bliquidity\b", 2),
        (r"\bextends? maturity\b", 2.5), (r"\bcredit facility\b", 2.5),
    ],
    "Merger/Acquisition": [
        (r"\bacquir", 3), (r"\bacquisition", 3), (r"\bmerger|\bmerge\b|\bmerges\b", 3),
        (r"\btakeover", 3), (r"\bbuyout", 3), (r"\bbid for\b|\bdeal to buy", 2.5),
        (r"\bto buy\b.*\b(billion|million|bn|m)\b", 2.5), (r"\bdivest|\bspin-?off", 2),
        (r"\bstrategic alternatives?\b", 2.5), (r"\bpossible sale\b|\bpotential sale\b", 2.5),
        (r"\btakeover premium\b|\bpremium (to|for) (acquire|buy|take)\b", 2.5),
        (r"\bprivate equity\b|\blbo\b", 2), (r"\bgo private\b|\btake.*private\b", 2.5),
        (r"\bshareholders? (approve|vote)\b", 2),
        (r"\bunsolicited proposal\b", 2.5), (r"\bpremium\b", 1.5),
    ],
    "Product Launch": [
        (r"\blaunch", 3), (r"\bunveil", 3), (r"\bannounces? new", 2.5), (r"\brelease[sd]?\b", 1.5),
        (r"\bnew (iphone|model|chip|feature|product|service)", 3), (r"\brolls? out", 2.5),
        (r"\bintroduc", 2), (r"\bfda approv", 3), (r"\bbreakthrough", 1.5),
        (r"\bdebuts?\b", 3), (r"\bversion \d+\b", 2), (r"\bnew (tier|platform|tool)\b", 2.5),
        (r"\bad.?supported tier\b", 2), (r"\bpre.?order\b", 1.5),
        (r"\bupdate\b", 1.5), (r"\brelease\b", 1.5),
    ],
    "Earnings": [
        (r"\bearnings", 3), (r"\bquarterly results|\bq[1-4]\b", 2.5), (r"\brevenue", 2),
        (r"\bguidance|\boutlook", 2.5), (r"\beps\b", 3),
        (r"\bbeats? (estimates|expectations|forecasts)", 3),
        (r"\bmiss(es)? (estimates|expectations|forecasts)", 3), (r"\bprofit warning", 3),
        (r"\bannual (profit|loss|results|earnings)\b", 2.5),
        (r"\bthird.?quarter results?\b|\bsecond.?quarter results?\b|\bfirst.?quarter results?\b", 2.5),
        (r"\bquarterly (loss|profit|income)\b", 2.5),
        (r"\bforecast(s)?\b|\bfull.?year\b", 2.5),
        (r"\bprofit\b", 1.5), (r"\bloss\b", 1.5),
        (r"\bto report\b.*\b(results|earnings|quarter)\b", 2.5),
        (r"\bresults\b", 1.5),
        (r"\bnet income\b", 2.5), (r"\bquarterly sales\b", 2.5), (r"\btargets\b", 1.5),
    ],
    "Regulatory/Legal": [
        (r"\blawsuit|\bsued?\b|\bsettlement", 3), (r"\bantitrust", 3.5),
        (r"\bsec\b|\bdoj\b|\bftc\b", 2.5), (r"\bregulator|\bregulation|\bfined?\b", 2.5),
        (r"\binvestigation|\bprobe\b", 3), (r"\bsubpoena|\bindict", 3),
        (r"\bcompliance|\bfraud", 2.5),
        (r"\bfines\b|\bpenalt(y|ies)\b", 2.5), (r"\bverdict\b|\bruling\b", 2.5),
        (r"\bhearing\b", 2), (r"\blicen(ce|se)\b", 2), (r"\bban\b", 2),
        (r"\btax proposal\b|\bwindfall tax\b", 2.5), (r"\bappeal(s)?\b", 1.5),
        (r"\bcourt\b", 2), (r"\bshort selling\b", 2),
        (r"\bdata privacy\b|\bpatent\b", 2), (r"\bstress (test|exercise)\b", 2),
        (r"\bwatchdog\b", 2.5), (r"\bmarket manipulation\b", 2.5), (r"\bsuit\b", 2.0),
        (r"\bclaims lacked merit\b", 2.5), (r"\bdraft rules\b", 2.5),
        (r"\bcharge.*\bdefendants?\b", 2.5), (r"\bsue.*\bdefendants?\b", 2.5),
    ],
    "Cyber/Operational": [
        (r"\bcyber", 3.5), (r"\bbreach", 3), (r"\bransomware", 3.5), (r"\bhack", 3),
        (r"\boutage", 3), (r"\brecall", 3), (r"\bsupply chain", 2.5),
        (r"\bfactory fire|\bstrike\b", 2),
        (r"\bmaintenance\b", 2), (r"\bunusual activity\b", 2.5),
        (r"\bsystems? (down|restored|investigating)\b", 2.5),
        (r"\bdata (lost|leaked|compromised)\b", 2.5),
        (r"\bapp (down|unavailable)\b", 2), (r"\bstrike action\b", 2),
        (r"\bsystem upgrade\b", 2.5), (r"\boffline\b", 2.0), (r"\bpipeline leak\b", 2.5),
        (r"\btechnology glitch\b", 2.5), (r"\bservers? (down|froze|lost)\b", 2.5),
    ],
}

# Baseline market-impact severity (1-10) per event class.
EVENT_SEVERITY = {
    "Geopolitical": 7.0,
    "Credit Event": 7.0,
    "Macroeconomic": 6.0,
    "Regulatory/Legal": 5.0,
    "Merger/Acquisition": 5.0,
    "Cyber/Operational": 5.0,
    "Earnings": 4.0,
    "Product Launch": 3.0,
    "Other": 2.0,
}

# Extra severity when catastrophic language is present.
SEVERITY_BOOSTERS = {
    "collapse": 1.5, "default": 1.5, "invasion": 2.0, "war": 1.5, "bankruptcy": 1.5,
    "crisis": 1.5, "systemic": 2.0, "contagion": 2.0, "emergency": 1.5, "plunge": 1.0,
    "crash": 1.5, "attack": 1.5, "missile": 1.5, "bank run": 2.0, "bailout": 1.5,
    "insolvency": 1.5, "blockade": 1.5, "worst": 1.0, "unprecedented": 1.0, "record": 0.5,
}
