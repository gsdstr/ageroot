# Extraction of orchestration and role routing into dedicated skills

**Status:** accepted

Ageroot extracts neutral task lifecycle orchestration and local model-role binding into two dedicated first-party skills: `skills/ageroot-orchestrate/` and `skills/ageroot-roles/`.

## Context

Previously, orchestration phase templates and validation lived in a monolithic `.agents/orchestration/` directory, while concrete agent and model assignments were hardcoded directly in `.agents/protocols/orchestration.md` and `templates/orchestration/orca/RUNBOOK.md`.

This design suffered from key limitations:
1. **Model and harness volatility**: Different machines and operating environments have access to distinct agent harnesses (`agy`, `codex`, `claude`, `orca`, `hermes`) and rapid model updates. Hardcoding vendor and model names in version-controlled protocols caused friction across environments.
2. **Monolithic root footprint**: Keeping phase templates, schemas, and runbooks directly under `.agents/` loaded unneeded structural overhead during routine tasks instead of treating orchestration as an on-demand skill (following ADR-0005).
3. **Rigid fallback and lack of local override**: Developers could not easily configure local model preferences or fallback priority lists without modifying git-tracked files.

A rigorous architectural review (Codex, `task_03c784cb636b`) identified eight essential design contracts required to ensure clean configuration inheritance, runtime resilience, review independence, and state-aware migration.

## Decision

### 1. Two dedicated first-party skills

- `skills/ageroot-orchestrate/`:
  - Houses task lifecycle phases (`01-intake.md` through `04-review-integration.md`), `lifecycle-map.md`, JSON schemas, runbooks, and offline validation scripts.
  - Owns lifecycle authority, human Owner gates, budget enforcement, and Reviewer-Builder orthogonal independence policies.
  - Houses the relocated Orca orchestration adapter and runbook (`orca/`), updated to resolve models dynamically via `ageroot-roles`.
- `skills/ageroot-roles/`:
  - Manages canonical role-to-model resolution, CLI harness auto-detection, and configuration hierarchy management via `scripts/roles.py`.
  - Provides deterministic, offline role resolution and interactive setup wizards.

### 2. Four-layer role configuration hierarchy and inheritance (F1)

Role resolution evaluates layers in strict order:
1. `.agents/roles.local.yaml` (workspace local override; ignored by git).
2. `.agents/roles.yaml` (workspace baseline defaults; tracked in git).
3. `$XDG_CONFIG_HOME/ageroot/roles.yaml` or `~/.config/ageroot/roles.yaml` (user machine-wide defaults).
4. Built-in skill fallback defaults.

**Inheritance and exhaustion rules:**
- **Granular role inheritance**: Each canonical role (`coordinator`, `researcher`, `author`, `builder`, `reviewer`, `integrator`) is resolved independently across layers.
- **Atomic list replacement**: When a higher-priority layer defines a role, its `targets` list replaces the entire role definition. Lists are never concatenated or merged by index across layers.
- **Strict exhaustion**: If an explicit layer defines a role and none of its candidate `targets` are available, resolution returns `unavailable` (with an explanatory rejection trace). Resolution does not silently fall back to lower-priority layers for that role, preventing unintended model execution outside explicit local constraints.
- **Explicit disablement**: A role with `targets: []` is explicitly disabled. Nulls, missing required fields (`harness`, `model`), or syntax errors are treated as fail-fast validation errors.

### 3. Candidate schema and runtime resilience (F2, F3)

Roles map to an ordered priority list of execution candidates:
```yaml
version: 1
roles:
  coordinator:
    targets:
      - harness: agy
        model: gemini-3.8-flash-high
      - harness: codex
        model: gpt-5.6-sol
  builder:
    targets:
      - harness: agy
        model: gemini-3.8-flash-high
  reviewer:
    targets:
      - harness: codex
        model: gpt-5.6-terra
      - harness: agy
        model: gemini-3.1-pro-high
```

**Resolution vs. Failover semantics:**
- **Deterministic static resolution**: `roles.py resolve <role>` is side-effect-free, deterministic, and requires no network calls. It checks binary presence in `$PATH` and returns candidate readiness status (`supported`, `unverified`, `missing`).
- **Bounded pre-dispatch traversal**: Automatic traversal to the next target in `targets` is permitted only *before* task execution starts (e.g. binary not found in `$PATH` or local pre-flight probe failure).
- **Post-dispatch failure handling**: Once an agent has started a turn, created files, or incurred token usage, timeouts or errors must not trigger automatic silent failover to another model. Post-dispatch recovery requires explicit coordinator reconciliation.
- **Reviewer independence enforcement**: `ageroot-orchestrate` validates that the selected Reviewer target is orthogonal to the active Builder (distinct model family / isolated worker context). `roles.py resolve reviewer` accepts `--exclude-model` and `--exclude-family` flags to skip ineligible candidates during traversal.

### 4. Standalone CLI contract and parser (F6, F8)

`skills/ageroot-roles/scripts/roles.py` is fully self-contained:
- **Zero runtime dependencies**: Does not import `ageroot_core` or rely on `PYTHONPATH`.
- **Strict stdlib block-YAML parser**: Validates version, rejects duplicate role keys, rejects unsupported flow structures, and reports syntax errors with line numbers.
- **Commands**:
  - `show [--workspace <path>] [--format text|json]`: Displays the active role-model matrix and the winning configuration layer for each role.
  - `setup [--workspace <path>] [--local|--team|--global] [--non-interactive]`: Auto-detects CLI harnesses in `$PATH` (`agy`, `codex`, `claude`, `orca`, `hermes`) and generates/updates configuration with atomic file writes.
  - `resolve <role> [--workspace <path>] [--exclude-model <id>] [--exclude-family <fam>]`: Outputs versioned JSON:
    ```json
    {
      "version": 1,
      "role": "coordinator",
      "status": "resolved",
      "layer": "local",
      "target": {
        "harness": "agy",
        "model": "gemini-3.8-flash-high"
      },
      "candidate_index": 0
    }
    ```

### 5. Orca adapter and runbook relocation (F4)

- Move Orca orchestration adapter and runbook from `.agents/orchestration/orca/` to `skills/ageroot-orchestrate/orca/`.
- Remove hardcoded model tables from `RUNBOOK.md` and `templates/core/.agents/AGENTS.md`.
- Adapter invokes `roles.py resolve` for dynamic agent and model parameters.

### 6. Migration and distribution compatibility (F5, F7)

- **Distribution packaging**:
  - `packages/ageroot_core/distribution/manifest.py` removes monolithic `.agents/orchestration` and `.agents/orchestration/orca` distribution components.
  - Registers `skills/ageroot-orchestrate` and `skills/ageroot-roles` as first-party managed components.
  - Both skills are declared in `apm.yml` and `templates/core/apm.yml`.
- **Protocol cleanup**:
  - Monolithic `.agents/protocols/orchestration.md` is removed.
  - `.agents/protocols/delegation.md` retains abstract capability contracts and delegates orchestration lifecycle to `/ageroot-orchestrate` and role routing to `/ageroot-roles`.
- **Repository and tooling updates**:
  - Add `.agents/roles.local.yaml` to root `.gitignore` and `templates/core/.gitignore`.
  - Update `scripts/sync-orchestration-package.py` and `scripts/test.sh` to validate the new skill source paths.
  - Update `packages/ageroot_core/tests/test_distribution.py` and `distribution/service.py` to recognize new skill paths and retired component names.
  - Update `ageroot.state.yaml` during standard state migration.
