#!/usr/bin/env python3
"""Compile W11, Sound Director and actual W10 dependencies against Unity assemblies.

This is a source check without VESPER_WWISE. It does not import the project, run Unity,
validate the Wwise SDK branch, compile shaders, or build a player.
"""
import argparse
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unity-contents", type=pathlib.Path, required=True)
    args = parser.parse_args()
    contents = args.unity_contents
    scripts = contents / "Resources/Scripting"
    compiler = next(scripts.rglob("csc.dll"))
    templates = contents / "Resources/PackageManager/ProjectTemplates/libcache"
    package = next(templates.glob("com.unity.template.3d-cross-platform-*/ScriptAssemblies"))
    framework = scripts / "UnityReferenceAssemblies/unity-4.8-api"
    references = list(framework.glob("*.dll")) + list((framework / "Facades").glob("*.dll"))
    references += list((scripts / "Managed/UnityEngine").glob("*.dll"))
    for pattern in ["Unity.RenderPipelines.*.dll", "Unity.Mathematics.dll", "Unity.Collections.dll", "Unity.Burst.dll"]:
        references += list(package.glob(pattern))
    sources = list((ROOT / "Unity/Vesper/Assets/Vesper/Expansion/WeatherW11").rglob("*.cs"))
    sources += list((ROOT / "Unity/Vesper/Assets/Vesper/SoundDirector").rglob("*.cs"))
    sources += [ROOT / "Unity/Vesper/Assets/Vesper/Expansion/WeatherW10/Runtime" / name for name in
                ["WorldMotor.cs", "WorldEnvironment.cs", "WorldLayout.cs", "WorldAnimation.cs", "WorldRunInput.cs", "WorldCamera.cs"]]
    sources += [ROOT / "Unity/Vesper/Assets/Vesper/Expansion/LinearWorld/Runtime/WorldLayout.cs",
                ROOT / "Unity/Vesper/Assets/Vesper/Runtime/VesperPlanarReflection.cs"]
    with tempfile.TemporaryDirectory(prefix="vesper-audio-compile-") as temp:
        output = pathlib.Path(temp) / "AudioCheck.dll"
        response = pathlib.Path(temp) / "compile.rsp"
        # Match Unity's serializer/conditional-compilation field warning exclusions.
        options = ["-nologo", "-target:library", "-nostdlib+", "-warnaserror+", "-nowarn:0649,0169", "-langversion:latest",
                   "-define:UNITY_EDITOR,UNITY_EDITOR_OSX,UNITY_STANDALONE_OSX,UNITY_6000_0_OR_NEWER",
                   '-out:"' + str(output) + '"']
        options += ['-r:"' + str(p) + '"' for p in references]
        options += ['"' + str(p) + '"' for p in sources]
        response.write_text("\n".join(options))
        subprocess.run([str(scripts / "NetCoreRuntime/dotnet"), str(compiler), "@" + str(response)], check=True)
    print(f"PASS: {len(sources)} actual C# source files; no-SDK compile, warnings treated as errors")

if __name__ == "__main__":
    main()
