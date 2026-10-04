"""Tests for metric functions in src.evaluate.

All tests use tiny hand-calculated examples. Never touches data/labeled_eval.csv.
Uses tempfiles for any CSV I/O.
"""
import csv
import os
import tempfile
import unittest
from pathlib import Path

# Import the pure metric helpers directly.
from src.evaluate import (
    accuracy, confusion_matrix, per_class_metrics, macro_f1,
    majority_baseline, split_rows,
)


class TestAccuracy(unittest.TestCase):

    def test_all_correct(self):
        """Accuracy is 1.0 when all predictions match truth."""
        self.assertEqual(accuracy(["a", "b", "c"], ["a", "b", "c"]), 1.0)

    def test_all_wrong(self):
        """Accuracy is 0.0 when no predictions match truth."""
        self.assertEqual(accuracy(["a", "a", "a"], ["b", "b", "b"]), 0.0)

    def test_half_correct(self):
        """Accuracy is 0.5 for 2/4 correct. Hand check: 2/4 = 0.5."""
        self.assertAlmostEqual(accuracy(["a","b","a","b"], ["a","b","b","a"]), 0.5)

    def test_empty(self):
        """Accuracy on empty lists returns 0.0 without error."""
        self.assertEqual(accuracy([], []), 0.0)


class TestConfusionMatrix(unittest.TestCase):

    def test_perfect_3x3(self):
        """Perfect predictions produce a diagonal matrix.
        labels=[A,B,C], truth=[A,B,C], pred=[A,B,C]
        expected: [[1,0,0],[0,1,0],[0,0,1]]
        """
        mat = confusion_matrix(["A","B","C"], ["A","B","C"], ["A","B","C"])
        self.assertEqual(mat, [[1,0,0],[0,1,0],[0,0,1]])

    def test_one_off_2x2(self):
        """One wrong prediction fills off-diagonal.
        truth=[A,A,B], pred=[A,B,B]  ->  A row: [1,1], B row: [0,1]
        """
        mat = confusion_matrix(["A","A","B"], ["A","B","B"], ["A","B"])
        self.assertEqual(mat, [[1,1],[0,1]])

    def test_all_predicted_as_one_class(self):
        """Everything predicted as A: column A is full, rest are zero.
        truth=[A,B,B], pred=[A,A,A]  ->  A:[1,0], B:[2,0]
        """
        mat = confusion_matrix(["A","B","B"], ["A","A","A"], ["A","B"])
        self.assertEqual(mat, [[1,0],[2,0]])


class TestPerClassMetrics(unittest.TestCase):

    def test_binary_hand_calculation(self):
        """Binary classification; hand-calculated expected values.

        truth = [pos, pos, neg, neg, neg]
        pred  = [pos, neg, neg, neg, pos]

        For 'pos': TP=1 (pos->pos), FP=1 (neg->pos), FN=1 (pos->neg)
                   P=1/(1+1)=0.5, R=1/(1+1)=0.5, F1=0.5
        For 'neg': TP=2 (neg->neg at idx 2,3), FP=1 (pos->neg at idx 1), FN=1 (neg->pos at idx 4)
                   P=2/(2+1)=0.667, R=2/(2+1)=0.667, F1=0.667
        """
        y_true = ["pos","pos","neg","neg","neg"]
        y_pred = ["pos","neg","neg","neg","pos"]
        pc = per_class_metrics(y_true, y_pred, ["pos","neg"])

        self.assertAlmostEqual(pc["pos"]["precision"], 0.5,       places=6)
        self.assertAlmostEqual(pc["pos"]["recall"],    0.5,       places=6)
        self.assertAlmostEqual(pc["pos"]["f1"],        0.5,       places=6)
        self.assertAlmostEqual(pc["neg"]["precision"], 2/3,       places=6)
        self.assertAlmostEqual(pc["neg"]["recall"],    2/3,       places=6)
        self.assertAlmostEqual(pc["neg"]["f1"],        2/3,       places=6)

    def test_zero_support_label_gets_zero_metrics(self):
        """A label with zero support gets precision=recall=f1=0 without division error."""
        pc = per_class_metrics(["a","a"], ["a","a"], ["a","b"])
        self.assertEqual(pc["b"]["precision"], 0.0)
        self.assertEqual(pc["b"]["recall"],    0.0)
        self.assertEqual(pc["b"]["f1"],        0.0)
        self.assertEqual(pc["b"]["support"],   0)

    def test_support_counts(self):
        """support equals the true count for each label."""
        y_true = ["a","a","b","c"]
        pc = per_class_metrics(y_true, y_true, ["a","b","c"])
        self.assertEqual(pc["a"]["support"], 2)
        self.assertEqual(pc["b"]["support"], 1)
        self.assertEqual(pc["c"]["support"], 1)


