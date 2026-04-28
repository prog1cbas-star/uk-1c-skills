from __future__ import annotations

from pathlib import Path
from typing import Any

from . import agents
from .platforms import PlatformResolver, validate_generated_type_name
from .upstream import dist_dir, repo_root
from .yamlio import load_yaml


class ValidationError(RuntimeError):
    """Raised when repository validation fails."""


REQUIRED_PLATFORM_CASES = {
    "8.3.15": ("2.9", "Version8_3_15"),
    "8.3.20": ("2.13", "Version8_3_20"),
    "8.3.27": ("2.20", "Version8_3_27"),
    "8.5.x": ("2.21", "Version8_5_X"),
    "8.5.1": ("2.21", "Version8_5_X"),
}


def validate_all(root: Path | None = None, require_dist: bool = True) -> list[str]:
    base = root or repo_root()
    errors: list[str] = []
    messages: list[str] = []

    for validator in [
        validate_platform_registry,
        validate_agents_config,
        validate_source_skills,
        validate_generated_type_rules,
    ]:
        try:
            messages.extend(validator(base))
        except ValidationError as exc:
            errors.append(str(exc))

    if require_dist:
        try:
            messages.extend(validate_agent_outputs(base))
        except ValidationError as exc:
            errors.append(str(exc))

    if errors:
        raise ValidationError("\n".join(errors))
    return messages


def validate_platform_registry(root: Path) -> list[str]:
    resolver = PlatformResolver.from_file(root / "configs" / "platform_versions_ua.yaml")
    errors: list[str] = []
    for version, (xml_format, compatibility_mode) in REQUIRED_PLATFORM_CASES.items():
        resolved = resolver.resolve(version)
        if resolved.xml_format != xml_format or resolved.compatibility_mode != compatibility_mode:
            errors.append(
                f"{version}: expected {xml_format}/{compatibility_mode}, "
                f"got {resolved.xml_format}/{resolved.compatibility_mode}"
            )
    if not resolver.resolve("8.3.15").configuration_xml_features == ():
        errors.append("8.3.15 must not include 8.3.16+ Configuration.xml features")
    if "StandaloneConfigurationRestrictionRoles" not in resolver.resolve("8.3.16").configuration_xml_features:
        errors.append("8.3.16 must include StandaloneConfigurationRestrictionRoles")
    if "InternalInfoContainedObject7" not in resolver.resolve("8.3.17").configuration_xml_features:
        errors.append("8.3.17 must include InternalInfoContainedObject7")
    features_318 = set(resolver.resolve("8.3.18").configuration_xml_features)
    if not {"URLExternalDataStorage", "MobileApplicationURLs"}.issubset(features_318):
        errors.append("8.3.18 must include URLExternalDataStorage and MobileApplicationURLs")
    features_320 = set(resolver.resolve("8.3.20").configuration_xml_features)
    if not {
        "DefaultReportAppearanceTemplate",
        "AllowedIncomingShareRequestTypes",
        "DatabaseTablespacesUseMode",
    }.issubset(features_320):
        errors.append("8.3.20 must include 8.3.20 Configuration.xml features")
    if errors:
        raise ValidationError("Platform registry errors:\n- " + "\n- ".join(errors))
    return ["platform registry ok"]


def validate_agents_config(root: Path) -> list[str]:
    data = load_yaml(root / "configs" / "agents.yaml")
    cfg = data.get("agents") if isinstance(data, dict) else None
    if not isinstance(cfg, dict) or not cfg:
        raise ValidationError("configs/agents.yaml does not define agents")
    errors: list[str] = []
    for name, item in cfg.items():
        if not isinstance(item, dict):
            errors.append(f"agent {name} must be a mapping")
            continue
        for key in ["output_dir", "skill_file_name", "supports_allowed_tools"]:
            if key not in item:
                errors.append(f"agent {name} missing {key}")
    if errors:
        raise ValidationError("Agent config errors:\n- " + "\n- ".join(errors))
    return ["agents config ok"]


def validate_source_skills(root: Path) -> list[str]:
    roots = [root / ".agents" / "skills", root / "overlays" / "skills"]
    skill_count = 0
    missing: list[str] = []
    for source in roots:
        if not source.is_dir():
            continue
        for child in source.iterdir():
            if child.is_dir():
                if (child / "SKILL.md").is_file():
                    skill_count += 1
                else:
                    missing.append(str(child.relative_to(root)))
    if skill_count == 0:
        raise ValidationError("No local UA skills found under .agents/skills or overlays/skills")
    if missing:
        raise ValidationError("Skill directories without SKILL.md:\n- " + "\n- ".join(missing))
    return [f"source skills ok ({skill_count})"]


def validate_generated_type_rules(root: Path) -> list[str]:
    registry = root / "configs" / "platform_versions_ua.yaml"
    strict = validate_generated_type_name("8.3.19", "CatalogObject.Wrong", "CatalogObject.Right", registry)
    tolerant = validate_generated_type_name("8.3.20", "CatalogObject.Wrong", "CatalogObject.Right", registry)
    if not strict["errors"] or strict["warnings"]:
        raise ValidationError("8.3.19 GeneratedType mismatch must be an error only")
    if tolerant["errors"] or not tolerant["warnings"]:
        raise ValidationError("8.3.20 GeneratedType mismatch must be a warning only")
    return ["GeneratedType validation rules ok"]


def validate_agent_outputs(root: Path) -> list[str]:
    cfg = agents.load_agents(root)
    out = dist_dir(root)
    errors: list[str] = []
    for name, item in cfg.items():
        skill_root = out / item["output_dir"]
        if not skill_root.is_dir():
            errors.append(f"missing output dir for {name}: {skill_root.relative_to(root)}")
            continue
        skill_dirs = [p for p in skill_root.iterdir() if p.is_dir()]
        if not skill_dirs:
            errors.append(f"no skills generated for {name}: {skill_root.relative_to(root)}")
            continue
        for skill_dir in skill_dirs:
            if not (skill_dir / item.get("skill_file_name", "SKILL.md")).is_file():
                errors.append(f"missing SKILL.md in {skill_dir.relative_to(root)}")
    hardcoded = agents.find_hardcoded_claude_paths(root)
    if hardcoded:
        errors.append("unexpected hardcoded .claude/skills paths:\n- " + "\n- ".join(hardcoded))
    if errors:
        raise ValidationError("Agent output errors:\n- " + "\n- ".join(errors))
    return ["agent outputs ok"]
