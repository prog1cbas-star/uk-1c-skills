from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .yamlio import dump_yaml, load_yaml


class BuildError(RuntimeError):
    """Raised for build orchestration errors."""


@dataclass(frozen=True)
class PreparedUpstream:
    source_path: Path
    worktree_path: Path
    used_fallback: bool
    message: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_build_config(root: Path | None = None) -> dict:
    base = root or repo_root()
    data = load_yaml(base / "configs" / "build.yaml")
    if not isinstance(data, dict):
        raise BuildError("configs/build.yaml must be a mapping")
    return data


def work_dir(root: Path | None = None) -> Path:
    base = root or repo_root()
    cfg = load_build_config(base)
    return base / cfg.get("paths", {}).get("work_dir", ".uk1c_work")


def dist_dir(root: Path | None = None) -> Path:
    base = root or repo_root()
    cfg = load_build_config(base)
    return base / cfg.get("paths", {}).get("dist_dir", "dist")


def upstream_path(root: Path | None = None) -> Path:
    base = root or repo_root()
    cfg = load_build_config(base)
    return base / cfg.get("repository", {}).get("upstream_path", "upstream/cc-1c-skills")


def upstream_skills_path(root: Path | None = None) -> Path:
    base = root or repo_root()
    cfg = load_build_config(base)
    return upstream_path(base) / cfg.get("paths", {}).get("upstream_skills_dir", ".claude/skills")


def clean(root: Path | None = None, include_dist: bool = False) -> None:
    base = root or repo_root()
    for path in [work_dir(base), dist_dir(base) if include_dist else None]:
        if path and path.exists():
            shutil.rmtree(path)


def prepare_upstream(root: Path | None = None) -> PreparedUpstream:
    base = root or repo_root()
    wd = work_dir(base)
    upstream_worktree = wd / "upstream"
    if upstream_worktree.exists():
        shutil.rmtree(upstream_worktree)
    upstream_worktree.parent.mkdir(parents=True, exist_ok=True)

    src = upstream_path(base)
    skills = upstream_skills_path(base)
    if skills.is_dir():
        ignore = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache")
        shutil.copytree(src, upstream_worktree, ignore=ignore)
        return PreparedUpstream(
            source_path=src,
            worktree_path=upstream_worktree,
            used_fallback=False,
            message=f"Copied upstream from {src}",
        )

    # Offline/fallback skeleton: enough for deterministic build and tests.
    (upstream_worktree / ".claude" / "skills").mkdir(parents=True, exist_ok=True)
    (upstream_worktree / "README.md").write_text(
        "# fallback upstream skeleton\n\n"
        "The real upstream submodule is not initialized. "
        "Run `python build/apply.py update-upstream` or `git submodule update --init --recursive`.\n",
        encoding="utf-8",
    )
    return PreparedUpstream(
        source_path=src,
        worktree_path=upstream_worktree,
        used_fallback=True,
        message=(
            "Upstream submodule is not initialized; using fallback skeleton and local UA skills"
        ),
    )


def update_upstream(root: Path | None = None) -> tuple[str, str]:
    base = root or repo_root()
    cfg = load_build_config(base)
    repo_cfg = cfg.get("repository", {})
    url = repo_cfg.get("upstream_url", "https://github.com/Nikolay-Shirokov/cc-1c-skills.git")
    branch = repo_cfg.get("upstream_branch", "main")
    target = upstream_path(base)

    before = "missing"
    if target.exists():
        before = _git(target, "rev-parse", "HEAD", allow_failure=True).strip() or "unknown"
        _git(target, "fetch", "origin", branch)
        _git(target, "checkout", branch)
        _git(target, "pull", "--ff-only", "origin", branch)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        _git(base, "clone", "--branch", branch, url, str(target))

    after = _git(target, "rev-parse", "HEAD").strip()
    lock = {
        "upstream": {
            "url": url,
            "branch": branch,
            "path": str(target.relative_to(base)),
            "commit": after,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "previous_commit": before,
        }
    }
    (base / "upstream.lock").write_text(dump_yaml(lock), encoding="utf-8")
    return before, after


def _git(cwd: Path, *args: str, allow_failure: bool = False) -> str:
    cmd = ["git", *args]
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.returncode != 0 and not allow_failure:
        raise BuildError(
            "Git command failed: "
            + " ".join(cmd)
            + f"\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc.stdout
