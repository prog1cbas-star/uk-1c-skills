from __future__ import annotations

import shutil
from pathlib import Path
from string import Template
from typing import Any

from .upstream import BuildError, repo_root
from .yamlio import load_yaml


def load_manifest(root: Path | None = None) -> dict[str, Any]:
    base = root or repo_root()
    manifest = load_yaml(base / "overlays" / "manifest.yaml")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("overlays"), list):
        raise BuildError("overlays/manifest.yaml must contain an overlays list")
    return manifest


def apply_overlays(root: Path | None = None, worktree: Path | None = None) -> list[str]:
    base = root or repo_root()
    target_root = worktree or (base / ".uk1c_work" / "upstream")
    manifest = load_manifest(base)
    messages: list[str] = []
    context = {"repo_name": "uk-1c-skills"}
    for item in manifest["overlays"]:
        if not isinstance(item, dict):
            raise BuildError(f"Invalid overlay item: {item!r}")
        source = base / str(item["source"])
        target = target_root / str(item["target"])
        mode = str(item.get("mode", "copy"))
        if not source.exists():
            raise BuildError(f"Overlay source does not exist: {source}")
        if mode == "copy":
            _copy(source, target, overwrite=True)
        elif mode == "replace":
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            _copy(source, target, overwrite=True)
        elif mode == "merge":
            if not source.is_dir():
                raise BuildError(f"merge overlay source must be directory: {source}")
            _merge_dir(source, target)
        elif mode == "template":
            _template(source, target, context)
        else:
            raise BuildError(f"Unsupported overlay mode '{mode}' for {source}")
        messages.append(f"{mode.upper()} {source.relative_to(base)} -> {target.relative_to(target_root)}")
    return messages


def _copy(source: Path, target: Path, overwrite: bool) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        if target.exists() and overwrite:
            _merge_dir(source, target)
        else:
            shutil.copytree(source, target)
    else:
        shutil.copy2(source, target)


def _merge_dir(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        dest = target / child.name
        if child.is_dir():
            _merge_dir(child, dest)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(child, dest)


def _template(source: Path, target: Path, context: dict[str, str]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8")
    target.write_text(Template(text).safe_substitute(context), encoding="utf-8")
