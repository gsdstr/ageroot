# Assign default agents and model capability profiles to roles

Type: grilling
Status: resolved
Assignee: /root
Blocked by: 01, 02

## Question

Given the canonical role contract and account-specific model inventory, which
of Antigravity, Codex, Hermes, and Pi is the default and fallback executor for
each role, and which capability profile selects its recommended model?

## Comments

- Created while charting **Neutral orchestration templates v1 — decision map**.

## Answer

Default agent harnesses, fallback executors, and capability profiles are assigned to the canonical roles as follows:

### 1. Role Assignment Matrix

| Role | Capability Profile | Default Agent & Model | Intra-Surface Fallback | Cross-Surface Fallback |
|---|---|---|---|---|
| **Owner** | Human | Human User | None | None |
| **Coordinator** | `fast` / `reasoning` | `agy`: `gemini-3.8-flash-high` | `agy`: `gemini-3.8-flash-medium` | `codex`: `gpt-5.6-sol` (medium) |
| **Researcher** | `reasoning` | `agy`: `gemini-3.1-pro-high` | `agy`: `gemini-3.8-flash-high` | `codex`: `gpt-6-astra` (medium) |
| **Author** | `reasoning` / `fast` | `codex`: `gpt-5.6-sol` (medium) | `codex`: `gpt-reserve` | `agy`: `gemini-3.1-pro-high` |
| **Builder** | `coding` | `agy`: `gemini-3.8-flash-high` | `agy`: `gemini-3.8-flash-medium` | `codex`: `gpt-5.6-terra` (medium) |
| **Reviewer** | `review` | `codex`: `codex-auto-review` or `gpt-5.6-terra` | `codex`: `gpt-reserve` | `agy`: `gemini-3.1-pro-high` *(dependent on Builder)* |
| **Integrator** | `coding` / `fast` | `agy`: `gemini-3.8-flash-high` | `agy`: `gemini-3.8-flash-medium` | `codex`: `gpt-5.6-terra` |

### 2. Orthogonal Reviewer Rule (Anti-Self-Review)
- **Principle**: A Reviewer must never share the same agent harness and model family as the Builder on risk-bearing artifacts.
- **Default state**: Builder runs on `agy` (`gemini-3.8-flash-high`); Reviewer runs on `codex` (`codex-auto-review` or `gpt-5.6-terra`).
- **Failover state**: If Builder fails over to `codex` (`gpt-5.6-terra`), Reviewer dynamically switches to `agy` (`gemini-3.1-pro-high`) to maintain harness and model independence.

### 3. Fallback Hierarchy & External Agents
- **Tier 1 (Intra-Subscription)**: Automatic fallback within the primary subscription surface (e.g. `gemini-3.8-flash-high` → `gemini-3.8-flash-medium`, `gpt-5.6-terra` → `gpt-reserve`).
- **Tier 2 (Cross-Subscription)**: Automatic cross-failover between active subscriptions (`agy` ↔ `codex`) following the Cross-Surface column above.
- **Tier 3 (Metered Reference Agents)**: If both primary and secondary subscriptions are exhausted or unavailable, secondary reference agents (`hermes` with Claude Opus 4.6 via OpenRouter, or `pi` via Omni-Joul) serve as emergency fallbacks. Tier 3 requires an Owner Decision Packet before invocation to authorize pay-per-token API consumption.
