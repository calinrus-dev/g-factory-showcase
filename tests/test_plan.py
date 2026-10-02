import json
import subprocess
import sys
import unittest
from pathlib import Path

from gfactory.plan import ClipPlan, Cut, PlanError


class PlanTests(unittest.TestCase):
    def test_final_duration_includes_branding(self):
        plan = ClipPlan(200, (Cut(10, 60), Cut(100, 150)), 2, 3, 105)
        self.assertEqual(plan.duration_us, 105)
        self.assertEqual(plan.report()["cuts"][1]["timeline_end_us"], 102)

    def test_branding_cannot_push_past_limit(self):
        with self.assertRaises(PlanError):
            ClipPlan(900_000_000, (Cut(0, 900_000_000),), intro_us=1)

    def test_order_and_repeated_material_are_preserved(self):
        plan = ClipPlan(100, (Cut(50, 70), Cut(0, 10), Cut(50, 70)))
        self.assertEqual(plan.duration_us, 50)
        self.assertEqual([x["timeline_start_us"] for x in plan.report()["cuts"]], [0, 20, 30])

    def test_invalid_ranges(self):
        for cut in (Cut(-1, 4), Cut(5, 5), Cut(8, 7), Cut(0, 101)):
            with self.subTest(cut=cut), self.assertRaises(PlanError):
                ClipPlan(100, (cut,))

    def test_invalid_numeric_types(self):
        for value in (True, 1.5, float("nan"), float("inf"), "12", None):
            with self.subTest(value=value), self.assertRaises(PlanError):
                ClipPlan(100, (Cut(0, value),))

    def test_empty_timeline(self):
        with self.assertRaises(PlanError):
            ClipPlan(100, ())

    def test_unknown_fields_and_versions_rejected(self):
        data = json.loads(Path("examples/clip-plan.json").read_text())
        for patch in ({"version": 2}, {"version": True}, {"surprise": 1}, {"cuts": {}}):
            with self.subTest(patch=patch), self.assertRaises(PlanError):
                ClipPlan.from_dict(data | patch)

    def test_example_cli(self):
        result = subprocess.run(
            [sys.executable, "-m", "gfactory.plan", "examples/clip-plan.json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["duration_us"], 185_000_000)

    def test_missing_manifest_cli_fails_cleanly(self):
        result = subprocess.run(
            [sys.executable, "-m", "gfactory.plan", "missing.json"], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
