# Agent Instruction Port Design

**Date:** 2026-08-30
**Status:** Approved and implemented

## Goal

Adapt the useful Morrow collaboration structure to Trend Signal Lab as it moves
from reproducible experiments into minimal data collection, without importing
Morrow's product contract or its mature audit harness.

## Structure

- `AGENTS.md` owns host-neutral experiment, public-data, collection, evidence,
  repository, and verification rules.
- `agent-instructions/codex.md` owns Codex delegation and custom-agent routing.
- `agent-instructions/opencode.md` owns OpenCode scope and capability honesty.
- `.codex/config.toml` and `opencode.json` load the host adapters.
- `.codex/agents/trend_data_pipeline_auditor.toml` defines one read-only,
  bounded specialist for consequential data-pipeline evidence questions.

## Deliberate Omissions

Morrow's mobile auditor, stewardship Skill, JSON report contract, hooks, queue,
checkpoint state, Git hook, and Node harness are not copied. Trend Signal Lab
has not demonstrated repeated failures that justify those mechanisms. Generic
code navigation, implementation, and review use existing agent roles rather
than project-specific duplicates.

The instructions do not choose a production source, collector type, cloud
provider, scheduler, database, final ranking, or API. Those remain task-level
decisions supported by current experiment evidence.