class TestMacroF1(unittest.TestCase):

    def test_perfect_macro_f1(self):
        """Perfect predictions give macro_f1 = 1.0."""
        y = ["a","b","c"]
        self.assertAlmostEqual(macro_f1(y, y, ["a","b","c"]), 1.0)

    def test_hand_calculated(self):
        """Hand-calculated macro-F1 for binary case.
        From TestPerClassMetrics above:
        F1(pos)=0.5, F1(neg)=2/3  ->  macro = (0.5 + 2/3) / 2 = 7/12 ≈ 0.5833
        """
        y_true = ["pos","pos","neg","neg","neg"]
        y_pred = ["pos","neg","neg","neg","pos"]
        expected = (0.5 + 2/3) / 2      # = 7/12
        self.assertAlmostEqual(macro_f1(y_true, y_pred, ["pos","neg"]), expected, places=6)

    def test_ignores_zero_support_labels(self):
        """macro_f1 uses only labels that appear in y_true (active labels)."""
        # Only 'a' appears in y_true; 'b' has zero support -> ignored
        self.assertAlmostEqual(macro_f1(["a","a"], ["a","a"], ["a","b"]), 1.0)


class TestMajorityBaseline(unittest.TestCase):

    def test_clear_majority(self):
        """Returns the most frequent class."""
        self.assertEqual(majority_baseline(["a","a","b"]), "a")

    def test_empty(self):
        """Returns empty string for empty list."""
        self.assertEqual(majority_baseline([]), "")


class TestSplitRows(unittest.TestCase):

    def _make_rows(self, ids):
        return [{"id": i} for i in ids]

    def test_split_is_deterministic_independent_of_order(self):
        """Rows split to the same bucket regardless of input order."""
        ids = [f"row-{i:03d}" for i in range(20)]
        rows1 = self._make_rows(ids)
        rows2 = self._make_rows(ids[::-1])       # reversed order

        dev1, test1 = split_rows(rows1)
        dev2, test2 = split_rows(rows2)

        dev_ids1  = sorted(r["id"] for r in dev1)
        dev_ids2  = sorted(r["id"] for r in dev2)
        test_ids1 = sorted(r["id"] for r in test1)
        test_ids2 = sorted(r["id"] for r in test2)

        self.assertEqual(dev_ids1, dev_ids2)
        self.assertEqual(test_ids1, test_ids2)

    def test_split_covers_all_rows(self):
        """Every row ends up in exactly one of dev or test."""
        ids = [f"row-{i:03d}" for i in range(30)]
        rows = self._make_rows(ids)
        dev, test = split_rows(rows)
        all_out = sorted(r["id"] for r in dev + test)
        self.assertEqual(all_out, sorted(ids))

    def test_split_stable_across_two_calls(self):
        """Same rows -> same split on repeated calls."""
        ids = [f"stable-{i}" for i in range(10)]
        rows = self._make_rows(ids)
        dev1, test1 = split_rows(rows)
        dev2, test2 = split_rows(rows)
        self.assertEqual(sorted(r["id"] for r in dev1),  sorted(r["id"] for r in dev2))
        self.assertEqual(sorted(r["id"] for r in test1), sorted(r["id"] for r in test2))


class TestFileMissingError(unittest.TestCase):

    def test_clean_error_when_file_missing(self):
        """main() returns exit code 1 and prints a helpful message when CSV is missing."""
        import src.evaluate as ev
        import io
        from contextlib import redirect_stdout

        # Point the module at a path that doesn't exist
        orig = ev.LABELED_CSV
        ev.LABELED_CSV = Path("/nonexistent/path/that/never/exists.csv")
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = ev.main()
            output = buf.getvalue()
            self.assertEqual(code, 1)
            # Should mention the expected path and what columns to create
            self.assertIn("ERROR", output)
            self.assertIn("id,text,sentiment,event_type,source_type", output)
        finally:
            ev.LABELED_CSV = orig


