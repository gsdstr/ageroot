# Record subscription-accessible model inventory

Type: task
Status: resolved
Assignee: /root

## Question

What model names and invocation surfaces are currently accessible through the
user's Antigravity and ChatGPT subscriptions, and what factual constraints
(availability, concurrency, quotas, tool access) must the replaceable local
inventory record before roles can receive default model assignments?

## Comments

- Created while charting **Neutral orchestration templates v1 — decision map**.
- This is HITL: subscription visibility is user-account-specific. It unblocks
  default-agent and default-model assignment but does not require sharing
  credentials.

## Answer

The local subscription inventory is recorded in [model-inventory.md](../model-inventory.md).

1. **Inventory Scope**:
   - Zero-marginal-cost models under the Owner's active **Antigravity** (`agy`) and **ChatGPT** (`codex`) subscriptions.
   - Claude models under Antigravity are explicitly excluded due to restrictive subscription quotas.
   - Secondary agents (`hermes` via OpenRouter, `pi` via Omni-Joul) are categorized as non-subscription reference surfaces.

2. **Inventory Schema (7 core fields)**:
   - `model_id`: CLI/API model slug.
   - `display_name`: Human-readable label for logs and decision packets.
   - `provider_surface`: `agy` (full tool sandbox) vs `codex` (`code_mode_only`).
   - `context_window`: Standard and max token limits.
   - `tool_mode`: `full` vs `code_mode_only`.
   - `supported_profiles`: One or more of `fast`, `coding`, `reasoning`, `review`.
   - `quota_fallback_id`: Default intra-subscription model to invoke when throttled.
   - Detailed descriptions and alternatives provided per model to simplify Owner choices.

3. **Canonical Capability Profile Mappings**:
   - `fast`: `gemini-3.8-flash-low` (`agy`) / `gpt-5.6-luna` (`codex`).
   - `coding`: `gemini-3.8-flash-high` (`agy`) / `gpt-5.6-terra` (`codex`).
   - `reasoning`: `gemini-3.1-pro-high` (`agy`) / `gpt-6-astra` (`codex`).
   - `review`: `gemini-3.1-pro-high` (`agy`) / `codex-auto-review` or `gpt-5.6-terra` (`codex`).

4. **Two-Tier Quota & Fallback Policy**:
   - *Intra-surface*: Automatic fallbacks within the same subscription (e.g. `gpt-6-astra` → `gpt-reserve` / `gpt-5.6-terra`; `gemini-3.1-pro-high` → `gemini-3.8-flash-high`).
   - *Cross-surface*: If an entire subscription surface is exhausted or unavailable, the Coordinator pauses the affected branch and raises an Owner decision packet before failing over across subscriptions.
