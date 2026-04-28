from __future__ import annotations

from pathlib import Path
from typing import Any

from .platforms import PlatformResolver
from .upstream import repo_root


def generate_platform_docs(root: Path | None = None) -> Path:
    base = root or repo_root()
    resolver = PlatformResolver.from_file(base / "configs" / "platform_versions_ua.yaml")
    feature_registry = resolver.feature_registry()
    docs_dir = base / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    target = docs_dir / "PLATFORM_VERSIONS_UA.md"

    lines = [
        "# UA registry версий платформ 1С",
        "",
        "Файл сгенерирован из `configs/platform_versions_ua.yaml` командой `python build/apply.py docs`.",
        "",
        "## Версии",
        "",
        "| Платформа | XML format | CompatibilityMode | GeneratedType | Configuration.xml features |",
        "|---|---:|---|---|---|",
    ]
    for key in sorted(resolver.platforms, key=_version_sort_key):
        item = resolver.resolve(key)
        features = ", ".join(item.configuration_xml_features) or "—"
        lines.append(
            f"| `{item.key}` | `{item.xml_format}` | `{item.compatibility_mode}` | "
            f"`{item.generated_type_validation_mode}` | {features} |"
        )

    lines.extend([
        "",
        "## Configuration.xml features",
        "",
    ])
    for name, info in feature_registry.items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"- Introduced in: `{info.get('introduced_in', 'unknown')}`")
        lines.append(f"- XML: `{info.get('xml_element', 'n/a')}`")
        if info.get("class_id"):
            lines.append(f"- ClassId: `{info['class_id']}`")
        if info.get("description"):
            lines.append(f"- Description: {info['description']}")
        lines.append("")

    lines.extend([
        "## GeneratedType validation",
        "",
        "- `8.3.15`–`8.3.19`: strict, mismatch is error.",
        "- `8.3.20+` и `8.5.x`: tolerant, mismatch is warning.",
        "",
        "Правила берутся из YAML registry; Python resolver не содержит длинных version-specific `if/else`.",
        "",
    ])
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def _version_sort_key(value: str) -> tuple[int, int, int, str]:
    parts = value.split(".")
    patch = 9999 if parts[2] == "x" else int(parts[2])
    return int(parts[0]), int(parts[1]), patch, value
