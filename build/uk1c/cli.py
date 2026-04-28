from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import agents, overlays, patches, render, upstream, validate
from .platforms import PlatformVersionError, platform_info_text
from .upstream import BuildError
from .validate import ValidationError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="uk-1c-skills build system")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="clean workspace, compose upstream+patches+overlays, generate dist and docs")
    sub.add_parser("update-upstream", help="clone/update upstream submodule and write upstream.lock")
    sub.add_parser("apply-patches", help="prepare workspace and apply enabled patches")
    sub.add_parser("apply-overlays", help="prepare workspace and apply overlays")
    sub.add_parser("validate", help="validate configs, skills and generated dist")
    pinfo = sub.add_parser("platform-info", help="print normalized UA platform information")
    pinfo.add_argument("version")
    sub.add_parser("clean", help="remove build workspace and dist")
    sub.add_parser("docs", help="generate docs from configs")
    args = parser.parse_args(argv)

    root = upstream.repo_root()
    try:
        if args.command == "build":
            return cmd_build(root)
        if args.command == "update-upstream":
            before, after = upstream.update_upstream(root)
            print(f"Upstream before: {before}")
            print(f"Upstream after:  {after}")
            return 0
        if args.command == "apply-patches":
            prepared = upstream.prepare_upstream(root)
            print(prepared.message)
            for msg in patches.apply_patches(root, prepared.worktree_path):
                print(msg)
            return 0
        if args.command == "apply-overlays":
            prepared = upstream.prepare_upstream(root)
            merged = _copy_to_merged(root, prepared.worktree_path)
            for msg in overlays.apply_overlays(root, merged):
                print(msg)
            return 0
        if args.command == "validate":
            for msg in validate.validate_all(root, require_dist=True):
                print(f"[OK] {msg}")
            return 0
        if args.command == "platform-info":
            print(platform_info_text(args.version, root / "configs" / "platform_versions_ua.yaml"))
            return 0
        if args.command == "clean":
            upstream.clean(root, include_dist=True)
            print("Cleaned .uk1c_work and dist")
            return 0
        if args.command == "docs":
            target = render.generate_platform_docs(root)
            print(f"Generated {target.relative_to(root)}")
            return 0
        parser.error(f"Unknown command {args.command}")
        return 2
    except (BuildError, ValidationError, PlatformVersionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def cmd_build(root: Path) -> int:
    upstream.clean(root, include_dist=True)
    prepared = upstream.prepare_upstream(root)
    print(prepared.message)
    merged = _copy_to_merged(root, prepared.worktree_path)
    for msg in patches.apply_patches(root, merged):
        print(msg)
    for msg in overlays.apply_overlays(root, merged):
        print(msg)
    report = agents.generate_agent_outputs(root, merged)
    for agent_name, skills in report.items():
        print(f"Generated {len(skills)} skills for {agent_name}")
    target = render.generate_platform_docs(root)
    print(f"Generated {target.relative_to(root)}")
    for msg in validate.validate_all(root, require_dist=True):
        print(f"[OK] {msg}")
    return 0


def _copy_to_merged(root: Path, source: Path) -> Path:
    merged = upstream.work_dir(root) / "merged"
    if merged.exists():
        shutil.rmtree(merged)
    shutil.copytree(source, merged)
    return merged
