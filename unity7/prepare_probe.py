#!/usr/bin/env python3
"""Prepare an exact Unity 7 source tree for isolated compiler/runtime validation.

Use a licensed local Unity installation. This does not install or register a
runtime and does not copy the Unity 6 runtime from this repository. It does not
generate project-specific method bridges or install a Player SDK.
"""
# Copyright (c) 2026 mmm1h. Licensed under the MIT license in the repository root.
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unity-il2cpp", type=Path, required=True)
    parser.add_argument("--hybridclr", type=Path, required=True,
                        help="Root of the hybridclr source repository")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--with-toolchain", action="store_true",
                        help="Also copy the matching Unity IL2CPP tools for standalone runtime tests")
    args = parser.parse_args()
    inputs = args.unity_il2cpp.resolve()
    source = args.hybridclr.resolve() / "hybridclr"
    output = args.output.resolve()
    patchdir = Path(__file__).resolve().parent / "7000.0.0a12"
    manifest = json.loads((patchdir / "manifest.json").read_text(encoding="utf-8"))
    if not shutil.which("git"):
        parser.error("git is required to validate and apply the source patch")
    if not (source / "Il2CppGenericClassCompat.h").is_file():
        parser.error("hybridclr must use the codex/unity7-support source branch")
    if output.exists():
        parser.error("output must not exist; inspect old output before reusing a path")
    if output.is_relative_to(inputs) or output.is_relative_to(args.hybridclr.resolve()):
        parser.error("output must be outside the Unity installation and HybridCLR source")
    for relative, expected in manifest["input_sha256"].items():
        path = inputs / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            parser.error(f"{relative} does not match Unity {manifest['unity_version']} ({manifest['revision']})")
    tree_hash = hashlib.sha256()
    runtime_source = inputs / "libil2cpp"
    files = sorted((p for p in runtime_source.rglob("*") if p.is_file()),
                   key=lambda p: p.relative_to(runtime_source).as_posix())
    for path in files:
        tree_hash.update(path.relative_to(runtime_source).as_posix().encode("utf-8") + b"\0")
        tree_hash.update(hashlib.sha256(path.read_bytes()).digest())
    if len(files) != manifest["source_file_count"] or tree_hash.hexdigest() != manifest["source_tree_sha256"]:
        parser.error("libil2cpp source tree does not match the pinned Unity revision")
    shutil.copytree(inputs / "libil2cpp", output / "libil2cpp")
    shutil.copytree(inputs / "external/google", output / "external/google")
    if args.with_toolchain:
        shutil.copytree(inputs, output, dirs_exist_ok=True,
                        ignore=lambda directory, names: ["libil2cpp"] if Path(directory) == inputs else [])
    shutil.copytree(source, output / "libil2cpp/hybridclr", ignore=shutil.ignore_patterns("generated"))
    for patch in sorted(patchdir.glob("*.patch")):
        subprocess.run(["git", "apply", "--check", "--unidiff-zero", str(patch)], cwd=output, check=True)
        subprocess.run(["git", "apply", "--unidiff-zero", str(patch)], cwd=output, check=True)
    generated = output / "libil2cpp/hybridclr/generated"
    generated.mkdir()
    (generated / "UnityVersion.inc").write_text("#define HYBRIDCLR_UNITY_VERSION 70000000\n", encoding="utf-8")
    # An empty assembly manifest is a valid configuration for source-only probes.
    # No MethodBridge.inc is fabricated; a Player must generate its own bridge.
    (generated / "AssemblyManifest.inc").write_text("", encoding="utf-8")
    (output / "INCOMPLETE_PORT.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Prepared {output}. This is NOT an installable HybridCLR runtime.")


if __name__ == "__main__":
    main()
