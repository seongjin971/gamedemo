#!/usr/bin/env python3
"""Build the checked-in, asset-grounded Sound Director catalog. No AI inference here."""
import hashlib
import json
import pathlib
import wave

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Unity/Vesper/Assets/Vesper/SoundDirector/Resources/VesperSoundCatalog.json"
POOLS = [
    ("day_wind", "ambience/morning/background", "Soft daytime wind bed; calm outdoor forest", True),
    ("river", "ambience/morning/object", "Flowing river water; local water source, pond or lakeside", True),
    ("birds", "ambience/morning/random one shot/bird", "Short daytime bird calls; lively, safe woodland", False),
    ("day_bugs", "ambience/morning/random one shot/bug", "Short daytime insect details", False),
    ("grass", "ambience/morning/random one shot/grass", "Dry grass rustle; movement and subtle unease", False),
    ("day_gusts", "ambience/morning/random one shot/wind", "Short gusts of wind in daytime woodland", False),
    ("night_bed", "ambience/night/background", "Continuous night ambience; quiet, dark outdoor setting", True),
    ("night_bugs", "ambience/night/oneshot/bug", "Night insect calls; intermittent nocturnal detail", False),
    ("owls", "ambience/night/oneshot/owl", "Owl calls; sparse nocturnal woodland", False),
    ("wolves", "ambience/night/oneshot/wolf", "Distant wolf calls; danger, isolation, uneasy night", False),
    ("rain_bed", "ambience/rainnight/background", "Steady rainy night ambience", True),
    ("heavy_rain", "ambience/rainnight/rainbackground", "Continuous heavy rainfall; storm without thunder", True),
    ("wet_grass", "ambience/rainnight/random/randomgrass", "Short wet vegetation rustle", False),
    ("rain_gusts", "ambience/rainnight/random/randomwind", "Intermittent windy rain gusts", False),
    ("snow_bed", "ambience/snow/background", "Continuous cold wind and snow ambience; exposed mountain", True),
    ("snow_gusts", "ambience/snow/random/randomwind", "Cold mountain wind gusts; bleak, exposed space", False),
    ("snow_wolves", "ambience/snow/random/randomwolf", "Distant wolf call in snowy mountains", False),
    ("thunder", "ambience/rainnight/thunder", "Thunder; unavailable until synchronized visual lightning exists", False),
] + [("footstep_" + name, "footstep/footstep " + folder,
       name + " footsteps; preserved by the existing animation/contact system", False)
      for name, folder in [("gravel", "gravel"), ("snow", "snow"), ("mud", "wet"), ("rock", "rock"), ("concrete", "concreate")]]


def build(root=ROOT):
    sounds = []
    for sound_id, folder, description, loop in POOLS:
        files = []
        for path in sorted((root / "sfx" / folder).glob("*.wav")):
            with wave.open(str(path)) as wav:
                seconds = round(wav.getnframes() / wav.getframerate(), 3)
            files.append({"path": path.relative_to(root).as_posix(),
                          "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "seconds": seconds})
        if not files:
            raise ValueError("Empty sound pool: " + folder)
        available = not (sound_id.startswith("footstep_") or sound_id == "thunder")
        sounds.append({"id": sound_id, "description": description, "loop": loop,
                       "available": available, "eventName": "SD_Play_" + sound_id if available else "",
                       "files": files})
    known = {f["path"] for s in sounds for f in s["files"]}
    actual = {p.relative_to(root).as_posix() for p in (root / "sfx").rglob("*.wav")}
    if known != actual:
        raise ValueError("Every source WAV must appear exactly once in the catalog")
    encoded = json.dumps(sounds, sort_keys=True).encode()
    return {"version": 1, "revision": hashlib.sha256(encoded).hexdigest(),
            "bankName": "Vesper_Director", "mediaBankName": "Vesper_W11", "sounds": sounds}


if __name__ == "__main__":
    catalog = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Catalog:", len(catalog["sounds"]), "pools;", sum(len(s["files"]) for s in catalog["sounds"]), "WAVs")
