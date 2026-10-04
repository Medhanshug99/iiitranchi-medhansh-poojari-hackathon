"""Tests for src.riskengine.rebalancer – weights, bounds, sentiment tilt, decay."""
import math
import unittest
from datetime import datetime, timezone, timedelta

from src.riskengine.rebalancer import (
    SentimentRebalancer, apply_bounds, summarize, TICKERS, MIN_W, MAX_W
)


def _make_signal(ts_offset_min=0, sentiment=0.8, impact=8.0,
                 entities=None, event_type="Earnings",
                 source_type="news", sig_id="s1"):
    """Build a minimal signal dict suitable for SentimentRebalancer.update."""
    t0 = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
    ts = (t0 + timedelta(minutes=ts_offset_min)).isoformat().replace("+00:00", "Z")
    return {
        "id": sig_id,
        "ts": ts,
        "entities": entities or [],
        "event_type": event_type,
        "sentiment": sentiment,
        "impact": impact,
        "source_type": source_type,
    }


class TestWeightBoundsAfterReplay(unittest.TestCase):

    def setUp(self):
        """Load the real sample signals via pipeline for a realistic replay."""
        from src.riskengine.pipeline import load_signals
        self.signals = load_signals()

    def test_weights_sum_to_one_every_step(self):
        """Weights sum to 1.0 (within 1e-9) at every history step."""
        reb = SentimentRebalancer()
        hist = reb.replay(self.signals)
        self.assertGreater(len(hist), 0, "History must not be empty")
        for i, h in enumerate(hist):
            total = sum(h["weights"].values())
            self.assertAlmostEqual(total, 1.0, places=9,
                                   msg=f"Step {i}: weights sum to {total}")

    def test_every_weight_within_bounds_every_step(self):
        """Every ticker weight is within [2%, 15%] at every history step."""
        reb = SentimentRebalancer()
        hist = reb.replay(self.signals)
        for i, h in enumerate(hist):
            for t, w in h["weights"].items():
                self.assertGreaterEqual(w, MIN_W - 1e-9,
                                        f"Step {i} ticker {t}: weight {w:.4f} below floor {MIN_W}")
                self.assertLessEqual(w, MAX_W + 1e-9,
                                     f"Step {i} ticker {t}: weight {w:.4f} above cap {MAX_W}")


class TestApplyBoundsEdgeCases(unittest.TestCase):

    def _check(self, raw):
        result = apply_bounds(raw)
        total = sum(result.values())
        self.assertAlmostEqual(total, 1.0, places=9, msg=f"Sum={total} for raw={raw}")
        for k, v in result.items():
            self.assertGreaterEqual(v, MIN_W - 1e-9)
            self.assertLessEqual(v, MAX_W + 1e-9)
        return result

    def test_all_equal_inputs(self):
        """All-equal weights should produce the equal-weight allocation."""
        n = len(TICKERS)
        raw = {t: 1.0 for t in TICKERS}
        result = self._check(raw)
        expected = 1.0 / n
        for v in result.values():
            self.assertAlmostEqual(v, expected, places=6)

    def test_one_huge_input_is_capped(self):
        """If one ticker weight is 1000x others, it must be capped at MAX_W."""
        raw = {t: 1.0 for t in TICKERS}
        raw[TICKERS[0]] = 1000.0
        result = self._check(raw)
        self.assertAlmostEqual(result[TICKERS[0]], MAX_W, places=6)

    def test_one_near_zero_input_is_floored(self):
        """If one ticker weight is nearly 0, it must be floored at MIN_W."""
        raw = {t: 1.0 for t in TICKERS}
        raw[TICKERS[0]] = 1e-9
        result = self._check(raw)
        self.assertAlmostEqual(result[TICKERS[0]], MIN_W, places=6)


