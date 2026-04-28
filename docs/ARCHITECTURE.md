# Architecture

`uk-1c-skills` is a downstream repository built as layers over `Nikolay-Shirokov/cc-1c-skills`.

## Layers

```text
upstream/cc-1c-skills/      clean upstream submodule
patches/                    small git patches, applied to temporary copy only
overlays/                   downstream files merged over temporary copy
configs/                    machine-readable registries and build config
build/                      Python orchestration, validation and rendering
dist/                       generated agent-specific outputs
```

## Build flow

`python build/apply.py build` performs:

1. remove `.uk1c_work` and `dist`;
2. copy clean upstream to `.uk1c_work/upstream` or create fallback skeleton if submodule is missing;
3. copy to `.uk1c_work/merged`;
4. run `git apply --check` and apply enabled patches;
5. apply overlays from `overlays/manifest.yaml`;
6. collect skills from upstream `.claude/skills`, root `.agents/skills` and overlay `.agents/skills`;
7. generate `dist/.agents/skills`, `dist/.claude/skills`, `dist/.codex/skills`, `dist/.gemini/skills`, `dist/.cursor/skills`;
8. generate docs from YAML registries;
9. validate configs, resolver rules, skill layout and hardcoded paths.

## Upstream policy

Never commit manual UA changes into `upstream/cc-1c-skills`. The upstream tree is replaceable: any local difference must be represented as a patch, overlay, config or build-system change.

## Canonical skills layout

This downstream uses `.agents/skills` as the canonical source-of-truth for UA-native skills because it is agent-neutral. Upstream skills are imported from `.claude/skills` during build and converted into agent-specific outputs.

## Submodule vs subtree

Submodule is the default because it keeps upstream history and downstream overlay history separate. Subtree is only preferable if you need an entirely self-contained monorepo and accept more complex upstream sync conflicts.
