# Findings

- README references obsolete as_memory-skills path; actual development source ageroot_skills.
- Skills policy requires external home-store symlinks; portable checkout is not self-contained.
- ADRs retain summary-first confirmation and workflow/maintenance separation.
- Update engine already consolidates comparison and atomic apply; preserve it.

- Confirmed template and skills are separate nested Git repositories excluded by root.
- sync-orchestration-package.py --check fails: Orca adapter files reported as unexpected.
- Agent Skills specification recommends relative resource references and progressive disclosure; harness instruction loading differs.
- permissions.md claims enforced pre_tool_call hook; no implementation/config wiring found in template.
- Sources: https://agentskills.io/specification ; https://learn.chatgpt.com/docs/agent-configuration/agents-md ; https://learn.chatgpt.com/docs/build-skills ; https://code.claude.com/docs/en/memory ; https://code.claude.com/docs/en/hooks

- Independent review: update engine accepts prepared renders, not renderer; directory entries in state require payload expansion and end-to-end coverage. Root external-link validation does not prove child skill availability.
- 35 comparison tests pass; report generated and HTML parsed, four candidates present.
