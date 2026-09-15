#!/usr/bin/env python3
"""Create the Director's independent sound bank through official WAAPI.

The AI never supplies WAAPI paths or code. It selects catalog IDs; this trusted
authoring step makes their events available once, before the editor is used.
Existing W11 mix rules and source files are preserved. Wwise may reconcile shared
MediaIDs when saving; always regenerate and ship Init, W11 and Director together.
"""
import argparse
import json
import pathlib
from director_catalog import ROOT, OUTPUT
from prepare_wwise import native_project_path


def author(project, url, shared_media_only=False):
    from waapi import WaapiClient
    catalog = json.loads(OUTPUT.read_text())
    with WaapiClient(url, allow_exception=True) as client:
        def call(uri, **args):
            result = client.call("ak.wwise.core." + uri, args)
            if result is None:
                raise RuntimeError("WAAPI failed: " + uri)
            return result

        opened = client.call("ak.wwise.core.object.get", {"from": {"ofType": ["Project"]}},
                             options={"return": ["filePath"]})["return"]
        if len(opened) != 1 or native_project_path(opened[0]["filePath"]).resolve() != project.resolve():
            raise RuntimeError("The requested VesperAudio project must be open")
        existing = client.call("ak.wwise.core.object.get", {"from": {"ofType": ["WorkUnit"]}},
                               options={"return": ["name"]})["return"]
        if shared_media_only:
            if not any(x["name"] == "Vesper_Director" for x in existing):
                raise RuntimeError("Create the Director work units first")
            call("soundbank.setInclusions", soundbank=r"\SoundBanks\Vesper_Director\Vesper_Director", operation="replace",
                 inclusions=[{"object": r"\Events\Vesper_Director" + "\\" + s["eventName"], "filter": ["events", "structures"]}
                             for s in catalog["sounds"] if s["available"]])
            call("project.save")
            print("Director structures use the already shipped W11 media bank.")
            return
        if any(x["name"] == "Vesper_Director" for x in existing):
            raise RuntimeError("Director authoring already exists; use the checked-in bank or review changes manually")

        def create(parent, kind, name, **properties):
            call("object.create", parent=parent, type=kind, name=name, onNameConflict="fail", **properties)
            return parent + "\\" + name

        audio = create(r"\Containers", "WorkUnit", "Vesper_Director")
        events = create(r"\Events", "WorkUnit", "Vesper_Director")
        bank_unit = create(r"\SoundBanks", "WorkUnit", "Vesper_Director")
        parameters = create(r"\Game Parameters", "WorkUnit", "Vesper_Director")
        gain = create(parameters, "GameParameter", "SD_Gain", **{"@Min": -96, "@Max": 0, "@InitialValue": -96})
        inclusions = []
        for sound in catalog["sounds"]:
            if not sound["available"]:
                continue
            pool = create(audio, "RandomSequenceContainer", sound["id"], **{
                "@RandomOrSequence": 1, "@PlayMechanismStepOrContinuous": 1,
                "@RandomAvoidRepeating": True, "@RandomAvoidRepeatingCount": 1,
                "@Volume": -6, "@OverridePositioning": True, "@ListenerRelativeRouting": True,
                "@3DPosition": 0, "@3DSpatialization": 1, "@EnableAttenuation": False,
                "@OverrideVirtualVoice": True, "@BelowThresholdBehavior": 2, "@VirtualVoiceQueueBehavior": 1})
            # Distance and fade envelopes are applied per game object through SD_Gain.
            # This allows the same bank to work for arbitrary scene target positions/radii.
            call("object.set", objects=[{"object": pool, "listMode": "replaceAll", "@RTPC": [{
                "type": "RTPC", "name": "", "@PropertyName": "Volume", "@ControlInput": gain,
                "@Curve": {"type": "Curve", "points": [{"x": -96, "y": -96, "shape": "Linear"},
                                                         {"x": 0, "y": 0, "shape": "Linear"}]}}]}])
            imports = []
            for i, source in enumerate(sound["files"]):
                file = pathlib.Path(source["path"])
                imports.append({"audioFile": str(ROOT / file), "objectPath": pool + "\\<Sound SFX>Sample_" + str(i + 1),
                                "originalsSubFolder": "Vesper_W11/" + file.parent.relative_to("sfx").as_posix()})
            call("audio.import", importOperation="createNew", default={"importLanguage": "SFX"}, imports=imports)
            if sound["loop"]:
                for item in imports:
                    call("object.setProperty", object=item["objectPath"].replace("<Sound SFX>", ""),
                         property="IsLoopingEnabled", value=True)
            event = create(events, "Event", sound["eventName"])
            create(event, "Action", "Play", **{"@ActionType": 1, "@Target": pool})
            inclusions.append({"object": event, "filter": ["events", "structures"]})
        bank = create(bank_unit, "SoundBank", catalog["bankName"])
        call("soundbank.setInclusions", soundbank=bank, operation="add", inclusions=inclusions)
        call("project.save")
        print("Created", len(inclusions), "Director events; generate Mac/Windows banks next.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=pathlib.Path, required=True)
    parser.add_argument("--url", default="ws://127.0.0.1:8085/waapi")
    parser.add_argument("--shared-media-only", action="store_true", help="Update only the existing Director bank's inclusion filters")
    args = parser.parse_args()
    author(args.project, args.url, args.shared_media_only)
