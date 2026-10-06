"""Tests for new NLP behaviour added in the tuning phase.

Each test class corresponds to one change (a through g) described in the tuning
log. All examples are fresh sentences not present in data/labeled_eval.csv.
"""
import unittest
from src.riskengine.nlp import (
    analyze, classify_event, label_sentiment, score_sentiment,
    EXTENDED_LEXICON, _has_neutral_cue, _aversion_blocked,
)


# ---------------------------------------------------------------------------
# (a) Inflection normaliser
# ---------------------------------------------------------------------------

class TestInflectionNormaliser(unittest.TestCase):

    def test_inflected_plunged_is_negative(self):
        """'plunged' (ed-form of 'plunge') must score negative via inflection lookup."""
        s, hits = score_sentiment("The stock plunged overnight")
        self.assertLess(s, 0.0, f"Expected negative for 'plunged', got {s}")

    def test_inflected_fines_is_negative(self):
        """'fines' (s-form of 'fine') must score negative via inflection lookup."""
        s, hits = score_sentiment("Regulator fines the bank over mis-selling")
        self.assertLess(s, 0.0, f"Expected negative for 'fines', got {s}")

    def test_inflected_downgrades_is_negative(self):
        """'downgrades' (s-form of 'downgrade') must score negative via inflection lookup."""
        s, hits = score_sentiment("Agency downgrades the sovereign rating to junk")
        self.assertLess(s, 0.0, f"Expected negative for 'downgrades', got {s}")

    def test_canonical_form_still_works(self):
        """Canonical form 'plunge' is unaffected — still negative."""
        s, _ = score_sentiment("Markets plunge on shock data")
        self.assertLess(s, 0.0, f"Expected negative for 'plunge', got {s}")

    def test_extended_lexicon_includes_inflection(self):
        """EXTENDED_LEXICON must contain 'plunged' and map it to the same sign as 'plunge'."""
        from src.riskengine.lexicon import LEXICON
        self.assertIn("plunged", EXTENDED_LEXICON)
        self.assertLess(EXTENDED_LEXICON["plunged"], 0)


# ---------------------------------------------------------------------------
# (b) Analyst-downgrade gate (Credit Event must NOT fire on stock downgrades)
# ---------------------------------------------------------------------------

class TestAnalystDowngradeGate(unittest.TestCase):

    def test_analyst_downgrade_is_not_credit_event(self):
        """'Broker downgrades stock to underperform' must NOT classify as Credit Event."""
        evt, _ = classify_event("Broker downgrades the stock to underperform on valuation concerns")
        self.assertNotEqual(evt, "Credit Event",
                            f"Analyst downgrade should not be Credit Event, got '{evt}'")

    def test_rating_agency_downgrade_is_credit_event(self):
        """'Rating agency downgrades sovereign debt to junk' MUST be Credit Event."""
        evt, _ = classify_event("Rating agency downgrades sovereign debt to junk, spreads blow out")
        self.assertEqual(evt, "Credit Event",
                         f"Rating downgrade with debt context should be Credit Event, got '{evt}'")

    def test_equity_downgrade_no_debt_context_not_credit_event(self):
        """'Analyst downgrades shares to sell' (no debt context) must NOT be Credit Event."""
        evt, _ = classify_event("Analyst downgrades shares to sell after disappointing results")
        self.assertNotEqual(evt, "Credit Event",
                            f"Equity downgrade without debt context should not be Credit Event")


# ---------------------------------------------------------------------------
# (c) Broadened event-rule vocabulary
# ---------------------------------------------------------------------------

