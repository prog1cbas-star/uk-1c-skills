# patches

Patches are for minimal upstream changes that cannot be expressed as overlays.

Rules:

1. Do not edit `upstream/cc-1c-skills` manually.
2. Create patches against a clean upstream checkout.
3. Keep patches small and focused.
4. Run:

```bash
python build/apply.py update-upstream
python build/apply.py apply-patches
python build/apply.py build
python build/apply.py validate
python -m pytest
```

Patch files can be marked as documentation-only with `# uk1c-patch: disabled`. Disabled patches are examples/templates and are skipped by the build system.
