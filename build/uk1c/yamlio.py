from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:  # pragma: no cover - exercised when PyYAML is installed by users/CI
    import yaml as _pyyaml  # type: ignore
except Exception:  # pragma: no cover - fallback is covered in this environment
    _pyyaml = None


class SimpleYAMLError(ValueError):
    """Raised when the tiny fallback YAML parser cannot parse a config file."""


def load_yaml(path: str | Path) -> Any:
    text = Path(path).read_text(encoding="utf-8")
    if _pyyaml is not None:
        return _pyyaml.safe_load(text) or {}
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        return json.loads(text)
    parser = _TinyYAML(text)
    return parser.parse()


def dump_yaml(data: Any) -> str:
    if _pyyaml is not None:
        return _pyyaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    return _dump(data).rstrip() + "\n"


class _TinyYAML:
    """Small YAML subset parser for this repository's configs.

    It supports nested mappings, block lists, inline [] lists, quoted strings,
    booleans and null. It is not a general YAML implementation; PyYAML remains
    the declared dependency for normal use.
    """

    def __init__(self, text: str):
        self.lines: list[tuple[int, str, int]] = []
        for lineno, raw in enumerate(text.splitlines(), 1):
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            self.lines.append((indent, raw.strip(), lineno))

    def parse(self) -> Any:
        if not self.lines:
            return {}
        value, index = self._parse_block(0, self.lines[0][0])
        if index != len(self.lines):
            _, _, lineno = self.lines[index]
            raise SimpleYAMLError(f"Unexpected YAML content at line {lineno}")
        return value

    def _parse_block(self, index: int, indent: int) -> tuple[Any, int]:
        if index >= len(self.lines):
            return {}, index
        cur_indent, stripped, _ = self.lines[index]
        if cur_indent < indent:
            return {}, index
        if stripped.startswith("- "):
            return self._parse_list(index, cur_indent)
        return self._parse_mapping(index, cur_indent)

    def _parse_mapping(self, index: int, indent: int) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        while index < len(self.lines):
            cur_indent, stripped, lineno = self.lines[index]
            if cur_indent < indent or stripped.startswith("- "):
                break
            if cur_indent > indent:
                raise SimpleYAMLError(f"Unexpected indentation at line {lineno}")
            key, raw_value = self._split_key_value(stripped, lineno)
            index += 1
            if raw_value == "":
                if index < len(self.lines) and self.lines[index][0] > cur_indent:
                    value, index = self._parse_block(index, self.lines[index][0])
                else:
                    value = {}
            else:
                value = self._parse_scalar(raw_value)
            result[key] = value
        return result, index

    def _parse_list(self, index: int, indent: int) -> tuple[list[Any], int]:
        result: list[Any] = []
        while index < len(self.lines):
            cur_indent, stripped, lineno = self.lines[index]
            if cur_indent < indent:
                break
            if cur_indent != indent or not stripped.startswith("- "):
                break
            item = stripped[2:].strip()
            index += 1
            if item == "":
                value, index = self._parse_block(index, indent + 2)
                result.append(value)
            elif ":" in item and not item.startswith(('"', "'")):
                key, raw_value = self._split_key_value(item, lineno)
                mapping: dict[str, Any] = {}
                if raw_value == "":
                    if index < len(self.lines) and self.lines[index][0] > cur_indent:
                        value, index = self._parse_block(index, self.lines[index][0])
                    else:
                        value = {}
                else:
                    value = self._parse_scalar(raw_value)
                mapping[key] = value
                while index < len(self.lines) and self.lines[index][0] > cur_indent:
                    nested_indent, nested_text, nested_lineno = self.lines[index]
                    if nested_text.startswith("- "):
                        break
                    nkey, nraw = self._split_key_value(nested_text, nested_lineno)
                    index += 1
                    if nraw == "":
                        if index < len(self.lines) and self.lines[index][0] > nested_indent:
                            nvalue, index = self._parse_block(index, self.lines[index][0])
                        else:
                            nvalue = {}
                    else:
                        nvalue = self._parse_scalar(nraw)
                    mapping[nkey] = nvalue
                result.append(mapping)
            else:
                result.append(self._parse_scalar(item))
        return result, index

    @staticmethod
    def _split_key_value(text: str, lineno: int) -> tuple[str, str]:
        if ":" not in text:
            raise SimpleYAMLError(f"Expected key: value at line {lineno}")
        key, raw_value = text.split(":", 1)
        key = _unquote(key.strip())
        return key, raw_value.strip()

    @staticmethod
    def _parse_scalar(text: str) -> Any:
        if text == "[]":
            return []
        if text == "{}":
            return {}
        lowered = text.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        if lowered in {"null", "none", "~"}:
            return None
        if text.startswith("[") and text.endswith("]"):
            inner = text[1:-1].strip()
            if not inner:
                return []
            return [_TinyYAML._parse_scalar(part.strip()) for part in inner.split(",")]
        return _unquote(text)


def _unquote(value: str) -> str:
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _dump(data: Any, indent: int = 0) -> str:
    space = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for key, value in data.items():
            rendered_key = _quote_key(str(key))
            if isinstance(value, (dict, list)) and value:
                lines.append(f"{space}{rendered_key}:")
                lines.append(_dump(value, indent + 2))
            else:
                lines.append(f"{space}{rendered_key}: {_format_scalar(value)}")
        return "\n".join(lines)
    if isinstance(data, list):
        if not data:
            return f"{space}[]"
        lines = []
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{space}-")
                lines.append(_dump(item, indent + 2))
            else:
                lines.append(f"{space}- {_format_scalar(item)}")
        return "\n".join(lines)
    return f"{space}{_format_scalar(data)}"


def _quote_key(key: str) -> str:
    if all(ch.isalnum() or ch in "_-" for ch in key):
        return key
    return json.dumps(key, ensure_ascii=False)


def _format_scalar(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if value == []:
        return "[]"
    if value == {}:
        return "{}"
    return json.dumps(str(value), ensure_ascii=False)