class TestEvaluateWithTempCSV(unittest.TestCase):
    """Run main() end-to-end against a tiny synthetic CSV in a tempfile."""

    def _write_temp_csv(self, rows, fieldnames):
        tmpf = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        )
        writer = csv.DictWriter(tmpf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        tmpf.close()
        return Path(tmpf.name)

    def test_valid_csv_exits_zero(self):
        """main() exits 0 on a valid labeled CSV."""
        import src.evaluate as ev
        import io
        from contextlib import redirect_stdout

        rows = [
            {"id": "e1", "text": "GDP strong unemployment down inflation fading",
             "sentiment": "positive", "event_type": "Macroeconomic", "source_type": "news"},
            {"id": "e2", "text": "missile strikes escalate military conflict sanctions",
             "sentiment": "negative", "event_type": "Geopolitical", "source_type": "news"},
            {"id": "e3", "text": "bank defaults regional credit spreads widen sharply",
             "sentiment": "negative", "event_type": "Credit Event", "source_type": "news"},
            {"id": "e4", "text": "Apple unveils new iPhone feature set launch event",
             "sentiment": "positive", "event_type": "Product Launch", "source_type": "social"},
        ]
        tmp = self._write_temp_csv(rows, ["id","text","sentiment","event_type","source_type"])
        orig = ev.LABELED_CSV
        orig_md = ev.RESULTS_MD
        # Redirect RESULTS_MD to a temp file too
        tmp_md = Path(tempfile.mktemp(suffix=".md"))
        ev.LABELED_CSV = tmp
        ev.RESULTS_MD  = tmp_md
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = ev.main()
            self.assertEqual(code, 0)
            output = buf.getvalue()
            # Core sections must appear in the output
            self.assertIn("DEV", output)
            self.assertIn("TEST", output)
            self.assertIn("Accuracy", output)
            self.assertIn("Macro-F1", output)
        finally:
            ev.LABELED_CSV = orig
            ev.RESULTS_MD  = orig_md
            tmp.unlink(missing_ok=True)
            tmp_md.unlink(missing_ok=True)

    def test_invalid_sentiment_label_exits_one(self):
        """main() exits 1 and reports error on invalid sentiment value."""
        import src.evaluate as ev
        import io
        from contextlib import redirect_stdout

        rows = [{"id": "bad1", "text": "some text", "sentiment": "INVALID",
                 "event_type": "Earnings", "source_type": "news"}]
        tmp = self._write_temp_csv(rows, ["id","text","sentiment","event_type","source_type"])
        orig = ev.LABELED_CSV
        ev.LABELED_CSV = tmp
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = ev.main()
            self.assertEqual(code, 1)
            self.assertIn("INVALID", buf.getvalue())
        finally:
            ev.LABELED_CSV = orig
            tmp.unlink(missing_ok=True)

    def test_duplicate_id_exits_one(self):
        """main() exits 1 when two rows share the same id."""
        import src.evaluate as ev
        import io
        from contextlib import redirect_stdout

        rows = [
            {"id": "dup", "text": "text one", "sentiment": "neutral",
             "event_type": "Other", "source_type": "news"},
            {"id": "dup", "text": "text two", "sentiment": "neutral",
             "event_type": "Other", "source_type": "news"},
        ]
        tmp = self._write_temp_csv(rows, ["id","text","sentiment","event_type","source_type"])
        orig = ev.LABELED_CSV
        ev.LABELED_CSV = tmp
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = ev.main()
            self.assertEqual(code, 1)
            self.assertIn("duplicate", buf.getvalue().lower())
        finally:
            ev.LABELED_CSV = orig
            tmp.unlink(missing_ok=True)

    def test_impact_label_section_appears(self):
        """When impact_label column is present, the ordering section appears in output."""
        import src.evaluate as ev
        import io
        from contextlib import redirect_stdout

        rows = [
            {"id": "i1", "text": "GDP strong unemployment down",
             "sentiment": "positive", "event_type": "Macroeconomic",
             "source_type": "news", "impact_label": "low"},
            {"id": "i2", "text": "missile strikes escalate conflict sanctions",
             "sentiment": "negative", "event_type": "Geopolitical",
             "source_type": "news", "impact_label": "high"},
        ]
        tmp = self._write_temp_csv(
            rows, ["id","text","sentiment","event_type","source_type","impact_label"])
        orig = ev.LABELED_CSV
        orig_md = ev.RESULTS_MD
        tmp_md = Path(tempfile.mktemp(suffix=".md"))
        ev.LABELED_CSV = tmp
        ev.RESULTS_MD  = tmp_md
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = ev.main()
            self.assertEqual(code, 0)
            self.assertIn("impact_label", buf.getvalue().lower())
        finally:
            ev.LABELED_CSV = orig
            ev.RESULTS_MD  = orig_md
            tmp.unlink(missing_ok=True)
            tmp_md.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
