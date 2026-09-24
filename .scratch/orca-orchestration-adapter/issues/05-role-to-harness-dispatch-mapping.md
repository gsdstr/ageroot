# Role-to-harness dispatch mapping

Status: ready-for-agent
Assignee: /root
Blocked by: 03

Spec: [Orca orchestration adapter v1](../spec.md)

## Scope

In portable orchestration, dispatch must map each Task to the harness and model
assigned to its role in `protocols/orchestration.md`, rather than imposing a
single global default across all tasks.

- Builder defaults to `agy` (`gemini-3.8-flash-high`), fallback `codex`.
- Reviewer defaults to `codex` (`codex-auto-review` / `gpt-5.6-terra`), fallback `agy`. Reviewer must maintain model-family independence from Builder.
- Author defaults to `codex`.
- Researcher defaults to `agy`.

Portability requirements:
1. Never embed machine-local absolute paths (e.g. `/Users/gsdstr/...`). Executables (`agy`, `codex`, `claude`) must resolve from PATH or environment variables.
2. In Orca: map role harness to `--agent <harness>` when natively supported, or create terminal via `orca terminal create --command "<harness>"` and bind via `worker-start --terminal <handle>`.
3. Do not mechanically pass template `--agent codex` when a role calls for another harness, and do not universally force `agy` where orthogonality or specs require another provider.

## Acceptance criteria

- Runbook and adapter enforce role-based harness resolution per `protocols/orchestration.md`.
- Builder and Reviewer model-family independence is preserved.
- No personal or machine-specific absolute paths exist in `.agents/` or adapter contracts.
- Executables resolve portably via PATH/environment.
- Adapter tasks declare role and assigned harness.

## Dependencies

- [Add explicit apply and execute gates](03-add-explicit-apply-execute-gates.md)
