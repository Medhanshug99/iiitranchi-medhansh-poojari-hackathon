"""Tests for src.riskengine.nlp – sentiment, impact, events, entities."""
import unittest
from src.riskengine.nlp import analyze, extract_tickers, score_sentiment, label_sentiment, classify_event, estimate_impact
from src.riskengine.ingest import FileSource, DATA_DIR


class TestSentimentBounds(unittest.TestCase):

    def _check_bounds(self, text, src="news", eng=0):
        a = analyze(text, src, eng)
        self.assertGreaterEqual(a.sentiment, -1.0, f"sentiment < -1 for: {text!r}")
        self.assertLessEqual(a.sentiment, 1.0, f"sentiment > +1 for: {text!r}")

    def test_sentiment_bounds_all_sample_news(self):
        """Every sample news item produces sentiment in [-1, 1]."""
        for item in FileSource(DATA_DIR / "sample_news.jsonl", "news").fetch():
            self._check_bounds(item.text)

    def test_sentiment_bounds_all_sample_social(self):
        """Every sample social item produces sentiment in [-1, 1]."""
        for item in FileSource(DATA_DIR / "sample_social.jsonl", "social").fetch():
            self._check_bounds(item.text, "social")

    def test_sentiment_bounds_empty(self):
        """Empty string produces sentiment in [-1, 1]."""
        self._check_bounds("")

    def test_sentiment_bounds_very_long(self):
        """A 10 000-character text produces sentiment in [-1, 1]."""
        self._check_bounds("terrible crash loss " * 500)

    def test_sentiment_bounds_emoji_only(self):
        """Emoji-only text produces sentiment in [-1, 1]."""
        self._check_bounds("🚀🚀🚀🚀🚀")

    def test_sentiment_empty_is_zero(self):
        """Empty string yields sentiment exactly 0.0."""
        s, _ = score_sentiment("")
        self.assertEqual(s, 0.0)


class TestSentimentLogic(unittest.TestCase):

    def test_negation_not_good_is_negative(self):
        """'not good' must produce a negative sentiment score."""
        s, _ = score_sentiment("not good")
        self.assertLess(s, 0.0, f"Expected negative, got {s}")

    def test_negation_no_growth_is_negative(self):
        """'no growth' must produce a negative sentiment score."""
        s, _ = score_sentiment("no growth")
        self.assertLess(s, 0.0, f"Expected negative, got {s}")

    def test_intensifier_stronger_than_plain(self):
        """'very terrible' scores lower than 'terrible' (INTENSIFIERS[very]=1.3)."""
        # NOTE: 'absolutely' is NOT in INTENSIFIERS — that is a coverage gap in
        # lexicon.py worth reporting but NOT fixed here per the rules.
        # We use 'very' which IS in INTENSIFIERS with weight 1.3.
        plain, _ = score_sentiment("terrible")
        intense, _ = score_sentiment("very terrible")
        self.assertLess(intense, plain,
                        f"intensifier should amplify: plain={plain}, intense={intense}")

    def test_up_percent_is_positive(self):
        """'up 8%' text produces a positive sentiment score."""
        s, _ = score_sentiment("stock up 8%")
        self.assertGreater(s, 0.0, f"Expected positive for 'up 8%', got {s}")

    def test_down_percent_is_negative(self):
        """'down 8%' text produces a negative sentiment score."""
        s, _ = score_sentiment("stock down 8%")
        self.assertLess(s, 0.0, f"Expected negative for 'down 8%', got {s}")

    def test_label_thresholds(self):
        """label_sentiment boundaries: >=0.15 positive, <=-0.15 negative, else neutral."""
        self.assertEqual(label_sentiment(0.15), "positive")
        self.assertEqual(label_sentiment(-0.15), "negative")
        self.assertEqual(label_sentiment(0.0), "neutral")
        self.assertEqual(label_sentiment(0.14), "neutral")
        self.assertEqual(label_sentiment(-0.14), "neutral")


