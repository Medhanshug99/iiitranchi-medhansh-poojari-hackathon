"""Tests for src.riskengine.stress – hand-checked P&L arithmetic and trigger logic.

All expected values verified by hand before writing the assertions.
Arithmetic shown in comments beside each test.
"""
import unittest
from datetime import datetime, timedelta, timezone

from src.riskengine.stress import (
    SCENARIOS, load_portfolio, position_pnl, run_stress, triggered_events,
    DEFAULT_TRIGGER,
)


def _p(portfolio, pid):
    return next(r for r in portfolio if r["id"] == pid)


class TestHandCheckedPnL(unittest.TestCase):
    """Each test states the arithmetic in a comment so it can be defended live."""

    @classmethod
    def setUpClass(cls):
        cls.port = load_portfolio()

    # -- Bonds -----------------------------------------------------------

    def test_B001_macroeconomic(self):
        """B001 US Treasury 10Y under Macro shock.
        MV=150M, dur=8.4, rate_shock=+200bp=0.02, spread_dur=0 (Govt -> no spread).
        dV = -150M * (8.4 * 0.02 + 0) = -150M * 0.168 = -25,200,000
        """
        pnl = position_pnl(_p(self.port, "B001"), SCENARIOS["Macroeconomic"])
        self.assertAlmostEqual(pnl, -25_200_000, places=0)

    def test_B005_credit_event(self):
        """B005 HY Vector Oilfield under Credit Event.
        MV=40M, dur=4.2, rate_shock=-30bp=-0.003, spread_dur=3.9, spread_shock=+250bp=0.025.
        dV = -40M * (4.2*(-0.003) + 3.9*0.025)
           = -40M * (-0.0126 + 0.0975)
           = -40M * 0.0849 = -3,396,000
        """
        pnl = position_pnl(_p(self.port, "B005"), SCENARIOS["Credit Event"])
        self.assertAlmostEqual(pnl, -3_396_000, places=0)

    # -- Equities --------------------------------------------------------

    def test_E003_credit_event(self):
        """E003 Financials Basket under Credit Event.
        Sector override for Financials = -0.25; uses override (not beta * equity_shock).
        dV = 40M * (-0.25) = -10,000,000
        """
        pnl = position_pnl(_p(self.port, "E003"), SCENARIOS["Credit Event"])
        self.assertAlmostEqual(pnl, -10_000_000, places=0)

    def test_E001_custom_scenario(self):
        """E001 Nasdaq-100 Basket under Custom scenario.
        No sector override for Tech in Custom. equity_shock=-0.10, beta=1.15.
        dV = MV * (beta * equity_shock) = 60M * (1.15 * -0.10) = 60M * -0.115 = -6,900,000
        """
        pnl = position_pnl(_p(self.port, "E001"), SCENARIOS["Custom: equity -10%, rates +200bp"])
        self.assertAlmostEqual(pnl, -6_900_000, places=0)

    # -- Loans -----------------------------------------------------------

    def test_L004_credit_event(self):
        """L004 Meridian Properties (Real Estate BB) under Credit Event.
        MV=notional=70M, spread_dur=4.5, spread_shock=+250bp=0.025.
        Spread P&L = -70M * 4.5 * 0.025 = -7,875,000
        Sector PD multiplier for Real Estate = 2.8.
        stressed_pd = min(1, 0.014 * 2.8) = 0.0392.
        Credit loss = -70M * 0.45 * (0.0392 - 0.014) = -70M * 0.45 * 0.0252 = -793,800
        Total = -7,875,000 - 793,800 = -8,668,800
        """
        pnl = position_pnl(_p(self.port, "L004"), SCENARIOS["Credit Event"])
        self.assertAlmostEqual(pnl, -8_668_800, places=0)

    # -- Derivatives -----------------------------------------------------

    def test_D001_gains_when_rates_rise(self):
        """D001 IR Swap (pay fixed) gains when rates rise.
        DV01=+130,000, rate_shock=+200bp.
        dV = 130,000 * 200 = +26,000,000 (positive = gain)
        """
        pnl = position_pnl(_p(self.port, "D001"), SCENARIOS["Custom: equity -10%, rates +200bp"])
        self.assertAlmostEqual(pnl, 26_000_000, places=0)
        self.assertGreater(pnl, 0, "D001 (pay-fixed) must gain when rates rise")

    def test_D002_loses_when_rates_rise(self):
        """D002 IR Swap (receive fixed) loses when rates rise.
        DV01=-70,000, rate_shock=+200bp.
        dV = -70,000 * 200 = -14,000,000 (negative = loss)
        """
        pnl = position_pnl(_p(self.port, "D002"), SCENARIOS["Custom: equity -10%, rates +200bp"])
        self.assertAlmostEqual(pnl, -14_000_000, places=0)
        self.assertLess(pnl, 0, "D002 (receive-fixed) must lose when rates rise")

    def test_D003_gains_when_spreads_widen(self):
        """D003 CDS Protection Bought gains when spreads widen.
        CS01=+90,000, spread_shock=+250bp.
        dV = 90,000 * 250 = +22,500,000 (positive = gain from protection)
        """
        pnl = position_pnl(_p(self.port, "D003"), SCENARIOS["Credit Event"])
        self.assertAlmostEqual(pnl, 22_500_000, places=0)
        self.assertGreater(pnl, 0, "D003 (protection bought) must gain when spreads widen")

    def test_D004_loses_when_spreads_widen(self):
        """D004 CDS Protection Sold loses when spreads widen.
        CS01=-20,000, spread_shock=+250bp.
        dV = -20,000 * 250 = -5,000,000 (negative = loss for protection seller)
        """
        pnl = position_pnl(_p(self.port, "D004"), SCENARIOS["Credit Event"])
        self.assertAlmostEqual(pnl, -5_000_000, places=0)
        self.assertLess(pnl, 0, "D004 (protection sold) must lose when spreads widen")


