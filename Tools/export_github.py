"""Copy an upload snapshot using .gitignore, without changing Git or source files."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def git(*args, data=None, allowed=(0,)):
    result = subprocess.run(
        ["git", *args], cwd=ROOT, input=data, capture_output=True, check=False
    )
    if result.returncode not in allowed:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    return result.stdout


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def select_files():
    candidates = sorted(set(filter(None, git(
        "ls-files", "--cached", "--others", "--exclude-standard", "-z"
    ).decode("utf-8").split("\0"))))
    # --no-index is essential: ignored files may already be tracked in the source.
    ignored = set(filter(None, git(
        "check-ignore", "--no-index", "--stdin", "-z",
        data=("\0".join(candidates) + "\0").encode("utf-8"), allowed=(0, 1)
    ).decode("utf-8").split("\0")))
    selected = [p for p in candidates if p not in ignored]
    for rel in selected:
        source = ROOT / rel
        if source.is_symlink() or not source.is_file():
            raise RuntimeError("Expected a regular source file: " + rel)
        if not source.resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError("Source escapes workspace: " + rel)
    return selected, sorted(ignored)


def preflight(selected):
    paths = set(selected)
    required = [
        ".gitignore", ".gitattributes", "README.md", "HANDOFF.md",
        "Unity/Vesper/Packages/manifest.json",
        "Unity/Vesper/Packages/packages-lock.json",
        "Unity/Vesper/ProjectSettings/ProjectVersion.txt",
        "Unity/Vesper/Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W10.unity",
    ]
    missing = [p for p in required if p not in paths]
    # Preserve the complete Unity project, including previous scenes and GUIDs.
    unity_files = []
    for folder in ("Assets", "Packages", "ProjectSettings"):
        for source in (ROOT / "Unity/Vesper" / folder).rglob("*"):
            if source.is_file():
                rel = source.relative_to(ROOT).as_posix()
                unity_files.append(rel)
                if rel not in paths:
                    missing.append(rel)
            if folder == "Assets" and source.suffix != ".meta":
                rel = source.relative_to(ROOT).as_posix() + ".meta"
                if rel not in paths:
                    missing.append(rel)
    if missing:
        raise RuntimeError("Required files or Unity metadata missing: " + repr(missing[:20]))
    large = [p for p in selected if (ROOT / p).stat().st_size > 100 * 1024 * 1024]
    if large:
        attributes = git(
            "check-attr", "-z", "--stdin", "filter",
            data=("\0".join(large) + "\0").encode("utf-8")
        ).decode("utf-8").split("\0")
        for index in range(0, len(attributes) - 1, 3):
            if attributes[index + 2] != "lfs":
                raise RuntimeError("File over 100 MiB requires LFS: " + attributes[index])
    # Fail without printing any suspected credential value.
    credential = re.compile(
        rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|"
        rb"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}|"
        rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"
    )
    text_extensions = {".py", ".ps1", ".cmd", ".js", ".json", ".md", ".txt", ".yaml", ".yml", ".cs", ".html"}
    for rel in selected:
        source = ROOT / rel
        if source.suffix.lower() in text_extensions and credential.search(source.read_bytes()):
            raise RuntimeError("Possible credential; inspect locally before export: " + rel)
    return {"unityFiles": len(unity_files), "largeFilesUsingLfs": large}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New, empty destination; never overwritten")
    args = parser.parse_args()
    selected, ignored = select_files()
    checks = preflight(selected)
    summary = {
        "selectedFiles": len(selected),
        "selectedBytes": sum((ROOT / p).stat().st_size for p in selected),
        "ignoredTrackedFiles": len(ignored),
        "sourceHead": git("rev-parse", "HEAD").decode().strip(),
        **checks,
    }
    print(json.dumps(summary, indent=2), flush=True)
    if not args.output:
        return
    destination = args.output.resolve()
    if destination == ROOT or ROOT.is_relative_to(destination):
        raise RuntimeError("Destination must not be the source or its parent")
    # All preflight checks finish before creating any output.
    destination.mkdir(parents=True, exist_ok=False)
    manifest = []
    for index, rel in enumerate(selected, 1):
        source, target = ROOT / rel, destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        before = digest(source)
        shutil.copy2(source, target)
        if before != digest(target) or before != digest(source):
            raise RuntimeError("Source changed or copy mismatch: " + rel)
        manifest.append({"path": rel, "bytes": target.stat().st_size, "sha256": before})
        if index % 2000 == 0:
            print(f"Copied and verified {index}/{len(selected)}", flush=True)
    (destination / "HANDOFF_CONTENTS.json").write_text(json.dumps({
        **summary,
        "files": manifest,
        "ignoredTrackedPaths": ignored,
        "note": "File hashes exclude this generated manifest. No Git history or credentials are copied.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Export ready: {destination}", flush=True)


if __name__ == "__main__":
    main()
