#!/usr/bin/env python3
"""Validate source grounding, Wwise bank dependencies, contract JSON and real PCM captures."""
import argparse
import array
import hashlib
import json
import math
import pathlib
import struct
import sys
import xml.etree.ElementTree as ET
from director_catalog import ROOT, OUTPUT, build


def signal(path):
    data = path.read_bytes()
    assert data[:4] == b"RIFF" and data[8:12] == b"WAVE"
    i, samples, rate, channels = 12, None, None, None
    while i + 8 <= len(data):
        tag, size = data[i:i + 4], struct.unpack_from("<I", data, i + 4)[0]
        assert i + 8 + size <= len(data), "Truncated capture"
        chunk = data[i + 8:i + 8 + size]; i += 8 + size + (size % 2)
        if tag == b"fmt ":
            fmt, channels, rate, _, _, bits = struct.unpack_from("<HHIIHH", chunk)
            assert bits == 16 and fmt in (1, 65534)
            if fmt == 65534:
                assert chunk[24:40] == bytes.fromhex("0100000000001000800000aa00389b71")
        if tag == b"data":
            samples = array.array("h", chunk)
            if sys.byteorder != "little": samples.byteswap()
    assert samples and rate and channels
    peak = max(map(abs, samples)) / 32768
    rms = math.sqrt(sum(s * s for s in samples) / len(samples)) / 32768
    clipped = sum(abs(s) >= 32767 for s in samples)
    assert clipped == 0, "Clipped output: " + path.name
    return {"seconds": len(samples) / (rate * channels), "rms": rms, "peak": peak, "clippedSamples": clipped}


def validate(captures=False):
    catalog = json.loads(OUTPUT.read_text())
    assert catalog == build(), "Catalog no longer matches source files"
    active = [s for s in catalog["sounds"] if s["available"]]
    expected = {s["eventName"] for s in active}
    saved = ET.parse(ROOT / "Audio/VesperAudio/Containers/Vesper_Director.wwu")
    assert len(saved.findall(".//Sound")) == sum(len(s["files"]) for s in active)
    banks = {}
    for platform in ["Mac", "Windows"]:
        folder = ROOT / "Unity/Vesper/Assets/StreamingAssets/Audio/GeneratedSoundBanks" / platform
        director = json.loads((folder / "Vesper_Director.json").read_text())["SoundBanksInfo"]["SoundBanks"][0]
        media = json.loads((folder / "Vesper_W11.json").read_text())["SoundBanksInfo"]["SoundBanks"][0]
        assert {event["Name"] for event in director["Events"]} == expected
        assert {item["Id"] for item in director["Media"]} <= {item["Id"] for item in media["Media"]}
        assert all(item["Location"] == "OtherBank" for item in director["Media"])
        bank = folder / "Vesper_Director.bnk"
        assert bank.read_bytes()[:4] == b"BKHD" and bank.stat().st_size < 100000
        banks[platform] = {"events": len(expected), "bytes": bank.stat().st_size,
                           "mediaBank": "Vesper_W11", "sha256": hashlib.sha256(bank.read_bytes()).hexdigest()}
    output = ROOT / "Audio/Director"
    request = json.loads((output / "request-contract.json").read_text())
    context = json.loads(request["input"][1]["content"])
    assert '"가까이"\n' in context["request"] and "한글" in context["request"]
    assert request["store"] is False
    schema = request["text"]["format"]["schema"]
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])
    choices = schema["properties"]["layers"]["items"]["properties"]
    assert set(choices["soundId"]["enum"]) == {s["id"] for s in active}
    report = {"catalogFiles": 76, "availablePools": len(active), "banks": banks,
              "liveAIValidated": False, "humanListeningValidated": False, "signals": {}}
    if captures:
        for scene in ["w11", "lab"]:
            runtime = json.loads((output / (scene + "-playback.json")).read_text())
            assert runtime["failures"] == 0 and not runtime["errors"], scene + " playback checks failed"
            signals = {path.stem.split("playback-", 1)[1]: signal(path) for path in output.glob(scene + "-playback-*.wav")}
            for name in ["full-direction", "water-near"]:
                assert signals[name]["rms"] > .00001 and signals[name]["seconds"] >= 1.5, scene + " silent " + name
            assert signals["water-far"]["rms"] < max(.000001, signals["water-near"]["rms"] * .05), scene + " water does not fade at distance"
            report["signals"][scene] = signals
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures", action="store_true")
    args = parser.parse_args()
    report = validate(args.captures)
    (ROOT / "Audio/Director/audio-validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
