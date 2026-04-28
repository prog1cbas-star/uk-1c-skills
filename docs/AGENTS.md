# Agent adapters

Agent outputs are configured in `configs/agents.yaml`.

## ChatGPT / Agent Skills

Output: `dist/.agents/skills/`

This is the universal downstream layout. Claude-specific frontmatter such as `allowed-tools` is removed when the target adapter does not support it.

## Claude Code

Output: `dist/.claude/skills/`

Claude Code compatibility is preserved. Claude-only metadata is kept.

## OpenAI Codex

Output: `dist/.codex/skills/`

Paths inside text files are rewritten from `.claude/skills` or `.agents/skills` to `.codex/skills`.

## Gemini CLI

Output: `dist/.gemini/skills/`

Same conversion rules as Codex.

## Cursor

Output: `dist/.cursor/skills/`

Included because upstream `scripts/switch.py` supports Cursor and Cursor is commonly used in 1C projects.

## Hardcoded path detection

Validation scans non-Claude outputs for unexpected `.claude/skills` references. If upstream adds a new hardcoded path, fix it with an overlay or an enabled patch.