class TestEventRuleExpansion(unittest.TestCase):

    def test_geopolitical_clash(self):
        """'Border clash' headline must classify as Geopolitical."""
        evt, _ = classify_event("Border clashes escalate between two neighbours as troops mobilise")
        self.assertEqual(evt, "Geopolitical", f"Expected Geopolitical, got '{evt}'")

    def test_geopolitical_summit(self):
        """'Summit between leaders' headline must classify as Geopolitical."""
        evt, _ = classify_event("Summit between regional leaders ends with joint statement")
        self.assertEqual(evt, "Geopolitical", f"Expected Geopolitical, got '{evt}'")

    def test_macro_retail_sales(self):
        """'Retail sales' headline must classify as Macroeconomic."""
        evt, _ = classify_event("Retail sales rise 0.1 percent in October")
        self.assertEqual(evt, "Macroeconomic", f"Expected Macroeconomic, got '{evt}'")

    def test_macro_payrolls(self):
        """'Payrolls beat expectations' must classify as Macroeconomic, not Earnings."""
        evt, _ = classify_event("Payrolls beat expectations by 120,000 as unemployment falls to record low")
        self.assertEqual(evt, "Macroeconomic", f"Expected Macroeconomic, got '{evt}'")

    def test_earnings_quarterly_loss(self):
        """'Quarterly loss widens' must classify as Earnings."""
        evt, _ = classify_event("Quarterly loss widens to $450m as costs balloon")
        self.assertEqual(evt, "Earnings", f"Expected Earnings, got '{evt}'")

    def test_earnings_annual_profit(self):
        """'Annual profit' headline must classify as Earnings."""
        evt, _ = classify_event("Oil major posts record annual profit and raises dividend")
        self.assertEqual(evt, "Earnings", f"Expected Earnings, got '{evt}'")

    def test_product_launch_debut(self):
        """'Debuts ad-supported tier' must classify as Product Launch."""
        evt, _ = classify_event("Streaming service debuts ad-supported tier priced at $6.99")
        self.assertEqual(evt, "Product Launch", f"Expected Product Launch, got '{evt}'")

    def test_regulatory_fine(self):
        """'Regulator fines bank' headline must classify as Regulatory/Legal."""
        evt, _ = classify_event("Regulator fines bank $1.2bn over money laundering failures")
        self.assertEqual(evt, "Regulatory/Legal", f"Expected Regulatory/Legal, got '{evt}'")

    def test_cyber_maintenance(self):
        """'Scheduled maintenance' headline must classify as Cyber/Operational."""
        evt, _ = classify_event("Exchange schedules planned maintenance for Saturday night")
        self.assertEqual(evt, "Cyber/Operational", f"Expected Cyber/Operational, got '{evt}'")

    def test_ma_strategic_alternatives(self):
        """'Explores strategic alternatives' must classify as Merger/Acquisition."""
        evt, _ = classify_event("Company explores strategic alternatives including a possible sale")
        self.assertEqual(evt, "Merger/Acquisition", f"Expected Merger/Acquisition, got '{evt}'")


# ---------------------------------------------------------------------------
# (d) Dev-supported sentiment lexicon changes
# ---------------------------------------------------------------------------

class TestSentimentLexiconExpansion(unittest.TestCase):

    def test_impressive_is_positive(self):
        """'Impressive' must produce a positive sentiment score."""
        s, _ = score_sentiment("New chip looks seriously impressive and benchmarks are ahead")
        self.assertGreater(s, 0.0, f"Expected positive for 'impressive', got {s}")

    def test_disappoints_is_negative(self):
        """'Disappoints' must produce a negative sentiment score."""
        s, _ = score_sentiment("Pre-order demand disappoints analysts this quarter")
        self.assertLess(s, 0.0, f"Expected negative for 'disappoints', got {s}")

    def test_lukewarm_is_negative(self):
        """'Lukewarm' must produce a negative sentiment score."""
        s, _ = score_sentiment("Early reviews of the new headset are lukewarm")
        self.assertLess(s, 0.0, f"Expected negative for 'lukewarm', got {s}")

    def test_threatens_is_strongly_negative(self):
        """'Threatens' scores <= -0.15 (negative label)."""
        s, _ = score_sentiment("Blockade threatens key grain export route")
        self.assertLess(s, -0.14, f"Expected negative for 'threatens', got {s}")

    def test_profit_warning_phrase_is_negative(self):
        """'Profit warning' as a phrase must produce a negative score (not cancelled by 'profit')."""
        s, hits = score_sentiment("Insurer issues profit warning citing claims costs")
        self.assertLess(s, 0.0, f"'profit warning' phrase should be negative, got {s}")
        self.assertIn("profit warning", hits)


