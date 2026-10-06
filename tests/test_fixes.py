import unittest
from src.riskengine.nlp import analyze, classify_event, score_sentiment
from src.riskengine.lexicon import EVENT_RULES

class TestRound2Fixes(unittest.TestCase):

    def test_domain_direction_flip_surge_inflation(self):
        """'surge' is usually positive, but with 'inflation' it flips to negative."""
        pos_text = "Profits surge 20% in the third quarter."
        neg_text = "Inflation surges to highest level in decades."
        
        pos_score, _ = score_sentiment(pos_text)
        neg_score, _ = score_sentiment(neg_text)
        
        self.assertGreater(pos_score, 0)
        self.assertLess(neg_score, 0)

    def test_domain_direction_flip_cut_rates(self):
        """'cut' is usually negative, but with 'rates' it flips to positive."""
        neg_text = "Company cuts its full-year earnings guidance."
        pos_text = "Central bank cuts interest rates to stimulate growth."
        
        neg_score, _ = score_sentiment(neg_text)
        pos_score, _ = score_sentiment(pos_text)
        
        self.assertLess(neg_score, 0)
        self.assertGreater(pos_score, 0)

    def test_neutral_process_cues(self):
        """Process cues like 'convenes' or 'appoints' should shrink sentiment toward neutral."""
        # 'amazing' is positive, but 'appoints' neutralizes it
        base_text = "He is an amazing CEO."
        neut_text = "Board appoints amazing CEO."
        
        base_score, _ = score_sentiment(base_text)
        neut_score, _ = score_sentiment(neut_text)
        
        self.assertGreater(base_score, neut_score)
        
    def test_broadened_event_vocab(self):
        """Ensure new event vocabulary correctly routes to specific classes."""
        tests = [
            ("The company extends maturity on its debt", "Credit Event"),
            ("Servers lost connection causing an outage", "Cyber/Operational"),
            ("Company confirms new 2027 targets", "Earnings"),
            ("Rival factions agree to peace talks", "Geopolitical"),
            ("Jobless claims climb again", "Macroeconomic"),
            ("Board reviews unsolicited proposal", "Merger/Acquisition"),
            ("Just downloaded the new update", "Product Launch"),
            ("Market watchdog sues the broker", "Regulatory/Legal"),
        ]
        for text, expected in tests:
            with self.subTest(text=text):
                event, conf = classify_event(text)
                self.assertEqual(event, expected)

    def test_lower_minimum_score_for_other(self):
        """Lower minimum score (1.5) allows less confident rules to win over Other."""
        # 'premium' is weight 1.5 in M&A. Before it would fall to Other (< 2.0). Now it wins.
        event, conf = classify_event("The offer included a small premium.")
        self.assertEqual(event, "Merger/Acquisition")

if __name__ == "__main__":
    unittest.main()
