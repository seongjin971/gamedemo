#!/usr/bin/env python3
"""Prepare an inspectable Wwise authoring plan; apply it to an explicitly named open project.

The default operation writes a JSON plan only. --apply requires the official waapi-client
package and Wwise Authoring with WAAPI enabled. It never installs an SDK or generates banks.
"""
import argparse
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
OWN = "Vesper_W11"
BASES = {"audio": "Actor-Mixer Hierarchy", "events": "Events", "switches": "Switches",
         "states": "States", "rtpc": "Game Parameters", "banks": "SoundBanks"}


def parent(kind):
    return "\\" + BASES[kind] + "\\" + OWN


def plan(root=ROOT):
    calls = []
    media = []

    def call(uri, **args):
        calls.append({"uri": "ak.wwise.core." + uri, "args": args})

    def create(where, kind, name, **props):
        call("object.create", parent=where, type=kind, name=name, onNameConflict="fail", **props)
        return where + "\\" + name

    for kind, folder in BASES.items():
        create("\\" + folder, "WorkUnit", OWN)
    surface = create(parent("switches"), "SwitchGroup", "SurfaceType")
    switches = {s: create(surface, "Switch", s) for s in ("Mud", "Gravel", "Snow", "Rock")}
    area = create(parent("states"), "StateGroup", "Area")
    states = {s: create(area, "State", s) for s in ("Forest", "SnowMountain")}
    create(parent("rtpc"), "GameParameter", "TimeOfDay", **{"@Min": 0, "@Max": 24, "@InitialValue": 8})
    create(parent("rtpc"), "GameParameter", "RainIntensity", **{"@Min": 0, "@Max": 1, "@InitialValue": 0})
    steps = create(parent("audio"), "SwitchContainer", "Footsteps")
    call("object.setReference", object=steps, reference="SwitchGroupOrStateGroup", value=surface)
    call("object.setReference", object=steps, reference="DefaultSwitchOrState", value=switches["Gravel"])

    used = set()

    def pool(where, name, relative_folder, loop=False):
        path = create(where, "RandomSequenceContainer", name,
                      **{"@RandomOrSequence": 0, "@PlayMechanismStepOrContinuous": 0})
        files = sorted((root / "sfx" / relative_folder).glob("*.wav"))
        if not files:
            raise ValueError("No WAV files: " + relative_folder)
        imports = []
        for i, file in enumerate(files):
            relative = file.relative_to(root).as_posix()
            used.add(relative)
            name = re.sub(r"[^a-zA-Z0-9_]", "_", file.stem) + "_" + str(i + 1)
            obj = path + "\\<Sound SFX>" + name
            # Paths remain portable in the reviewed plan; they become absolute only during apply.
            imports.append({"audioFile": relative, "objectPath": obj})
            media.append({"source": relative, "objectPath": obj, "loop": loop,
                          "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
        call("audio.import", importOperation="createNew", default={"importLanguage": "SFX"}, imports=imports)
        if loop:
            for item in imports:
                call("object.setProperty", object=item["objectPath"].replace("<Sound SFX>", ""), property="IsLoopingEnabled", value=True)
        return path

    for label, folder in {"Mud": "wet", "Gravel": "gravel", "Snow": "snow", "Rock": "rock"}.items():
        child = pool(steps, label, "footstep/footstep " + folder)
        call("switchContainer.addAssignment", child=child, stateOrSwitch=switches[label])

    # Continuous state switching and the documented RTPC mix are intentionally left as authoring review steps.
    world = create(parent("audio"), "SwitchContainer", "World_Ambience")
    call("object.setReference", object=world, reference="SwitchGroupOrStateGroup", value=area)
    call("object.setReference", object=world, reference="DefaultSwitchOrState", value=states["Forest"])
    forest = create(world, "BlendContainer", "Forest")
    mountain = create(world, "BlendContainer", "SnowMountain")
    for child, state in [(forest, states["Forest"]), (mountain, states["SnowMountain"])]:
        call("switchContainer.addAssignment", child=child, stateOrSwitch=state)
    layers = []
    for where, name, folder, parameter, points in [
        (forest, "Day_Wind", "ambience/morning/background", "TimeOfDay", [[0,-96],[5,-24],[8,0],[16,0],[19,-96],[24,-96]]),
        (forest, "Night_Bed", "ambience/night/background", "TimeOfDay", [[0,0],[5,0],[8,-96],[17,-96],[20,0],[24,0]]),
        (forest, "Rain_Bed", "ambience/rainnight/background", "RainIntensity", [[0,-96],[0.15,-24],[0.5,-8],[1,0]]),
        (forest, "Rain_Heavy", "ambience/rainnight/rainbackground", "RainIntensity", [[0,-96],[0.4,-96],[0.7,-10],[1,0]]),
        (mountain, "Snow_Wind", "ambience/snow/background", None, [])
    ]:
        path = pool(where, name, folder, loop=True)
        layers.append({"object": path, "rtpc": parameter, "property": "Volume", "points": points})
    lake = pool(parent("audio"), "Lake_Ambience", "ambience/morning/object", loop=True)

    # Import the remaining source folders into a separate library for sound-design review.
    library = create(parent("audio"), "ActorMixer", "Source_Library")
    for folder in sorted({f.parent for f in (root / "sfx").rglob("*.wav") if f.relative_to(root).as_posix() not in used}):
        relative = folder.relative_to(root / "sfx").as_posix()
        pool(library, re.sub(r"[^a-zA-Z0-9_]", "_", relative), relative)

    events = []
    for name, target in [("Play_Footstep", steps), ("Play_World_Ambience", world), ("Play_Lake_Ambience", lake)]:
        event = create(parent("events"), "Event", name)
        create(event, "Action", "Play", **{"@ActionType": 1, "@Target": target})
        events.append(event)
    bank = create(parent("banks"), "SoundBank", OWN)
    call("soundbank.setInclusions", soundbank=bank, operation="add",
         inclusions=[{"object": e, "filter": ["events", "structures", "media"]} for e in events])
    return {
        "status": "AUTHORING_PLAN_NOT_APPLIED", "bank": OWN,
        "scope": "Creates game syncs, imports, containers, events and bank membership. Authoring settings below must be completed before banks are generated.",
        "calls": calls, "media": media, "rtpc_volume_curves_to_author": layers,
        "authoring_required": [
            "Set World_Ambience Switch Container to Continuous; set Forest/SnowMountain crossfades to 1.5 seconds.",
            "Apply each RTPC Volume curve listed in rtpc_volume_curves_to_author before auditioning the combined mix.",
            "Set Lake_Ambience to game-defined 3D positioning and attenuation: 0m=0dB, 8m=-3dB, 20m=-18dB, 40m=-96dB.",
            "Audition wet footstep files as the proposed Mud mapping. Concrete files are imported to Source_Library, not mixed into Rock.",
            "Author sparse random bird/bug/owl/wind cues from Source_Library, with TimeOfDay/RainIntensity gating. Thunder needs visual flash synchronization if enabled.",
            "Generate Mac/Windows banks, copy all generated media and metadata into Unity Assets/StreamingAssets/Audio/GeneratedSoundBanks/<platform>, and configure Wwise's bank base path accordingly.",
            "Validate actual Unity SDK compilation, Wwise Profiler values, audible playback and Windows player before claiming completion."
        ]
    }


def apply(data, expected_project):
    try:
        from waapi import WaapiClient
    except ImportError as exc:
        raise RuntimeError("Install the official waapi-client package in a Python virtual environment first.") from exc
    expected = expected_project.resolve()
    with WaapiClient() as client:
        result = client.call("ak.wwise.core.object.get", {"from": {"ofType": ["Project"]}}, options={"return": ["filePath"]})
        projects = result.get("return", []) if result else []
        if len(projects) != 1 or pathlib.Path(projects[0]["filePath"]).resolve() != expected:
            raise RuntimeError("Open the explicitly specified Wwise project before applying the plan.")
        # Never merge a partially applied plan or overwrite an existing project's work units.
        existing = client.call("ak.wwise.core.object.get", {"from": {"ofType": ["WorkUnit"]}}, options={"return": ["name", "path"]})
        if not existing or any(x["name"] == OWN for x in existing["return"]):
            raise RuntimeError("Vesper_W11 work units already exist (or inspection failed). Review them manually; this tool never overwrites them.")
        reserved = {"SurfaceType", "Area", "TimeOfDay", "RainIntensity", "Play_Footstep", "Play_World_Ambience", "Play_Lake_Ambience", OWN}
        objects = client.call("ak.wwise.core.object.get",
                              {"from": {"ofType": ["SwitchGroup", "StateGroup", "GameParameter", "Event", "SoundBank"]}},
                              options={"return": ["name", "path"]})
        if not objects or any(x["name"] in reserved for x in objects["return"]):
            raise RuntimeError("A protocol name already exists (or inspection failed). Reconcile existing sound-design work before importing.")
        client.call("ak.wwise.core.undo.beginGroup", {})
        try:
            for item in data["calls"]:
                args = json.loads(json.dumps(item["args"]))
                for entry in args.get("imports", []):
                    entry["audioFile"] = str((ROOT / entry["audioFile"]).resolve())
                if client.call(item["uri"], args) is None:
                    raise RuntimeError("WAAPI failed: " + item["uri"])
            client.call("ak.wwise.core.undo.endGroup", {"displayName": "Create Vesper W11 audio scaffold"})
        except Exception:
            client.call("ak.wwise.core.undo.cancelGroup", {})
            raise
        client.call("ak.wwise.core.project.save", {})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=ROOT / "Audio/wwise-authoring-plan.json")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--project", type=pathlib.Path, help="Exact .wproj path, required for --apply")
    args = parser.parse_args()
    data = plan()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Prepared {len(data['media'])} WAV mappings and {len(data['calls'])} WAAPI calls: {args.output}")
    if args.apply:
        if not args.project:
            parser.error("--apply requires --project")
        apply(data, args.project)
        print("Scaffold applied. Complete the listed authoring settings before generating banks.")

if __name__ == "__main__":
    main()