class TestRunStressConsistency(unittest.TestCase):
    """run_stress() totals must be internally consistent."""

    @classmethod
    def setUpClass(cls):
        cls.port = load_portfolio()
        cls.result = run_stress(cls.port, SCENARIOS["Custom: equity -10%, rates +200bp"])

    def test_total_pnl_equals_sum_of_positions(self):
        """Portfolio total P&L equals the sum of individual position P&Ls."""
        position_sum = sum(p["pnl"] for p in self.result["worst_positions"])
        # worst_positions is only top 5; use by_asset_type totals for the full sum
        asset_pnl_sum = sum(v["pnl"] for v in self.result["by_asset_type"].values())
        self.assertAlmostEqual(asset_pnl_sum, self.result["pnl"], places=2,
                               msg="Asset-type P&L sum must equal total P&L")

    def test_after_minus_before_equals_pnl(self):
        """result['after'] - result['before'] == result['pnl']."""
        self.assertAlmostEqual(
            self.result["after"] - self.result["before"],
            self.result["pnl"],
            places=2,
        )


class TestTriggerLogic(unittest.TestCase):
    """triggered_events() must respect label, impact threshold, and event-type mapping."""

    def _sig(self, sid, offset_min, impact, label, event_type):
        t0 = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
        ts = (t0 + timedelta(minutes=offset_min)).isoformat().replace("+00:00", "Z")
        return {
            "id": sid,
            "ts": ts,
            "impact": impact,
            "sentiment": -0.8 if label == "negative" else 0.5,
            "sentiment_label": label,
            "event_type": event_type,
            "text": "test",
        }

    def test_negative_high_impact_mapped_type_triggers(self):
        """negative label + impact > 7 + mapped event type triggers a stress run."""
        sigs = [self._sig("s1", 0, 9.0, "negative", "Geopolitical")]
        triggered = triggered_events(sigs, threshold=7.0)
        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0]["id"], "s1")

    def test_positive_label_does_not_trigger(self):
        """Positive-label signal does NOT trigger even at high impact."""
        sigs = [self._sig("s1", 0, 9.0, "positive", "Geopolitical")]
        self.assertEqual(triggered_events(sigs), [])

    def test_neutral_label_does_not_trigger(self):
        """Neutral-label signal does NOT trigger even at high impact."""
        sigs = [self._sig("s1", 0, 9.0, "neutral", "Geopolitical")]
        self.assertEqual(triggered_events(sigs), [])

    def test_impact_exactly_at_threshold_does_not_trigger(self):
        """Impact exactly == threshold (7.0) does NOT trigger (condition is strict >)."""
        sigs = [self._sig("s1", 0, DEFAULT_TRIGGER, "negative", "Geopolitical")]
        self.assertEqual(triggered_events(sigs, threshold=DEFAULT_TRIGGER), [])

    def test_unmapped_event_type_does_not_trigger(self):
        """An event type not in SCENARIOS does NOT trigger a stress run."""
        sigs = [self._sig("s1", 0, 9.5, "negative", "Other")]
        self.assertEqual(triggered_events(sigs), [])

    def test_60min_dedup_pattern_0_10_40_90(self):
        """De-duplication: signals at 0, 10, 40, 90 minutes triggers only t=0 and t=90."""
        sigs = [
            self._sig("s0",  0,  8.0, "negative", "Geopolitical"),  # triggers
            self._sig("s1", 10,  8.5, "negative", "Geopolitical"),  # suppressed (<60min)
            self._sig("s2", 40,  9.0, "negative", "Geopolitical"),  # suppressed (<60min)
            self._sig("s3", 90,  8.0, "negative", "Geopolitical"),  # triggers (>60min)
        ]
        triggered = triggered_events(sigs, threshold=7.0)
        ids = [t["id"] for t in triggered]
        self.assertEqual(ids, ["s0", "s3"],
                         f"Expected ['s0','s3'], got {ids}")

    def test_different_event_types_independent_dedup(self):
        """Different event types have independent 60-min windows."""
        sigs = [
            self._sig("g1",  0, 9.0, "negative", "Geopolitical"),
            self._sig("c1",  5, 9.0, "negative", "Credit Event"),  # different type -> triggers
        ]
        triggered = triggered_events(sigs, threshold=7.0)
        self.assertEqual(len(triggered), 2)


class TestLoadPortfolio(unittest.TestCase):

    def test_portfolio_has_25_rows(self):
        """load_portfolio returns exactly 25 rows."""
        port = load_portfolio()
        self.assertEqual(len(port), 25)

    def test_total_market_value_near_1266_7M(self):
        """Total portfolio market value is approximately 1,266.7M."""
        port = load_portfolio()
        total_mv = sum(p["market_value"] for p in port)
        self.assertAlmostEqual(total_mv, 1_266_700_000, delta=500_000,
                               msg=f"Total MV: {total_mv/1e6:.1f}M")

    def test_numeric_fields_are_floats(self):
        """All numeric fields in every row are Python floats after load."""
        port = load_portfolio()
        for row in port:
            for field in ("market_value", "notional", "duration", "spread_dur",
                          "beta", "pd", "lgd", "dv01", "cs01", "fx_direction"):
                self.assertIsInstance(row[field], float,
                                      f"{row['id']}.{field} is not float")


if __name__ == "__main__":
    unittest.main()
