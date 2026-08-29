# Codex Instructions

This file supplements the root `AGENTS.md` for Codex sessions. The root file,
current experiment record, and approved pipeline design remain authoritative.

## Subagents

Use subagents only when a bounded assignment is plausibly cheaper than the main
session doing and reviewing the same work. The main session owns experiment and
product judgment, integration, and final verification.

- Use one worker by default and give it one read-only boundary or explicit file
  ownership. Do not create overlapping writers or recursive agent trees.
- A short complete brief states the goal, boundary, constraints, expected
  evidence, and concise return format. Let the worker recover routine code
  details instead of restating the repository.
- Good bounded work includes code mapping, repetitive implementation, focused
  tests, log triage, and independent diff review.
- Do not delegate source-policy, cultural usefulness, product promise, or final
  experiment interpretation as if the worker could decide them.
- Review the returned diff and evidence, then verify in proportion to risk.

Use `trend_data_pipeline_auditor` only for one consequential data-source or
storage decision, one bounded collection-pipeline diff, or one explicit
research-to-operational boundary review. Do not invoke it for ordinary edits or
to prove that custom agents are available.

If the configured custom agent or model is unavailable, report that fact rather
than silently claiming an equivalent review.
