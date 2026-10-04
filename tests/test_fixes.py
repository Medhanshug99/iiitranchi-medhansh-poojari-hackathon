import unittest
from datetime import datetime, timedelta, timezone

from src.riskengine.nlp import analyze
from src.riskengine.stress import triggered_events

class TestFixes(unittest.TestCase):
    def test_sentiment_words(self):
        a1 = analyze("This is not good.")
        self.assertEqual(a1.sentiment_label, "negative")
        self.assertLess(a1.sentiment, 0.0)

        a2 = analyze("This is good.")
        self.assertEqual(a2.sentiment_label, "positive")
        self.assertGreater(a2.sentiment, 0.0)

    def test_entity_linking(self):
        a1 = analyze("apple the fruit is tasty")
        self.assertNotIn("AAPL", a1.tickers)

        a2 = analyze("chase the dog")
        self.assertNotIn("JPM", a2.tickers)

        a3 = analyze("Apple Inc unveils new iPhone")
        self.assertIn("AAPL", a3.tickers)

        a4 = analyze("$AAPL rallies")
        self.assertIn("AAPL", a4.tickers)

    def test_dedup_and_trigger(self):
        t0 = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
        def iso(m): return (t0 + timedelta(minutes=m)).isoformat().replace("+00:00", "Z")

        sigs = [
            # 1. Valid trigger
            {"id": "s1", "ts": iso(0), "impact": 8.0, "event_type": "Geopolitical", "sentiment": -0.5, "sentiment_label": "negative", "text": ""},
            # 2. Suppressed (within 60m)
            {"id": "s2", "ts": iso(10), "impact": 8.5, "event_type": "Geopolitical", "sentiment": -0.6, "sentiment_label": "negative", "text": ""},
            # 3. Suppressed (within 60m of s1)
            {"id": "s3", "ts": iso(40), "impact": 9.0, "event_type": "Geopolitical", "sentiment": -0.7, "sentiment_label": "negative", "text": ""},
            # 4. Triggers (90m > 60m from s1)
            {"id": "s4", "ts": iso(90), "impact": 8.0, "event_type": "Geopolitical", "sentiment": -0.5, "sentiment_label": "negative", "text": ""},
            # 5. High impact but positive (should NOT trigger)
            {"id": "pos1", "ts": iso(100), "impact": 8.0, "event_type": "Credit Event", "sentiment": 0.5, "sentiment_label": "positive", "text": ""},
        ]
        
        trig = triggered_events(sigs)
        t_ids = [t["id"] for t in trig]
        self.assertEqual(t_ids, ["s1", "s4"])
        self.assertNotIn("pos1", t_ids)

if __name__ == '__main__':
    unittest.main()
