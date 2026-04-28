# Migration from cc-1c-skills

## Existing project using upstream directly

Before:

```text
project/.claude/skills/    copied from cc-1c-skills
```

After:

```bash
cd uk-1c-skills
python build/apply.py build
cp -R dist/.claude/skills /path/to/project/.claude/
# or for universal layout
cp -R dist/.agents/skills /path/to/project/.agents/
```

## Do not edit copied upstream skills

If you need a Ukrainian change:

1. add or modify a UA skill in `.agents/skills`;
2. add an override under `overlays/skills`;
3. add a patch only if an upstream file must be changed;
4. add/update tests;
5. regenerate docs and dist.

## Runtime notes

Upstream contains PowerShell and Python scripts for different skills. This downstream does not replace that runtime policy; it converts skill layout paths and keeps upstream runtime instructions intact unless an overlay/patch intentionally changes them.
