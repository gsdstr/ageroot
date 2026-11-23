---
name: ageroot-roles
description: Resolve canonical roles to local harnesses and models, inspect configuration inheritance, or set up machine preferences. Use for /ageroot-roles or when orchestration needs role routing.
---

# Role routing

Run `python3 <this-skill>/scripts/roles.py` directly; no package installation,
PYTHONPATH, provider credentials, or network access is required.

## Commands

- `show [--format text|json]`: inspect all six canonical roles, their ordered
  targets, and the winning configuration layer. `--json` aliases JSON format.
- `setup [--local|--team|--global] [--non-interactive]`: probe PATH for `agy`,
  `codex`, `claude`, `orca`, and `hermes`; write preferences atomically. Local
  is the default. Existing roles in the destination are preserved; missing
  roles are populated from detected harnesses. With no detected binaries,
  generated roles are explicitly disabled. Interactive mode confirms the
  destination before writing; non-interactive mode writes immediately.
- `resolve <role> [--exclude-model <id>] [--exclude-family <family>]`: emit
  versioned JSON with `resolved` or `unavailable`, winning layer, selected
  target/index, readiness, and rejection trace. Exclusion flags repeat.
  Unavailable is a valid routing result (exit 0); malformed configuration is
  an error (exit 2, JSON diagnostic on stderr).

Every command accepts `--workspace <path>` (`--root` alias) before or after
its subcommand. Without it, walk upward from cwd to the first `.agents/`.
Global setup works outside a workspace.

## Configuration hierarchy

First definition of each role wins, independently:

1. `.agents/roles.local.yaml` — workspace preference, git ignored.
2. `.agents/roles.yaml` — tracked team baseline.
3. `$XDG_CONFIG_HOME/ageroot/roles.yaml`, or `~/.config/ageroot/roles.yaml`.
4. Defaults embedded in `scripts/roles.py`.

A role replaces its entire target list. Exhausting that list returns
`unavailable`; it never resumes at a lower layer. `targets: []` disables a
role. Every existing layer is validated, including shadowed definitions.

```yaml
version: 1
roles:
  builder:
    targets:
      - harness: codex
        model: gpt-5.6-sol
  reviewer:
    targets: []
```

Canonical names: `coordinator`, `researcher`, `author`, `builder`, `reviewer`,
`integrator`. Use two-space block mappings and target lists. Each target
contains exactly nonempty string `harness` and `model` fields. Version must
be integer 1. Duplicate keys, nulls, extra fields, YAML anchors/tags, and flow
collections other than the empty list are validation errors with line numbers.
Quote numeric-looking model IDs. Partial role maps inherit missing roles.

## Readiness and independence

`missing` means the binary is absent from PATH. `supported` means a known
invocation surface (`agy`, `codex`, `claude`) is present. Other present
surfaces, including `orca` and `hermes`, are `unverified`; resolution may
select them, but the Coordinator must check runtime support before dispatch.
All model availability remains unverified offline. Binary presence does not
prove model access or subscription entitlement.

For Reviewer, pass the active Builder's model and family as exclusions.
Families include `gpt` (including Codex), `gemini`, `claude`, `llama`, `qwen`,
and `deepseek`. Opaque/default IDs have family `unknown`; family exclusion
rejects those because independence cannot be established. Orchestration
must additionally isolate Reviewer worker context.

Automatic candidate traversal is limited to pre-dispatch checks. Once a turn
starts, files change, or usage accrues, reconcile failures explicitly with
the Coordinator before selecting another target. Lifecycle policy lives in
`/ageroot-orchestrate`.
