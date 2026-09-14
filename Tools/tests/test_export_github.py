import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("export_github", ROOT / "Tools/export_github.py")
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


class UnityExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.root_patch = patch.object(export, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def write(self, path):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"example")

    def requirements(self):
        return export.unity_requirements(list((self.root / "Unity/Vesper/Assets").rglob("*")))

    def test_ignored_sdk_docs_and_symbols_do_not_block_export(self):
        (self.root / ".gitignore").write_text("/Unity/Vesper/Assets/Wwise/Documentation/\n/Unity/Vesper/Assets/Wwise/Documentation.meta\n*.pdb\n*.pdb.meta\n")
        for path in ["Documentation/api.html", "Documentation.meta", "engine.pdb", "engine.pdb.meta"]:
            self.write("Unity/Vesper/Assets/Wwise/" + path)
        self.assertEqual(self.requirements(), {"Unity/Vesper/Assets/Wwise.meta"})

    def test_bundle_preserves_binary_but_only_requires_bundle_metadata(self):
        bundle = "Unity/Vesper/Assets/Engine.bundle"
        binary = bundle + "/Contents/MacOS/Engine"
        self.write(binary)
        self.assertEqual(self.requirements(), {bundle + ".meta", binary})

    def test_regular_asset_and_folder_metadata_remain_required(self):
        path = "Unity/Vesper/Assets/Game/Audio.cs"
        self.write(path)
        self.assertEqual(self.requirements(), {path, path + ".meta", "Unity/Vesper/Assets/Game.meta"})

    def test_soundbanks_are_included_with_metadata(self):
        path = "Unity/Vesper/Assets/StreamingAssets/Vesper_W11.bnk"
        self.write(path)
        self.assertIn(path, self.requirements())
        self.assertIn(path + ".meta", self.requirements())


if __name__ == "__main__":
    unittest.main()
