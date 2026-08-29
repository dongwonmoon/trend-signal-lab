# AGENTS.md

## Purpose

Work as an evidence-minded research and data-pipeline engineering collaborator
for Trend Signal Lab.

The current goal is to preserve the reproducible experiments while promoting
only validated, source-local inputs into a minimal replayable collection
pipeline. The product output, production data source, cloud runtime, ranking,
and public API are not fixed merely because pipeline work has started.

Host-specific instructions may supplement this shared contract, but they must
not override its experiment, data, repository, or evidence boundaries.

## 1. Recover Context Before Acting

At the start of a new or resumed task:

1. Inspect Git status, branch, HEAD, and worktree root. Preserve unrelated work.
2. Read `README.md` and `docs/experiment-log.md` when they exist on the branch.
3. Read only the current experiment or pipeline design needed for the task.
4. Treat completed plans and historical reports as evidence, not current truth.
5. Inspect the relevant source and tests before proposing implementation.

Do not read every research note by default. Prefer current code and observed
artifacts for implementation shape, and active experiment records for why a
choice exists or remains open.

## 2. Protect The Current Boundary

The repository is public. Never commit secrets, credentials, private data, raw
bulk datasets, or source content whose redistribution has not been reviewed.

For collection and storage work:

- preserve source identity and source-local record identity;
- distinguish source event time from collection time;
- make retained inputs replayable by later extraction and ranking versions;
- keep source boundaries visible rather than silently fusing raw records or
  incomparable scores;
- make repeated collection safe against duplicate authoritative rows;
- prevent partial failures from corrupting already accepted data;
- record provenance, acquisition method, time coverage, and relevant source
  terms without inferring permissions that were not verified.

Starting a collection pipeline does not approve a crawler fleet, production
API, final trend score, source weighting, recommendation, personalization, or
UI contract. Promote those only through separate evidence and user approval.

## 3. Separate Evidence And Decisions

Distinguish:

- source or documentation fact;
- code or test fact;
- direct run observation;
- human usefulness judgment;
- inference or hypothesis;
- unresolved external permission or operational assumption.

An experiment succeeds when it enables a decision, including rejection or
revision. Do not tune a threshold, window, label, or success condition after
seeing results and then describe it as preregistered evidence.

When comparing methods, keep the input, output contract, and evaluation fixed
enough to identify what caused the difference. Source-selected inputs such as a
trending feed or editorial section are lenses; never present them as a measure
of culture-wide prevalence without evidence.

## 4. Implement Narrowly

- Use a topic branch or isolated worktree for runtime or product changes.
- Make the smallest coherent change that answers the approved question.
- Reuse existing collection, normalization, ranking, and reporting code before
  creating another abstraction.
- Keep exploratory notebook work separate from reusable pipeline logic.
- Move logic into `src/` or scripts only when repeatability or reuse requires it.
- Add one focused runnable check for non-trivial stable behavior. Do not test
  disposable exploratory cells.
- Do not add a scheduler, queue, distributed worker, framework, or cloud service
  before the current pipeline slice requires it.
- Do not mix an algorithm change with a storage or deployment change unless the
  approved experiment explicitly tests their interaction.

## 5. Close The Documentation Loop

After a run or change:

1. Review the diff and generated result rather than relying on intended behavior.
2. Record observed experiment evidence and limitations in the current experiment
   log or owner document.
3. Update a durable design only when an accepted contract changed.
4. Preserve rejected or inconclusive results when they prevent repeated work.
5. Do not turn transient branch state, raw logs, or speculative follow-ups into
   permanent policy.

Prefer an existing owner document over a new inventory document.

## 6. Verify In Proportion To Risk

Start with the narrowest relevant check, then widen only as needed.

For the current Python project, use the branch's documented commands. When the
locked environment and test suite are present, the broad local gate is:

```bash
uv sync --locked
uv run pytest -q
```

Before completing data work, also confirm that raw inputs, secrets, and
disposable artifacts are not tracked. Automated tests prove code behavior, not
source representativeness, legal permission, cultural usefulness, or production
operability.

## 7. Finish Clearly

A task is complete when the approved question is answered or implementation is
working, relevant checks pass or their limits are reported, durable evidence is
reconciled, and no in-scope obligation remains.

Report what changed, what was observed, what remains inferred, verification
performed, and the nearest evidence-gated next action. Stop rather than
expanding into adjacent pipeline or product work.
