from __future__ import annotations

import subprocess
from pathlib import Path

from .upstream import BuildError, repo_root


def patch_files(root: Path | None = None) -> list[Path]:
    base = root or repo_root()
    return sorted((base / "patches").glob("*.patch"))


def is_disabled_patch(path: Path) -> bool:
    head = "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[:20])
    markers = [
        "uk1c-patch: disabled",
        "Patch-Status: Documentation-only",
        "Patch-Status: Disabled",
    ]
    return any(marker in head for marker in markers)


def apply_patches(root: Path | None = None, worktree: Path | None = None) -> list[str]:
    base = root or repo_root()
    target = worktree or (base / ".uk1c_work" / "upstream")
    messages: list[str] = []
    for patch in patch_files(base):
        rel = patch.relative_to(base)
        if is_disabled_patch(patch):
            messages.append(f"SKIP {rel} (disabled/documentation-only)")
            continue
        _git_apply_check(target, patch)
        _git_apply(target, patch)
        messages.append(f"APPLY {rel}")
    return messages


def _git_apply_check(target: Path, patch: Path) -> None:
    proc = subprocess.run(
        ["git", "apply", "--check", str(patch)],
        cwd=target,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise BuildError(
            f"Patch check failed for {patch.name}.\n"
            f"Worktree: {target}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}\n"
            "Refresh the patch against the current upstream and retry."
        )


def _git_apply(target: Path, patch: Path) -> None:
    proc = subprocess.run(
        ["git", "apply", str(patch)], cwd=target, text=True, capture_output=True
    )
    if proc.returncode != 0:
        raise BuildError(
            f"Patch apply failed for {patch.name}.\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
