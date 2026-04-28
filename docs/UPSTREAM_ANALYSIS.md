# Upstream analysis snapshot

Generation environment attempted `git clone --depth 1 https://github.com/Nikolay-Shirokov/cc-1c-skills.git`, but DNS resolution for `github.com` was unavailable in the execution container. The repository was then inspected through GitHub/Web pages.

Observed upstream structure:

- skills live in `.claude/skills/`;
- `scripts/switch.py` exists and maps platforms such as `.claude/skills`, `.agents/skills`, `.codex/skills`, `.gemini/skills`, `.cursor/skills`;
- repository includes `docs/`, `scripts/`, `tests/skills/`, `README.md`, `LICENSE`;
- upstream README lists groups for EPF, ERF, MXL, Form, Role, SKD, metadata, CF, CFE, subsystem, DB, Web and utility skills;
- upstream README references `Configuration.xml`, `ConfigDumpInfo.xml`, XML specifications, CF/CFE/EPF/ERF flows and `scripts/switch.py`.

Skill names observed in upstream `.claude/skills/` include:

`cf-edit`, `cf-info`, `cf-init`, `cf-validate`, `cfe-borrow`, `cfe-diff`, `cfe-init`, `cfe-patch-method`, `cfe-validate`, `db-create`, `db-dump-cf`, `db-dump-xml`, `db-list`, `db-load-cf`, `db-load-git`, `db-load-xml`, `db-run`, `db-update`, `epf-add-form`, `epf-bsp-add-command`, `epf-bsp-init`, `epf-build`, `epf-dump`, `epf-init`, `epf-validate`, `erf-build`, `erf-dump`, `erf-init`, `erf-validate`, `form-add`, `form-compile`, `form-edit`, `form-info`, `form-patterns`, `form-remove`, `form-validate`, `help-add`, `img-grid`, `interface-edit`, `interface-validate`, `meta-compile`, `meta-edit`, `meta-info`, `meta-remove`, `meta-validate`, `mxl-compile`, `mxl-decompile`, `mxl-info`, `mxl-validate`, `role-compile`, `role-info`, `role-validate`, `skd-compile`, `skd-edit`, `skd-info`, `skd-validate`, `subsystem-compile`, `subsystem-edit`, `subsystem-info`, `subsystem-validate`, `template-add`, `template-remove`, `web-info`, `web-publish`, `web-stop`, `web-test`, `web-unpublish`.

Recommended follow-up after unpacking this repository with network access:

```bash
git submodule update --init --recursive
python build/apply.py update-upstream
python build/apply.py build
python build/apply.py validate
python -m pytest
```
