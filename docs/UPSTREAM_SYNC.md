# Upstream sync

## Initial setup

```bash
git submodule add https://github.com/Nikolay-Shirokov/cc-1c-skills.git upstream/cc-1c-skills
git submodule update --init --recursive
python build/apply.py build
python build/apply.py validate
python -m pytest
```

## Update upstream

```bash
python build/apply.py update-upstream
python build/apply.py apply-patches
python build/apply.py build
python build/apply.py validate
python -m pytest
```

`update-upstream` prints old/new commits and writes `upstream.lock`.

## Patch conflicts

If `apply-patches` fails:

1. inspect the failing patch in `patches/`;
2. compare it with the current upstream file;
3. edit the patch or mark it disabled if the change is obsolete;
4. rerun `python build/apply.py apply-patches`;
5. run build, validate and tests.

## What to keep out of upstream

- UA platform registry;
- Ukrainian documentation;
- generated dist outputs;
- compatibility wrappers;
- CI and downstream build logic.