class TestSentimentTilt(unittest.TestCase):

    def test_positive_sentiment_raises_weight_above_equal(self):
        """Positive-sentiment signal on a specific ticker raises its weight above 1/N."""
        n = len(TICKERS)
        equal = 1.0 / n
        reb = SentimentRebalancer()
        sig = _make_signal(entities=["AAPL"], sentiment=0.9, impact=9.0)
        w = reb.update(sig)
        self.assertGreater(w["AAPL"], equal,
                           f"AAPL weight {w['AAPL']:.4f} should be above equal {equal:.4f}")

    def test_negative_sentiment_lowers_weight_below_equal(self):
        """Negative-sentiment signal on a specific ticker lowers its weight below 1/N."""
        n = len(TICKERS)
        equal = 1.0 / n
        reb = SentimentRebalancer()
        sig = _make_signal(entities=["AAPL"], sentiment=-0.9, impact=9.0)
        w = reb.update(sig)
        self.assertLess(w["AAPL"], equal,
                        f"AAPL weight {w['AAPL']:.4f} should be below equal {equal:.4f}")

    def test_time_decay_fades_to_equal_weight(self):
        """After many half-lives with no new signal, a tilted weight approaches 1/N."""
        from src.riskengine.rebalancer import HALF_LIFE_MIN
        n = len(TICKERS)
        equal = 1.0 / n

        reb = SentimentRebalancer()
        # Strong positive push on AAPL
        reb.update(_make_signal(ts_offset_min=0, entities=["AAPL"], sentiment=0.9, impact=9.0))
        initial_w = reb.weights()["AAPL"]
        self.assertGreater(initial_w, equal)

        # Advance time by 10 half-lives – state should decay by factor exp(-10*ln2) ≈ 0.001
        # No signals, just apply _decay manually
        from datetime import datetime, timezone, timedelta
        future = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc) + timedelta(minutes=10 * HALF_LIFE_MIN)
        reb._decay(future)
        after_decay_w = reb.weights()["AAPL"]

        # Weight should be much closer to equal weight (within 1% of equal)
        self.assertAlmostEqual(after_decay_w, equal, delta=0.01,
                               msg=f"After 10 half-lives: {after_decay_w:.5f} vs equal {equal:.5f}")


class TestMarketWideSectorBeta(unittest.TestCase):

    def test_geopolitical_negative_lowers_tech_raises_energy(self):
        """A market-wide Geopolitical negative signal lowers Tech and raises Energy.

        From MARKET_EVENT_BETA: Geopolitical beta for Tech=+1.0, Energy=-1.2.
        Negative sentiment * positive beta -> Tech state goes negative -> weight drops.
        Negative sentiment * negative beta (-1.2) -> Energy state goes positive -> weight rises.
        """
        n = len(TICKERS)
        equal = 1.0 / n

        reb = SentimentRebalancer()
        sig = _make_signal(
            entities=[],                    # market-wide: no entities
            event_type="Geopolitical",
            sentiment=-0.9,
            impact=9.0,
        )
        w = reb.update(sig)

        # Tech names should drop; pick AAPL as representative
        self.assertLess(w["AAPL"], equal,
                        f"AAPL (Tech) should be below equal after Geopolitical neg, got {w['AAPL']:.4f}")
        # Energy names should rise; pick XOM
        self.assertGreater(w["XOM"], equal,
                           f"XOM (Energy) should be above equal after Geopolitical neg, got {w['XOM']:.4f}")


class TestReplayDeterminism(unittest.TestCase):

    def test_replay_is_deterministic(self):
        """Two consecutive replay() calls on the same rebalancer produce identical history."""
        from src.riskengine.pipeline import load_signals
        signals = load_signals()
        reb = SentimentRebalancer()
        hist1 = reb.replay(signals)
        hist2 = reb.replay(signals)
        self.assertEqual(len(hist1), len(hist2))
        for i, (h1, h2) in enumerate(zip(hist1, hist2)):
            for t in h1["weights"]:
                self.assertAlmostEqual(h1["weights"][t], h2["weights"][t], places=12,
                                       msg=f"Step {i} ticker {t} differs between runs")


if __name__ == "__main__":
    unittest.main()
