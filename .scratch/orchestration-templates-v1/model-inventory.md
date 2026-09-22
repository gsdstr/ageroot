# Replaceable Local Model Inventory (v1)

This inventory records models accessible under the Owner's current **Antigravity** and **ChatGPT** subscriptions. It serves as the local provider binding for neutral orchestration templates. Claude models routed through Antigravity are excluded due to restrictive subscription rate limits.

---

## Schema & Field Definitions

Each model entry specifies seven core fields:

| Field | Description | Importance & Owner Guidance |
| --- | --- | --- |
| `model_id` | Exact CLI or provider model slug | Used directly in CLI flags (`agy --model <id>` or `codex`). |
| `display_name` | Human-readable label | Used in logs, status output, and Owner decision packets. |
| `provider_surface` | Invocation agent wrapper (`agy` or `codex`) | Identifies executable surface and environment isolation mode. |
| `context_window` | Context capacity (standard / max limit) | Determines maximum context payload before compaction/pruning. |
| `tool_mode` | Execution capability (`full` vs `code_mode_only`) | `full` supports subagents/MCP/all tools; `code_mode_only` is sandbox-constrained. |
| `supported_profiles` | Canonical capability profiles matched | Which roles can use this model: `fast`, `coding`, `reasoning`, `review`. |
| `quota_fallback_id` | Primary fallback model when throttled | The intra-subscription model to invoke if rate limit or quota warning trips. |

---

## Core Inventory: Antigravity Subscription (`agy`)

Zero marginal cost under active Google / Antigravity subscription. Supports full tool sandbox, background tasks, MCP, and concurrent subagents.

### Models

| `model_id` | `display_name` | Context | Tool Mode | Supported Profiles | Quota Fallback | Description & Alternatives |
| --- | --- | ---: | --- | --- | --- | --- |
| `gemini-3.8-flash-low` | Gemini 3.8 Flash (Low) | 1M | `full` | `fast` | `gemini-3.7-flash-low` | High-throughput, zero-thinking model for intake, quick lookups, file filtering. *Alternative:* `gemini-3.7-flash-low` if 3.8 encounters availability issues. |
| `gemini-3.8-flash-high` | Gemini 3.8 Flash (High) | 1M | `full` | `coding`, `fast` | `gemini-3.8-flash-medium` | Fast execution with reasoning capability. Ideal for Builder role on standard code generation and test execution. *Alternative:* `gemini-3.8-flash-medium` for lower latency. |
| `gemini-3.1-pro-high` | Gemini 3.1 Pro (High) | 2M | `full` | `reasoning`, `review` | `gemini-3.8-flash-high` | Deep reasoning and massive context flagship. Default for Researcher, complex Author tasks, and Reviewer. *Alternative:* `gemini-3.8-flash-high` when speed/quota takes precedence over depth. |

*Excluded*: `claude-sonnet-4-6` and `claude-opus-4-6-thinking` excluded due to restrictive subscription quotas.

---

## Core Inventory: ChatGPT Subscription (`codex`)

Zero marginal cost under active ChatGPT subscription (authenticated via OAuth/session tokens in `~/.codex`). Invoked via `codex` CLI and app-server daemon in `code_mode_only` sandbox.

### Models

| `model_id` | `display_name` | Context | Tool Mode | Supported Profiles | Quota Fallback | Description & Alternatives |
| --- | --- | ---: | --- | --- | --- | --- |
| `gpt-5.6-luna` | GPT-5.6-Luna | 272K / 872K | `code_mode_only` | `fast` | `gpt-5.5` | Fast lightweight model for quick code searches, file inspections, and simple diffs. *Alternative:* `gpt-5.5`. |
| `gpt-5.6-terra` | GPT-5.6-Terra | 272K / 872K | `code_mode_only` | `coding`, `review` | `gpt-reserve` | Local Codex default. Strong code generation, patch application, and verification. Default Builder model in Codex. *Alternative:* `gpt-5.6-sol`. |
| `gpt-5.6-sol` | GPT-5.6-Sol | 272K / 872K | `code_mode_only` | `fast`, `reasoning` | `gpt-reserve` | Balanced authoring and coordination model in Codex. Default for Author role and fallback for Coordinator. |
| `gpt-6-astra` | GPT-6-Astra | 272K / 872K | `code_mode_only` | `reasoning`, `coding` | `gpt-reserve` | Deep reasoning flagship for complex multi-file refactors, edge-case analysis, and debugging. Multi-agent v2 support. *Alternative:* `gpt-5.6-terra`. |
| `codex-auto-review` | Codex Auto Review | 272K / 872K | `code_mode_only` | `review` | `gpt-5.6-terra` | Specialized review model trained for evaluating diffs against specifications, test compliance, and standards. *Alternative:* `gpt-5.6-terra`. |
| `gpt-reserve` | GPT-Reserve | 272K / 872K | `code_mode_only` | *fallback* | None | Dedicated high-availability capacity pool automatically available when primary ChatGPT subscription limits are reached. |

---

## Canonical Capability Profile Mapping

| Capability Profile | Primary Model (`agy`) | Primary Model (`codex`) | Selection Rationale |
| --- | --- | --- | --- |
| `fast` | `gemini-3.8-flash-low` | `gpt-5.6-luna` | Sub-second response, minimal capability units, sufficient for status checks and small queries. |
| `coding` | `gemini-3.8-flash-high` | `gpt-5.6-terra` | Strong instruction following, diff generation, AST comprehension, and test fixing. |
| `reasoning` | `gemini-3.1-pro-high` | `gpt-6-astra` | High-depth reasoning for architecture, root-cause diagnosis, planning, and arbitration. |
| `review` | `gemini-3.1-pro-high` | `codex-auto-review` | Independent evaluation against requirements, risk detection, spec compliance checking. |

---

## Two-Tier Quota & Throttling Policy

1. **Intra-surface fallback**:
   - When a specific model hits rate limits or latency spikes, the agent automatically falls back to its configured `quota_fallback_id` on the same surface (e.g., `gpt-6-astra` → `gpt-reserve` / `gpt-5.6-terra`, or `gemini-3.1-pro-high` → `gemini-3.8-flash-high`).
2. **Cross-surface fallback**:
   - If an entire subscription surface hits a hard rate limit or outage, the Coordinator pauses the affected task branch and raises an Owner decision packet (Human Gate). With Owner approval, the task fails over to the alternative subscription surface (e.g. `codex` → `agy` or vice-versa).

---

## Supplementary / Non-Subscription Agent Surfaces (Reference Only)

These agents exist on the local system but require separate API credits or custom endpoints; they do not form part of the zero-marginal-cost baseline:

- **Hermes Agent** (`hermes`): Configured with `anthropic/claude-opus-4.6` via OpenRouter (pay-per-token API).
- **Pi Agent** (`pi`): Configured with custom `omni-joul` endpoint (`code/act`, `code/plan`, `default`).
