# Planning storage location

Evaluate moving isolated `planning-with-files` plan directories from the
skill-default `.planning/<plan-id>/` to a project-owned location under
`.scratch/`.

The work is deferred. Preserve compatibility with the skill resolver, hooks,
attestation, active-plan pointer, and parallel-session isolation before making
the change.
