"""FX Forward P&L tests – hand-checked arithmetic in comments.

position_pnl formula for FX Forwards:
    dV = notional * fx_direction * fx_shock
"""
import unittest
from src.riskengine.stress import load_portfolio, position_pnl, SCENARIOS, Scenario


def _p(portfolio, pid):
    return next(r for r in portfolio if r["id"] == pid)


# A zero-fx synthetic scenario for the zero-effect test
_ZERO_FX_SCENARIO = Scenario(
    name="Zero FX",
    description="No FX shock at all.",
    equity_shock=0.0, rate_shock_bp=0, spread_shock_bp=0,
    fx_shock=0.0, pd_multiplier=1.0,
)


class TestFXForwardPnL(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.port = load_portfolio()

    # ------------------------------------------------------------------
    # Geopolitical scenario: fx_shock = -0.04 (-4%)
    # ------------------------------------------------------------------

    def test_D005_geopolitical(self):
        """D005 EURUSD (notional 120M, direction +1) under Geopolitical.
        dV = 120,000,000 * (+1) * (-0.04) = -4,800,000
        """
        sc = SCENARIOS["Geopolitical"]
        self.assertEqual(sc.fx_shock, -0.04)          # guard: confirm scenario unchanged
        pnl = position_pnl(_p(self.port, "D005"), sc)
        self.assertAlmostEqual(pnl, -4_800_000, places=0)

    def test_D006_geopolitical(self):
        """D006 USDJPY (notional 80M, direction -1) under Geopolitical.
        dV = 80,000,000 * (-1) * (-0.04) = +3,200,000
        USD strengthens against JPY -> short JPY position gains.
        """
        sc = SCENARIOS["Geopolitical"]
        pnl = position_pnl(_p(self.port, "D006"), sc)
        self.assertAlmostEqual(pnl, 3_200_000, places=0)
        self.assertGreater(pnl, 0, "D006 (short JPY) gains when USD strengthens")

    # ------------------------------------------------------------------
    # Zero fx_shock -> both positions unchanged
    # ------------------------------------------------------------------

    def test_D005_zero_fx_shock_is_zero(self):
        """D005 P&L is exactly 0 when fx_shock = 0."""
        pnl = position_pnl(_p(self.port, "D005"), _ZERO_FX_SCENARIO)
        self.assertEqual(pnl, 0.0)

    def test_D006_zero_fx_shock_is_zero(self):
        """D006 P&L is exactly 0 when fx_shock = 0."""
        pnl = position_pnl(_p(self.port, "D006"), _ZERO_FX_SCENARIO)
        self.assertEqual(pnl, 0.0)

    # ------------------------------------------------------------------
    # USD bond (B001, Government sector) is unaffected by fx_shock
    # ------------------------------------------------------------------

    def test_usd_bond_unaffected_by_fx(self):
        """B001 (USD Government bond) P&L does not change when fx_shock changes.
        Bond P&L formula uses only duration * rate_shock + spread_dur * spread_shock.
        fx_shock is irrelevant for Bonds; the FX path is only for Derivative/FX.
        """
        b001 = _p(self.port, "B001")
        geo_pnl    = position_pnl(b001, SCENARIOS["Geopolitical"])
        no_fx_pnl  = position_pnl(b001, _ZERO_FX_SCENARIO)

        # B001 is Government, so no spread component either.
        # Both scenarios should affect it only via rate_shock.
        # Geo: rate_shock = -50bp; zero: rate_shock = 0.
        # The rate parts differ – what we assert is that changing ONLY fx_shock
        # on an otherwise identical scenario does not change B001's result.
        same_rates_diff_fx = Scenario(
            name="Same rates, diff FX",
            description="Clone of Geo rates but +10% FX to prove FX irrelevance.",
            equity_shock=-0.10, rate_shock_bp=-50, spread_shock_bp=150,
            fx_shock=0.10,      # very different from Geo's -0.04
            pd_multiplier=1.6,
        )
        pnl_with_big_fx = position_pnl(b001, same_rates_diff_fx)
        self.assertAlmostEqual(geo_pnl, pnl_with_big_fx, places=2,
                               msg="B001 P&L should be identical regardless of fx_shock value")


if __name__ == "__main__":
    unittest.main()
