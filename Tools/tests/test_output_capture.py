import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("validate_wwise_assets", ROOT / "Tools/validate_wwise_assets.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class OutputCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "capture.wav"

    def capture(self, samples):
        with wave.open(str(self.path), "wb") as out:
            out.setparams((2, 2, 48000, 0, "NONE", "not compressed"))
            out.writeframes(struct.pack("<" + "h" * len(samples), *samples))

    def test_non_silent_pcm_is_measured(self):
        self.capture([1000, -1000] * 480)
        result = validator.measure_capture(self.path)
        self.assertEqual(result["sampleRate"], 48000)
        self.assertEqual(result["channels"], 2)
        self.assertEqual(result["clippedSamples"], 0)
        self.assertAlmostEqual(result["seconds"], .01)

    def test_silence_and_clipping_are_rejected(self):
        for samples in ([0, 0] * 100, [32767, -32768] * 100):
            with self.subTest(samples=samples[:2]):
                self.capture(samples)
                with self.assertRaises(AssertionError):
                    validator.measure_capture(self.path)

    def test_empty_capture_is_rejected(self):
        self.capture([])
        with self.assertRaises(AssertionError):
            validator.measure_capture(self.path)

    def test_truncated_capture_is_rejected(self):
        self.capture([1000, -1000] * 100)
        self.path.write_bytes(self.path.read_bytes()[:-20])
        with self.assertRaises(AssertionError):
            validator.measure_capture(self.path)


if __name__ == "__main__":
    unittest.main()
