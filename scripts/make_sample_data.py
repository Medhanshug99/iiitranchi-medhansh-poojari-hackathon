"""Generate SYNTHETIC sample news + social data for offline demos.

All headlines/posts below are fabricated for demonstration; they are not real
reporting. Re-run: python scripts/make_sample_data.py
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data"
T0 = datetime(2026, 10, 1, 13, 30, tzinfo=timezone.utc)  # US market open

# (minutes after open, source, text)
NEWS = [
    (5,   "wire-sample", "Nvidia beats earnings estimates and raises guidance as AI chip demand surges, record quarterly revenue reported."),
    (20,  "wire-sample", "Apple unveils new iPhone feature set at launch event; analysts see strong upgrade cycle ahead."),
    (35,  "wire-sample", "Fed officials signal interest rates may stay higher for longer as inflation proves stubborn, Treasury yields rise."),
    (50,  "bizwire-sample", "Microsoft announces partnership expansion for Azure AI services, boosting enterprise demand outlook."),
    (65,  "wire-sample", "Tesla recalls 400,000 vehicles over brake software defect; regulators open investigation, shares slide."),
    (80,  "bizwire-sample", "JPMorgan reports profit beat and raises dividend as trading revenue jumps."),
    (95,  "wire-sample", "Amazon hit with FTC antitrust lawsuit over marketplace practices; fine could be significant."),
    (110, "bizwire-sample", "Pfizer wins FDA approval for new oncology drug, a breakthrough for its late-stage pipeline."),
    (125, "wire-sample", "Chevron agrees to acquire shale producer in $12 billion deal, expanding production capacity."),
    (140, "wire-sample", "Walmart raises full-year outlook on resilient consumer spending; revenue tops expectations."),
    (160, "wire-sample", "BREAKING: Missile strikes escalate military tensions; oil surges as global stocks plunge on war fears and blockade threat."),
    (172, "wire-sample", "Markets in turmoil: energy prices spike, sanctions announced, investors flee to Treasuries amid geopolitical crisis."),
    (185, "wire-sample", "Exxon and Chevron shares jump as crude surges on supply disruption fears."),
    (200, "wire-sample", "Regional lender defaults on loan covenants; credit spreads widen sharply and contagion fears hit Bank of America, Goldman Sachs and JPMorgan."),
    (215, "wire-sample", "Goldman Sachs warns of mounting loan losses; ratings agencies weigh downgrade of regional banks."),
    (235, "wire-sample", "Central bank springs surprise 75bp rate hike and warns of further tightening as inflation stays stubborn; bond yields surge and equities slide."),
    (255, "wire-sample", "Ceasefire talks ease tensions; oil falls from highs and stocks rebound in afternoon trade."),
    (270, "bizwire-sample", "Meta Platforms faces new EU investigation over data practices, shares fall."),
    (285, "wire-sample", "Alphabet unveils new Gemini model and launches enterprise agents; Google cloud demand strong."),
    (300, "wire-sample", "Johnson & Johnson misses revenue estimates, cuts outlook on weak medical device sales."),
    (315, "wire-sample", "US GDP growth revised higher as unemployment falls, easing recession fears."),
    (330, "wire-sample", "Tesla unveils new model and rolls out autopilot upgrade; deliveries beat forecasts."),
    (345, "bizwire-sample", "Apple faces supply chain delays and a possible factory strike, raising concerns about holiday production."),
    (360, "wire-sample", "Amazon launches new AWS service; Microsoft and Google rally in sympathy as cloud demand stays robust."),
]

# (minutes, source, text, likes, retweets)
SOCIAL = [
    (3,   "x-sample", "$NVDA absolutely crushing it, earnings beat and raised guidance 🚀🚀", 1800, 420),
    (12,  "x-sample", "Nvidia to the moon 🚀 $NVDA calls printing", 950, 210),
    (22,  "reddit-sample", "Apple new iPhone looks great, I love the new camera. Buying more $AAPL", 600, 80),
    (38,  "x-sample", "Fed not cutting rates anytime soon. inflation still a problem. bearish 📉", 700, 130),
    (52,  "x-sample", "$MSFT Azure partnership is huge, bullish", 420, 60),
    (66,  "x-sample", "Tesla recall is terrible news. brake defect?? $TSLA dumping 📉", 2200, 540),
    (82,  "reddit-sample", "JPM dividend raise is nice, strong profit. $JPM", 310, 45),
    (97,  "x-sample", "Amazon antitrust lawsuit could be a disaster, big fine incoming $AMZN", 880, 150),
    (112, "x-sample", "Pfizer FDA approval is a breakthrough 🚀 $PFE", 540, 90),
    (128, "reddit-sample", "Chevron acquisition looks smart, expansion of shale capacity $CVX", 260, 30),
    (142, "x-sample", "Walmart raising outlook, resilient consumer, strong $WMT", 330, 40),
    (162, "x-sample", "🚨 WAR. missile strikes, markets crashing, oil surging. sell everything 📉", 9500, 4200),
    (166, "x-sample", "This is a geopolitical crisis, sanctions incoming, stocks plunge sharply 💀", 6100, 2100),
    (170, "reddit-sample", "Market crash today, war fears everywhere. portfolio is bleeding 🩸", 3200, 800),
    (188, "x-sample", "$XOM and $CVX ripping as oil surges 🔥 hedge for the win", 1400, 260),
    (202, "x-sample", "Bank defaults?? credit spreads blowing out, contagion fears. $BAC $GS $JPM falling 📉", 5200, 1900),
    (210, "reddit-sample", "Is this 2008 again? regional bank default, bailout talk. very worried", 2400, 600),
    (218, "x-sample", "Goldman warns loan losses, downgrade risk. $GS dumping", 1500, 310),
    (238, "x-sample", "Central bank liquidity support is a relief, markets stabilise", 1900, 380),
    (258, "x-sample", "Ceasefire talks! tensions easing, oil down, stocks rebound 📈", 4100, 1100),
    (272, "reddit-sample", "Meta EU investigation is a headache for $META, shares falling", 520, 70),
    (288, "x-sample", "Gemini launch is amazing, Alphabet innovative again $GOOGL 🚀", 1200, 200),
    (302, "reddit-sample", "J&J missed revenue and cut outlook, weak. $JNJ selling", 280, 35),
    (318, "x-sample", "GDP strong, unemployment down, recession fears fading 📈", 1700, 300),
    (332, "x-sample", "$TSLA new model unveiled, deliveries beat. recall forgotten 🚀", 2600, 480),
    (348, "reddit-sample", "Apple factory strike and supply chain delays, worried about holiday quarter $AAPL", 410, 55),
    (362, "x-sample", "AWS launch plus cloud demand: $AMZN $MSFT $GOOGL all gaining 📈", 980, 150),
    (30,  "x-sample", "just bought some coffee, nice weather today", 5, 0),
    (150, "x-sample", "Not sure what to think about the market, waiting for more news", 12, 1),
]


def write(name, rows, social):
    with open(OUT / name, "w", encoding="utf-8") as f:
        for i, r in enumerate(rows):
            mins, src, text = r[0], r[1], r[2]
            rec = {
                "id": f"{name.split('_')[1].split('.')[0]}-{i:03d}",
                "ts": (T0 + timedelta(minutes=mins)).isoformat().replace("+00:00", "Z"),
                "source": src,
                "text": text,
            }
            if social:
                rec["likes"], rec["retweets"] = r[3], r[4]
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    write("sample_news.jsonl", NEWS, False)
    write("sample_social.jsonl", SOCIAL, True)
    print(f"wrote {len(NEWS)} news + {len(SOCIAL)} social items to {OUT}")