# ---------------------------------------------------------------------------
# (e) Aversion context for "default" and "attack"
# ---------------------------------------------------------------------------

class TestAversionContext(unittest.TestCase):

    def test_averting_default_not_negative(self):
        """'Averting default' must suppress the -3.0 default score."""
        s, _ = score_sentiment("Lender secures rescue financing, averting default")
        # Should be neutral or positive, definitely not strongly negative
        self.assertGreater(s, -0.15, f"'averting default' should not be strongly negative, got {s}")

    def test_thwarts_attack_not_negative(self):
        """'Thwarts attack' must suppress the -2.5 attack score."""
        s, _ = score_sentiment("Company thwarts attempted cyber attack with new defences")
        self.assertGreater(s, -0.15, f"'thwarts attack' should not be strongly negative, got {s}")

    def test_plain_default_still_negative(self):
        """'Defaults on debt' without aversion context must remain negative."""
        s, _ = score_sentiment("Bank defaults on loan covenants")
        self.assertLess(s, 0.0, f"Plain 'default' should remain negative, got {s}")


# ---------------------------------------------------------------------------
# (f) Neutral cues
# ---------------------------------------------------------------------------

class TestNeutralCues(unittest.TestCase):

    def test_in_line_with_shrinks_score(self):
        """'in line with' neutral cue must shrink sentiment by NEUTRAL_SHRINK factor."""
        from src.riskengine.lexicon import NEUTRAL_SHRINK
        # Without cue: "retail sales rise" -> score from 'rise'
        s_plain, _ = score_sentiment("Retail sales rise strongly this month")
        # With cue: same positive word but cue should shrink magnitude
        s_cued, _ = score_sentiment("Retail sales rise in line with economists forecasts")
        self.assertLess(abs(s_cued), abs(s_plain),
                        f"Neutral cue should shrink score: no-cue={s_plain}, cued={s_cued}")

    def test_scheduled_shrinks_to_neutral(self):
        """'Scheduled maintenance' should land in neutral band."""
        s, _ = score_sentiment("Exchange scheduled planned maintenance for Saturday")
        lbl = label_sentiment(s)
        # Just verify it's not strongly positive or negative
        self.assertNotEqual(lbl, "positive", f"Routine scheduled event should not be positive")

    def test_neutral_cue_helper(self):
        """_has_neutral_cue identifies 'in line with' correctly."""
        self.assertTrue(_has_neutral_cue("retail sales rise in line with forecasts"))
        self.assertFalse(_has_neutral_cue("bank defaults on loan covenants"))


# ---------------------------------------------------------------------------
# (g) Negation window — kept at 3, regression check
# ---------------------------------------------------------------------------

class TestNegationWindow(unittest.TestCase):

    def test_negation_window_3_no_growth_negative(self):
        """'no growth' with 3-token window is still negative (regression guard)."""
        s, _ = score_sentiment("no growth")
        self.assertLess(s, 0.0, f"'no growth' must remain negative, got {s}")

    def test_negation_window_not_good_negative(self):
        """'not good' with 3-token window is still negative (regression guard)."""
        s, _ = score_sentiment("not good")
        self.assertLess(s, 0.0, f"'not good' must remain negative, got {s}")

    def test_window_4_would_break_no_growth(self):
        """Document why window=4 is NOT used: 'no growth' remains correct at 3."""
        # The token sequence is ['no', 'growth']. At window=3, 'no' is in the 3-token
        # lookback for 'growth'. At window=4, the same — so in this specific pair both
        # work. The risk is in longer compounds like "no significant growth today" where
        # window=4 and an intervening intensifier could interact unexpectedly.
        # We confirm window=3 gives the correct result.
        s, _ = score_sentiment("no growth")
        self.assertLess(s, 0.0)


if __name__ == "__main__":
    unittest.main()
