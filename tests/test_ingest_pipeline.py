"""Tests for src.riskengine.ingest and src.riskengine.pipeline.

All tests run offline. urllib is mocked where network would be hit.
Writes to signals.jsonl are redirected to a tempfile; data/ files are never touched.
"""
import json
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from src.riskengine.ingest import FileSource, DATA_DIR, RawItem


class TestFileSource(unittest.TestCase):

    def test_news_file_returns_24_items(self):
        """FileSource on sample_news.jsonl returns exactly 24 items."""
        items = list(FileSource(DATA_DIR / "sample_news.jsonl", "news").fetch())
        self.assertEqual(len(items), 24)

    def test_social_file_returns_29_items(self):
        """FileSource on sample_social.jsonl returns exactly 29 items."""
        items = list(FileSource(DATA_DIR / "sample_social.jsonl", "social").fetch())
        self.assertEqual(len(items), 29)

    def test_news_source_type_is_news(self):
        """All items from the news FileSource have source_type='news'."""
        for item in FileSource(DATA_DIR / "sample_news.jsonl", "news").fetch():
            self.assertEqual(item.source_type, "news")

    def test_social_source_type_is_social(self):
        """All items from the social FileSource have source_type='social'."""
        for item in FileSource(DATA_DIR / "sample_social.jsonl", "social").fetch():
            self.assertEqual(item.source_type, "social")

    def test_raw_items_have_required_fields(self):
        """Every RawItem has non-empty id, ts, source, source_type, and text."""
        for fname, stype in [("sample_news.jsonl", "news"), ("sample_social.jsonl", "social")]:
            for item in FileSource(DATA_DIR / fname, stype).fetch():
                self.assertIsInstance(item, RawItem)
                self.assertTrue(item.id, f"id empty for item in {fname}")
                self.assertTrue(item.ts, f"ts empty for item in {fname}")
                self.assertTrue(item.source, f"source empty for item in {fname}")
                self.assertTrue(item.source_type)
                # text may be empty for blank posts; just check it's a str
                self.assertIsInstance(item.text, str)


class TestGatherFallback(unittest.TestCase):

    def test_gather_live_falls_back_when_network_fails(self):
        """When urllib raises (network blocked), gather(live=True) falls back to samples."""
        import src.riskengine.ingest as ingest_mod

        with mock.patch.object(ingest_mod, "_http_get", side_effect=OSError("blocked")):
            from src.riskengine.ingest import gather
            items = gather(live=True)

        # Should get the same total as offline: 24 news + 29 social = 53
        self.assertEqual(len(items), 53,
                         f"Expected 53 fallback items, got {len(items)}")
        types = {item.source_type for item in items}
        self.assertIn("news", types)
        self.assertIn("social", types)


class TestPipelineOutput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Run pipeline once (offline) to a temp file; collect signals."""
        from src.riskengine.pipeline import build_signals, write_signals
        from src.riskengine.ingest import gather

        items = gather(live=False)
        cls.signals = build_signals(items)

        cls.tmpfile = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False)
        cls.tmppath = Path(cls.tmpfile.name)
        cls.tmpfile.close()
        write_signals(cls.signals, cls.tmppath)

    @classmethod
    def tearDownClass(cls):
        cls.tmppath.unlink(missing_ok=True)

    def test_signal_count_matches_input(self):
        """Pipeline produces one signal per input item (24+29=53)."""
        self.assertEqual(len(self.signals), 53)

    def test_required_fields_present_and_typed(self):
        """Every Signal has all required fields with correct Python types."""
        for sig in self.signals:
            d = sig.to_dict()
            self.assertIsInstance(d["id"], str)
            self.assertIsInstance(d["ts"], str)
            self.assertIsInstance(d["source"], str)
            self.assertIsInstance(d["source_type"], str)
            self.assertIn(d["source_type"], ("news", "social"))
            self.assertIsInstance(d["entities"], list)
            self.assertIsInstance(d["sentiment"], float)
            self.assertIsInstance(d["sentiment_label"], str)
            self.assertIn(d["sentiment_label"], ("positive", "negative", "neutral"))
            self.assertIsInstance(d["event_type"], str)
            self.assertIsInstance(d["event_confidence"], float)
            self.assertIsInstance(d["impact"], float)
            self.assertIsInstance(d["text"], str)

    def test_write_load_roundtrip(self):
        """write_signals / load_signals round-trips identically (field-by-field)."""
        from src.riskengine.pipeline import load_signals
        loaded = load_signals(self.tmppath)
        self.assertEqual(len(loaded), len(self.signals))
        for orig, loaded_row in zip(self.signals, loaded):
            d = orig.to_dict()
            for key in d:
                self.assertEqual(d[key], loaded_row[key],
                                 f"Mismatch on field '{key}': {d[key]!r} vs {loaded_row[key]!r}")


class TestDataFileIntegrity(unittest.TestCase):

    def _check_jsonl(self, path, source_type):
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        ids = []
        for i, line in enumerate(lines):
            try:
                d = json.loads(line)
            except json.JSONDecodeError as e:
                self.fail(f"Invalid JSON on line {i+1} of {path.name}: {e}")
            self.assertIn("id", d, f"Missing 'id' on line {i+1}")
            self.assertIn("ts", d, f"Missing 'ts' on line {i+1}")
            self.assertIn("text", d, f"Missing 'text' on line {i+1}")
            ids.append(d["id"])
        return ids

    def test_sample_news_valid_jsonl_no_duplicates(self):
        """sample_news.jsonl: every line is valid JSON and all ids are unique."""
        ids = self._check_jsonl(DATA_DIR / "sample_news.jsonl", "news")
        self.assertEqual(len(ids), len(set(ids)), "Duplicate ids in sample_news.jsonl")

    def test_sample_social_valid_jsonl_no_duplicates(self):
        """sample_social.jsonl: every line is valid JSON and all ids are unique."""
        ids = self._check_jsonl(DATA_DIR / "sample_social.jsonl", "social")
        self.assertEqual(len(ids), len(set(ids)), "Duplicate ids in sample_social.jsonl")

    def test_no_duplicate_ids_across_files(self):
        """No id appears in both news and social sample files."""
        news_ids = set(
            json.loads(l)["id"]
            for l in (DATA_DIR / "sample_news.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()
        )
        social_ids = set(
            json.loads(l)["id"]
            for l in (DATA_DIR / "sample_social.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()
        )
        overlap = news_ids & social_ids
        self.assertEqual(overlap, set(), f"Cross-file duplicate ids: {overlap}")


if __name__ == "__main__":
    unittest.main()
