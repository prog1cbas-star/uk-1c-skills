from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .yamlio import load_yaml


class PlatformVersionError(ValueError):
    """Raised when a platform version is not present in the UA registry."""


@dataclass(frozen=True)
class ResolvedPlatform:
    key: str
    xml_format: str
    compatibility_mode: str
    configuration_xml_features: tuple[str, ...]
    generated_type_name_validation: dict[str, Any]

    @property
    def generated_type_validation_mode(self) -> str:
        return str(self.generated_type_name_validation.get("mode", "unknown"))


class PlatformResolver:
    def __init__(self, registry: dict[str, Any]):
        self.registry = registry
        self.platforms: dict[str, dict[str, Any]] = {
            key: value
            for key, value in registry.items()
            if isinstance(value, dict) and _looks_like_platform_key(key)
        }
        if not self.platforms:
            raise PlatformVersionError("Platform registry is empty or malformed")

    @classmethod
    def from_file(cls, path: str | Path | None = None) -> "PlatformResolver":
        return cls(load_registry(path))

    def resolve(self, version: str) -> ResolvedPlatform:
        raw = str(version).strip()
        candidates = [raw]
        parts = raw.split(".")
        if len(parts) >= 3:
            candidates.append(".".join(parts[:3]))

        for key in self.platforms:
            if key.endswith(".x"):
                prefix = key[:-2]
                if raw == key or raw == prefix or raw.startswith(prefix + "."):
                    candidates.append(key)

        seen: set[str] = set()
        for candidate in candidates:
            if candidate in seen:
                continue
            seen.add(candidate)
            record = self.platforms.get(candidate)
            if record is not None:
                return self._make_resolved(candidate, record)

        known = ", ".join(sorted(self.platforms))
        raise PlatformVersionError(
            f"Unknown 1C platform version '{version}'. Known normalized versions: {known}"
        )

    @staticmethod
    def _make_resolved(key: str, record: dict[str, Any]) -> ResolvedPlatform:
        return ResolvedPlatform(
            key=key,
            xml_format=str(record["xml_format"]),
            compatibility_mode=str(record["compatibility_mode"]),
            configuration_xml_features=tuple(record.get("configuration_xml_features", [])),
            generated_type_name_validation=dict(record["generated_type_name_validation"]),
        )

    def feature_registry(self) -> dict[str, dict[str, Any]]:
        value = self.registry.get("_configuration_xml_feature_registry", {})
        return value if isinstance(value, dict) else {}


def default_registry_path() -> Path:
    return Path(__file__).resolve().parents[2] / "configs" / "platform_versions_ua.yaml"


def load_registry(path: str | Path | None = None) -> dict[str, Any]:
    registry_path = Path(path) if path is not None else default_registry_path()
    data = load_yaml(registry_path)
    if not isinstance(data, dict):
        raise PlatformVersionError(f"Platform registry must be a mapping: {registry_path}")
    return data


def validate_generated_type_name(
    version: str,
    generated_type_name: str,
    metadata_name: str,
    registry_path: str | Path | None = None,
) -> dict[str, list[str]]:
    resolved = PlatformResolver.from_file(registry_path).resolve(version)
    result = {"errors": [], "warnings": []}
    if generated_type_name == metadata_name:
        return result

    profile = resolved.generated_type_name_validation
    message = (
        f"GeneratedType name '{generated_type_name}' does not match <Name> "
        f"'{metadata_name}' for platform {resolved.key}: {profile.get('rule', '')}"
    ).strip()
    if profile.get("mismatch_is_error"):
        result["errors"].append(message)
    if profile.get("mismatch_is_warning"):
        result["warnings"].append(message)
    return result


def platform_info_text(version: str, registry_path: str | Path | None = None) -> str:
    resolved = PlatformResolver.from_file(registry_path).resolve(version)
    lines = [
        f"Platform: {resolved.key}",
        f"XML format: {resolved.xml_format}",
        f"CompatibilityMode: {resolved.compatibility_mode}",
        f"GeneratedType validation: {resolved.generated_type_validation_mode}",
        "Configuration.xml features:",
    ]
    if resolved.configuration_xml_features:
        lines.extend(f"  - {name}" for name in resolved.configuration_xml_features)
    else:
        lines.append("  - none")
    return "\n".join(lines)


def _looks_like_platform_key(key: str) -> bool:
    parts = key.split(".")
    if len(parts) != 3:
        return False
    if not (parts[0].isdigit() and parts[1].isdigit()):
        return False
    return parts[2].isdigit() or parts[2] == "x"
