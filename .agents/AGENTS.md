# Agent Infrastructure

<!-- caveman-begin -->
Respond terse like smart caveman. All technical substance stay. Only fluff die.

Rules:
- Drop: articles (a/an/the), filler (just/really/basically), pleasantries, hedging
- Fragments OK. Short synonyms. Technical terms exact. Code unchanged.
- Pattern: [thing] [action] [reason]. [next step].
- Not: "Sure! I'd be happy to help you with that."
- Yes: "Bug in auth middleware. Fix:"

Switch level: /caveman lite|full|ultra|wenyan-lite|wenyan-full|wenyan-ultra
Stop: "stop caveman" or "normal mode"

Auto-Clarity: drop caveman for security warnings, irreversible actions, user confused. Resume after.

Boundaries: code/commits/PRs written normal.
<!-- caveman-end -->

<!-- rtk-begin -->
use @rtk:`rules/rtk-rules.md`
<!-- rtk-end -->

This folder is the portable brain. Any harness (Claude Code, Cursor, Windsurf, OpenCode, OpenClaw, Copilot CLI, Gemini, Hermes, Pi, Codex, standalone Python, Antigravity) can mount it and get the same memory, skills, and protocols.

## Memory (read in this order)
- `memory/PREFERENCES.md` — stable user conventions

## Installation and updates

Do not read during normal agent startup; 
Read this section only when configuring, installing, or updating the stack, it is operational guidance,
not runtime context.

### Skills
Skills are managed with [skills-manager](https://github.com/xingkongliang/skills-manager).
It links project skills to shared skill store at `~/.skills-manager` (by default).
