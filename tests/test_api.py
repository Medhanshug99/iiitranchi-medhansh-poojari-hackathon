"""Tests for the Flask API (src.app) using the test client.

All tests run fully offline. pipeline.run() is patched to prevent real file writes
to data/signals.jsonl. The test client loads signals from the real sample data via
a patch that intercepts the run() call and writes to a tempfile instead.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# We need the app object. Import it and seed STATE before running tests.
import src.app as app_module
from src.app import app, STATE
from src.riskengine.stress import SCENARIOS


def _seed_state():
    """Load sample signals into STATE without writing to data/signals.jsonl."""
    from src.riskengine.ingest import gather
    from src.riskengine.pipeline import build_signals
    import tempfile, json
    from pathlib import Path

    items, prov = gather(live=False)
    signals = build_signals(items)
    # Write to a temp file instead of data/signals.jsonl
    tmpf = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w", encoding="utf-8")
    for s in signals:
        tmpf.write(json.dumps(s.to_dict(), ensure_ascii=False) + "\n")
    tmpf.close()
    STATE["signals"] = [s.to_dict() for s in signals]
    STATE["live"] = False
    return Path(tmpf.name)


class TestAPIBasic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.testing = True
        cls.client = app.test_client()
        cls._tmppath = _seed_state()

    @classmethod
    def tearDownClass(cls):
        cls._tmppath.unlink(missing_ok=True)

    # --- Homepage ---
    def test_get_root_200(self):
        """GET / returns HTTP 200."""
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)

    # --- /api/summary ---
    def test_summary_200_and_keys(self):
        """GET /api/summary returns 200 with required top-level keys."""
        r = self.client.get("/api/summary")
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        for key in ("total", "by_source", "by_event", "avg_sentiment", "high_impact", "live"):
            self.assertIn(key, body, f"Missing key '{key}' in /api/summary")

    def test_summary_total_matches_state(self):
        """GET /api/summary total matches number of signals in STATE."""
        r = self.client.get("/api/summary")
        body = json.loads(r.data)
        self.assertEqual(body["total"], len(STATE["signals"]))

    # --- /api/signals ---
    def test_signals_200_returns_list(self):
        """GET /api/signals returns 200 with a JSON list."""
        r = self.client.get("/api/signals")
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIsInstance(body, list)

    def test_signals_limit_filter(self):
        """GET /api/signals?limit=5 returns exactly 5 items."""
        r = self.client.get("/api/signals?limit=5")
        body = json.loads(r.data)
        self.assertEqual(len(body), 5)

    def test_signals_ticker_filter(self):
        """GET /api/signals?ticker=AAPL returns only rows with AAPL in entities."""
        r = self.client.get("/api/signals?ticker=AAPL")
        body = json.loads(r.data)
        for sig in body:
            self.assertIn("AAPL", sig["entities"],
                          f"Signal {sig['id']} lacks AAPL but was returned")

    def test_signals_event_type_filter(self):
        """GET /api/signals?event_type=Earnings returns only Earnings rows."""
        r = self.client.get("/api/signals?event_type=Earnings")
        body = json.loads(r.data)
        for sig in body:
            self.assertEqual(sig["event_type"].lower(), "earnings",
                             f"Non-Earnings event: {sig['event_type']}")

    def test_signals_min_impact_filter(self):
        """GET /api/signals?min_impact=7 returns only rows with impact >= 7."""
        r = self.client.get("/api/signals?min_impact=7")
        body = json.loads(r.data)
        self.assertGreater(len(body), 0, "No signals with impact >= 7")
        for sig in body:
            self.assertGreaterEqual(sig["impact"], 7.0,
                                    f"Signal {sig['id']} has impact {sig['impact']} < 7")

    # --- /api/analyze ---
    def test_analyze_400_on_empty_text(self):
        """POST /api/analyze with missing 'text' field returns 400."""
        r = self.client.post("/api/analyze",
                             data=json.dumps({}),
                             content_type="application/json")
        self.assertEqual(r.status_code, 400)
        body = json.loads(r.data)
        self.assertIn("error", body)

    def test_analyze_400_on_whitespace_text(self):
        """POST /api/analyze with whitespace-only text returns 400."""
        r = self.client.post("/api/analyze",
                             data=json.dumps({"text": "   "}),
                             content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_analyze_200_on_valid_text(self):
        """POST /api/analyze with valid text returns 200 with all expected keys."""
        r = self.client.post("/api/analyze",
                             data=json.dumps({"text": "Markets crash as bank defaults emerge"}),
                             content_type="application/json")
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        for key in ("sentiment", "sentiment_label", "event_type", "event_confidence",
                    "impact", "tickers", "matched_terms"):
            self.assertIn(key, body, f"Missing key '{key}' in /api/analyze response")

    # --- /api/refresh ---
    def test_refresh_200_sample(self):
        """POST /api/refresh {live:false} returns 200 with signals count and live=false."""
        # Patch pipeline.run to avoid writing data/signals.jsonl
        tmpf = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False)
        tmppath = Path(tmpf.name)
        tmpf.close()

        orig_run = app_module.pipeline.run
        def patched_run(live=False, path=None):
            # Write to temp, not data/
            return orig_run(live=live, path=tmppath)

        with mock.patch.object(app_module.pipeline, "run", side_effect=patched_run):
            r = self.client.post("/api/refresh",
                                 data=json.dumps({"live": False}),
                                 content_type="application/json")
        tmppath.unlink(missing_ok=True)
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("signals", body)
        self.assertIn("live", body)
        self.assertFalse(body["live"])

    # --- /api/rebalance ---
    def test_rebalance_200_and_keys(self):
        """GET /api/rebalance returns 200 with tickers, history, summary."""
        r = self.client.get("/api/rebalance")
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        for key in ("tickers", "sectors", "history", "summary"):
            self.assertIn(key, body)

    # --- /api/stress ---
    def test_stress_200_and_runs(self):
        """GET /api/stress returns 200 with a 'runs' list."""
        r = self.client.get("/api/stress")
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("runs", body)
        self.assertIsInstance(body["runs"], list)

    # --- /api/stress/run ---
    def test_stress_run_400_unknown_scenario(self):
        """POST /api/stress/run with unknown scenario returns 400."""
        r = self.client.post("/api/stress/run",
                             data=json.dumps({"scenario": "NotAScenario"}),
                             content_type="application/json")
        self.assertEqual(r.status_code, 400)
        body = json.loads(r.data)
        self.assertIn("error", body)
        self.assertIn("available", body)

    def test_stress_run_200_for_each_known_scenario(self):
        """POST /api/stress/run returns 200 for each scenario in SCENARIOS."""
        for name in SCENARIOS:
            r = self.client.post("/api/stress/run",
                                 data=json.dumps({"scenario": name}),
                                 content_type="application/json")
            self.assertEqual(r.status_code, 200, f"Scenario '{name}' returned {r.status_code}")
            body = json.loads(r.data)
            self.assertIn("pnl", body, f"Missing 'pnl' for scenario '{name}'")

    # --- /api/scenarios ---
    def test_scenarios_200_and_all_names(self):
        """GET /api/scenarios returns 200 and lists all scenario names."""
        r = self.client.get("/api/scenarios")
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        for name in SCENARIOS:
            self.assertIn(name, body, f"Scenario '{name}' missing from /api/scenarios")


class TestLiveState(unittest.TestCase):

    def setUp(self):
        from src.app import STATE
        # Reset state
        STATE["signals"] = []
        STATE["live"] = False
        STATE["live_requested"] = False
        STATE["sources"] = {"news": "sample", "social": "sample"}

        # Patch pipeline.run to avoid writing to data/signals.jsonl
        import tempfile
        from pathlib import Path
        import src.app as app_module

        self.tmpf = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False)
        self.tmppath = Path(self.tmpf.name)
        self.tmpf.close()

        self.orig_run = app_module.pipeline.run
        def patched_run(live=False, path=None):
            return self.orig_run(live=live, path=self.tmppath)
        
        self.patcher = mock.patch.object(app_module.pipeline, "run", side_effect=patched_run)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tmppath.unlink(missing_ok=True)

    def test_live_network_fails(self):
        """Live requested but the network fetch raises or times out: live is false, live_requested is true, sources are 'sample'."""
        from src.app import refresh, STATE
        import src.riskengine.ingest as ingest_mod

        with mock.patch.object(ingest_mod, "_http_get", side_effect=OSError("network down")):
            refresh(live=True)
        
        self.assertFalse(STATE["live"])
        self.assertTrue(STATE["live_requested"])
        self.assertEqual(STATE["sources"], {"news": "sample", "social": "sample"})

    def test_live_network_succeeds(self):
        """Live requested and fetch succeeds: live is true and sources show 'live'."""
        from src.app import refresh, STATE
        import src.riskengine.ingest as ingest_mod

        def fake_get(url, timeout=8):
            if "reddit" in url:
                return b'{"data":{"children":[{"data":{"id":"1","created_utc":1600000000,"title":"test","selftext":"txt","ups":1,"num_comments":1}}]}}'
            else:
                return b'<rss><channel><item><title>A</title><description>B</description><pubDate>Mon, 01 Jan 2000 00:00:00 GMT</pubDate><guid>1</guid></item></channel></rss>'

        with mock.patch.object(ingest_mod, "_http_get", side_effect=fake_get):
            refresh(live=True)
        
        self.assertTrue(STATE["live"])
        self.assertTrue(STATE["live_requested"])
        self.assertEqual(STATE["sources"], {"news": "live", "social": "live"})

    def test_live_mixed_case(self):
        """Mixed case: news live, social fell back: live is true, sources are {"news":"live","social":"sample"}."""
        from src.app import refresh, STATE
        import src.riskengine.ingest as ingest_mod

        def fake_get(url, timeout=8):
            if "reddit" in url:
                raise OSError("reddit down")
            else:
                return b'<rss><channel><item><title>A</title><description>B</description><pubDate>Mon, 01 Jan 2000 00:00:00 GMT</pubDate><guid>1</guid></item></channel></rss>'

        with mock.patch.object(ingest_mod, "_http_get", side_effect=fake_get):
            refresh(live=True)
        
        self.assertTrue(STATE["live"])
        self.assertTrue(STATE["live_requested"])
        self.assertEqual(STATE["sources"], {"news": "live", "social": "sample"})

    def test_live_not_requested(self):
        """Live not requested: live false, live_requested false."""
        from src.app import refresh, STATE
        refresh(live=False)
        self.assertFalse(STATE["live"])
        self.assertFalse(STATE["live_requested"])
        self.assertEqual(STATE["sources"], {"news": "sample", "social": "sample"})


if __name__ == "__main__":
    unittest.main()