class TestImpactBounds(unittest.TestCase):

    def test_impact_bounds_all_sample_items(self):
        """Every sample item produces impact in [1, 10]."""
        for src_type, fname in [("news", "sample_news.jsonl"), ("social", "sample_social.jsonl")]:
            for item in FileSource(DATA_DIR / fname, src_type).fetch():
                a = analyze(item.text, src_type, item.engagement)
                self.assertGreaterEqual(a.impact, 1.0, f"impact < 1 for: {item.text!r}")
                self.assertLessEqual(a.impact, 10.0, f"impact > 10 for: {item.text!r}")

    def test_catastrophic_beats_routine(self):
        """A missile-strike headline scores higher impact than a routine product launch."""
        cat = analyze("BREAKING: Missile strikes escalate military tensions; oil surges as global stock markets crash", "news")
        routine = analyze("Apple unveils new iPhone feature at launch event", "news")
        self.assertGreater(cat.impact, routine.impact,
                           f"catastrophic={cat.impact} should beat routine={routine.impact}")

    def test_social_damped_versus_news(self):
        """Same text gets lower impact as 'social' than as 'news'."""
        text = "Regional bank defaults on loan covenants; credit spreads widen sharply"
        news_impact = analyze(text, "news").impact
        social_impact = analyze(text, "social", 0).impact
        self.assertLess(social_impact, news_impact,
                        f"social={social_impact} should be < news={news_impact}")


class TestEventClassification(unittest.TestCase):

    CASES = [
        ("Geopolitical",      "missile strikes military conflict sanctions war escalating"),
        ("Macroeconomic",     "Fed raises interest rates inflation GDP unemployment"),
        ("Credit Event",      "bank defaults on loan covenants credit spreads contagion"),
        ("Merger/Acquisition","acquisition merger takeover bid deal shareholder approval"),
        ("Product Launch",    "company unveils new product launch keynote feature release"),
        ("Earnings",          "quarterly earnings beat estimates profit revenue guidance raised"),
        ("Regulatory/Legal",  "regulatory investigation antitrust fine enforcement action penalty"),
        ("Cyber/Operational", "cyber attack data breach ransomware system outage disruption"),
        ("Other",             "asdfjkl qwerty xyzzy gibberish nkjhgfd"),
    ]

    def test_event_classification(self):
        """Each prototype sentence classifies into the expected event type."""
        for expected_type, text in self.CASES:
            result, _ = classify_event(text)
            self.assertEqual(result, expected_type,
                             f"Expected '{expected_type}' for: {text!r}, got '{result}'")


class TestEntityLinking(unittest.TestCase):

    def test_cashtag_detected(self):
        """$AAPL cashtag is detected as AAPL."""
        self.assertIn("AAPL", extract_tickers("$AAPL rallies"))

    def test_cashtag_googl(self):
        """$GOOGL cashtag is detected as GOOGL."""
        self.assertIn("GOOGL", extract_tickers("$GOOGL beats estimates"))

    def test_alias_iphone_detects_aapl(self):
        """'iphone' alias maps to AAPL (case-insensitive)."""
        self.assertIn("AAPL", extract_tickers("New iPhone model launched today"))

    def test_alias_microsoft_detects_msft(self):
        """'microsoft' alias maps to MSFT."""
        self.assertIn("MSFT", extract_tickers("Microsoft announces layoffs"))

    def test_capitalized_apple_detects_aapl(self):
        """Capitalized 'Apple' company name maps to AAPL."""
        self.assertIn("AAPL", extract_tickers("Apple Inc unveils new Mac"))

    def test_lowercase_apple_no_false_positive(self):
        """Lowercase 'apple' (fruit context) does NOT produce AAPL."""
        self.assertNotIn("AAPL", extract_tickers("apple the fruit is tasty"))

    def test_chase_generic_no_false_positive(self):
        """Generic word 'chase' does NOT map to JPM."""
        self.assertNotIn("JPM", extract_tickers("chase the dog around the park"))

    def test_windows_generic_no_false_positive(self):
        """Generic word 'windows' does NOT map to MSFT."""
        self.assertNotIn("MSFT", extract_tickers("clean the windows in your house"))

    def test_multiple_entities(self):
        """Multiple tickers can appear in one text."""
        tickers = extract_tickers("$TSLA and $NVDA both surged today")
        self.assertIn("TSLA", tickers)
        self.assertIn("NVDA", tickers)

    def test_no_entities_market_wide(self):
        """A pure macro headline produces no entity tickers."""
        tickers = extract_tickers("Fed raises interest rates by 50 basis points")
        self.assertEqual(tickers, [])


if __name__ == "__main__":
    unittest.main()
