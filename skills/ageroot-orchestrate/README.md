# Orchestration skill package

`manifest.yaml` and phase frontmatter use JSON-compatible YAML so validation
requires only Python's standard library. See `SKILL.md` for lifecycle steps.

```sh
python3 skills/ageroot-orchestrate/scripts/validate.py --schema-smoke-test --package
python3 -m unittest discover -s skills/ageroot-orchestrate/tests
python3 scripts/sync-orchestration-package.py --check
```

The skill directory is canonical; no `.agents/orchestration/` mirror is needed.
For an explicit portable copy, use `sync-orchestration-package.py --write
--target <directory>`; unexpected target files are preserved and reported.
In consumer repositories, validate
`.agents/skills/ageroot-orchestrate/scripts/validate.py --package`.
