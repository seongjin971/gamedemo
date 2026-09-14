import hashlib
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("prepare_wwise", ROOT / "Tools/prepare_wwise.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AuthoringPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = module.plan(ROOT)

    def test_every_source_imported_once_without_renaming_files(self):
        expected = {p.relative_to(ROOT).as_posix() for p in (ROOT / "sfx").rglob("*.wav")}
        actual = [m["source"] for m in self.plan["media"]]
        self.assertEqual(len(actual), 76)
        self.assertEqual(len(actual), len(set(actual)))
        self.assertEqual(set(actual), expected)
        for media in self.plan["media"]:
            self.assertEqual(hashlib.sha256((ROOT / media["source"]).read_bytes()).hexdigest(), media["sha256"])

    def test_footstep_switch_uses_requested_surface_names(self):
        assignments = [x["args"] for x in self.plan["calls"] if x["uri"].endswith("switchContainer.addAssignment")]
        foot = [x for x in assignments if "\\Footsteps\\" in x["child"]]
        self.assertEqual({x["stateOrSwitch"].split("\\")[-1] for x in foot}, {"Mud", "Gravel", "Snow", "Rock"})
        self.assertFalse(any(m["loop"] for m in self.plan["media"] if "\\Footsteps\\" in m["objectPath"]))

    def test_parameter_ranges_match_protocol(self):
        parameters = {x["args"]["name"]: x["args"] for x in self.plan["calls"] if x["args"].get("type") == "GameParameter"}
        self.assertEqual((parameters["TimeOfDay"]["@Min"], parameters["TimeOfDay"]["@Max"]), (0, 24))
        self.assertEqual((parameters["RainIntensity"]["@Min"], parameters["RainIntensity"]["@Max"]), (0, 1))

    def test_bank_contains_all_runtime_events(self):
        bank = next(x["args"] for x in self.plan["calls"] if x["uri"].endswith("soundbank.setInclusions"))
        self.assertEqual({x["object"].split("\\")[-1] for x in bank["inclusions"]},
                         {"Play_Footstep", "Play_World_Ambience", "Play_Lake_Ambience"})
        self.assertTrue(all(set(x["filter"]) == {"events", "structures", "media"} for x in bank["inclusions"]))

    def test_volume_curves_are_ordered_and_midnight_is_continuous(self):
        for layer in self.plan["rtpc_volume_curves_to_author"]:
            points = layer["points"]
            self.assertTrue(all(a[0] < b[0] for a, b in zip(points, points[1:])))
            if layer["rtpc"] == "TimeOfDay":
                self.assertEqual(points[0][1], points[-1][1])

    def test_no_overwrite_or_unrequested_playback(self):
        for item in self.plan["calls"]:
            if item["uri"].endswith("object.create"):
                self.assertEqual(item["args"]["onNameConflict"], "fail")
            self.assertNotIn("transport", item["uri"])
            self.assertNotIn("soundbank.generate", item["uri"])
        self.assertEqual(self.plan["status"], "AUTHORING_PLAN_NOT_APPLIED")

if __name__ == "__main__":
    unittest.main()
