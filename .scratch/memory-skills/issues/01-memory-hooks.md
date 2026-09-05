# Add host adapters for the portable memory protocol

Type: task
Status: needs-triage

Spec: [Ageroot memory skills](../spec.md)

## Problem

The first version relies on an agent following the portable AGENTS.md memory
protocol. Host hooks may improve coverage of relevant tool outcomes and
failures, but event schemas, installation and lifecycle behavior differ across
agent environments.

## Scope

Evaluate and implement explicitly selected host adapters after the portable
memory-manager workflow exists. Reuse upstream adapters where compatible;
route events into the one runtime owned by memory-manager.

Do not activate maintenance at session end as a side effect of logging hooks.
Automatic maintenance is a separate design in
[issue 02](02-maintenance-invocation-options.md).

## Acceptance criteria

- Inventory relevant upstream hooks and verify actual supported hosts/events;
  publish a compatibility matrix rather than assuming every host is covered.
- Identify which portable protocol steps each hook automates and which still
  require the agent, including explicit knowledge acceptance.
- Specify configuration, installation, disabling and behavior when unsupported.
  Preserve the portable protocol as the fallback.
- Map success/failure events to append-only journal writes using the shared
  runtime and the correct project data root.
- Address duplicate events from retries or overlap with agent-driven recording.
- Verify representative event payloads, malformed input, missing runtime and
  repeated delivery using disposable memory roots.
- Preserve existing host configuration and other hooks; adapters must not run
  maintenance, automatically accept knowledge, or rewrite source journals.

## Dependencies

The core two-skill runtime and its portable workflow contract must exist before
adapter implementation. Supported hosts and enablement policy need triage.

## Comments

- Requested during the memory design interview. Hooks are deferred from the
  initial version; this issue does not authorize enabling them now.
