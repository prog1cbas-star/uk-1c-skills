# upstream placeholder

This directory is reserved for the upstream git submodule:

```bash
git submodule add https://github.com/Nikolay-Shirokov/cc-1c-skills.git upstream/cc-1c-skills
git submodule update --init --recursive
```

The generated ZIP intentionally does not vendor a full upstream checkout. The build system can operate in fallback mode with local UA skills, and it will use `upstream/cc-1c-skills/.claude/skills` automatically once the submodule is initialized.
