from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .upstream import BuildError, dist_dir, repo_root
from .yamlio import load_yaml

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".ps1",
    ".js",
    ".ts",
    ".xml",
}
UNSUPPORTED_FRONTMATTER_KEYS = {"allowed-tools", "allowed_tools"}


def load_agents(root: Path | None = None) -> dict[str, Any]:
    base = root or repo_root()
    data = load_yaml(base / "configs" / "agents.yaml")
    agents = data.get("agents") if isinstance(data, dict) else None
    if not isinstance(agents, dict) or not agents:
        raise BuildError("configs/agents.yaml must define agents mapping")
    return agents


def discover_skills(source_roots: list[Path]) -> dict[str, Path]:
    skills: dict[str, Path] = {}
    for root in source_roots:
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if child.is_dir() and (child / "SKILL.md").is_file():
                skills[child.name] = child
    return skills


def generate_agent_outputs(root: Path | None = None, worktree: Path | None = None) -> dict[str, list[str]]:
    base = root or repo_root()
    wt = worktree or (base / ".uk1c_work" / "upstream")
    agents = load_agents(base)
    sources = [
        wt / ".claude" / "skills",
        base / ".agents" / "skills",
        wt / ".agents" / "skills",
    ]
    skills = discover_skills(sources)
    if not skills:
        raise BuildError(
            "No skills found. Initialize upstream submodule or add local skills under .agents/skills or overlays/skills."
        )

    out_root = dist_dir(base)
    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    report: dict[str, list[str]] = {}
    for agent_name, cfg in agents.items():
        output_dir = str(cfg["output_dir"])
        skill_file_name = str(cfg.get("skill_file_name", "SKILL.md"))
        supports_allowed_tools = bool(cfg.get("supports_allowed_tools", False))
        target_root = out_root / output_dir
        generated: list[str] = []
        for skill_name, src in sorted(skills.items()):
            dst = target_root / skill_name
            shutil.copytree(src, dst)
            _normalize_skill_file_name(dst, skill_file_name)
            _transform_tree(
                dst,
                output_dir=output_dir,
                supports_allowed_tools=supports_allowed_tools,
            )
            generated.append(skill_name)
        report[agent_name] = generated
    return report


def find_hardcoded_claude_paths(root: Path | None = None) -> list[str]:
    base = root or repo_root()
    out_root = dist_dir(base)
    offenders: list[str] = []
    for path in out_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(base).as_posix()
        if rel.startswith("dist/.claude/skills/"):
            continue
        if not _is_text_file(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if ".claude/skills" in text:
            offenders.append(rel)
    return offenders


def _normalize_skill_file_name(skill_dir: Path, skill_file_name: str) -> None:
    if skill_file_name == "SKILL.md":
        return
    source = skill_dir / "SKILL.md"
    if source.exists():
        source.rename(skill_dir / skill_file_name)


def _transform_tree(skill_dir: Path, output_dir: str, supports_allowed_tools: bool) -> None:
    for file_path in skill_dir.rglob("*"):
        if not file_path.is_file() or not _is_text_file(file_path):
            continue
        text = file_path.read_text(encoding="utf-8", errors="replace")
        original = text
        text = text.replace(".claude/skills", output_dir)
        text = text.replace(".agents/skills", output_dir)
        if file_path.name == "SKILL.md" and not supports_allowed_tools:
            text = _strip_unsupported_frontmatter(text)
        if text != original:
            file_path.write_text(text, encoding="utf-8")


def _strip_unsupported_frontmatter(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return text

    header = lines[1:end]
    filtered: list[str] = []
    skipping = False
    for line in header:
        stripped = line.strip()
        is_top_key = bool(stripped) and not line.startswith((" ", "\t")) and ":" in line
        if is_top_key:
            key = stripped.split(":", 1)[0].strip()
            skipping = key in UNSUPPORTED_FRONTMATTER_KEYS
        if not skipping:
            filtered.append(line)
    return "---\n" + "".join(filtered) + "---\n" + "".join(lines[end + 1 :])


def _is_text_file(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES or path.name == "SKILL.md":
        return True
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\x00" not in chunk
