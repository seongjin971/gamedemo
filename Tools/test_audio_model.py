#!/usr/bin/env python3
"""Run engine-independent audio tests using Mono bundled with a Unity Editor."""
import argparse
import os
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unity-contents", type=pathlib.Path, required=True,
                        help="Unity.app/Contents on macOS, or Unity Editor/Data on Windows")
    args = parser.parse_args()
    candidates = [args.unity_contents / "Resources/Scripting/MonoBleedingEdge",
                  args.unity_contents / "MonoBleedingEdge"]
    mono_root = next((p for p in candidates if p.exists()), None)
    if mono_root is None:
        parser.error("MonoBleedingEdge was not found in this Editor")
    mono = mono_root / "bin" / ("mono.exe" if os.name == "nt" else "mono")
    compiler = mono_root / "lib/mono/4.5/mcs.exe"
    sources = [ROOT / "Unity/Vesper/Assets/Vesper/Expansion/WeatherW11/Core/AudioModel.cs",
               ROOT / "Tools/tests/AudioModelTests.cs"]
    with tempfile.TemporaryDirectory(prefix="vesper-audio-tests-") as temp:
        exe = pathlib.Path(temp) / "AudioModelTests.exe"
        subprocess.run([str(mono), str(compiler), "-warnaserror", "-out:" + str(exe), *map(str, sources)], check=True)
        subprocess.run([str(mono), str(exe)], check=True)

if __name__ == "__main__":
    main()
