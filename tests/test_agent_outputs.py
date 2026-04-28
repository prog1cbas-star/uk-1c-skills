from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_build() -> None:
    subprocess.run([sys.executable, "build/apply.py", "build"], cwd=ROOT, check=True)


def snapshot_dist() -> dict[str, str]:
    result = {}
    for path in sorted((ROOT / "dist").rglob("*")):
        if path.is_file():
            rel = path.relative_to(ROOT).as_posix()
            result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def test_build_generates_agent_outputs():
    run_build()
    for rel in [
        "dist/.agents/skills",
        "dist/.claude/skills",
        "dist/.codex/skills",
        "dist/.gemini/skills",
    ]:
        path = ROOT / rel
        assert path.is_dir(), rel
        assert list(path.glob("*/SKILL.md")), rel


def test_build_is_idempotent():
    run_build()
    first = snapshot_dist()
    run_build()
    second = snapshot_dist()
    assert first == second
