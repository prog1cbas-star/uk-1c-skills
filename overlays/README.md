# overlays

Overlays are downstream files copied over a prepared upstream worktree during build.

Use overlays for:

- Ukrainian platform registry and documentation;
- additional skills;
- skill overrides;
- agent-specific wrappers;
- generated documentation inputs.

`overlays/manifest.yaml` supports:

- `copy` — copy file or directory over target;
- `replace` — remove target and copy source;
- `merge` — recursively merge directory contents;
- `template` — render a simple `string.Template` file.
