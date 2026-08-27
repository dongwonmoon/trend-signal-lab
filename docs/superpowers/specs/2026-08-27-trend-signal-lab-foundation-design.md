# Trend Signal Lab Foundation Design

**Date:** 2026-08-27
**Status:** Approved for repository setup; experiment implementation pending review

## Purpose

Trend Signal Lab is a research workspace for testing whether emerging Korean
keywords, names, and cultural phenomena can be detected from time-ordered
public data and explained with evidence.

It is deliberately not a production service yet. The repository exists to
preserve experiments, negative results, datasets' provenance, and decisions in
a reproducible form while keeping this work separate from Morrow.

## Product Hypothesis

The eventual product may help people who care about current culture discover a
term or name before they know to search for it, then understand why it is
emerging through source-backed context.

The two initial output levels are related rather than competing:

1. **Emerging keyword or name:** an observable candidate detected from data.
2. **Cultural phenomenon:** an interpretation formed by grouping related
   candidates and evidence.

The repository must not assume this hypothesis is true. Its first job is to
make the hypothesis falsifiable.

## Experiment Contract

Each experiment must state before execution:

- the single uncertainty it intends to reduce;
- the input dataset and its provenance;
- the expected output and human-readable examples;
- the baseline and evaluation method;
- success, failure, and stop conditions;
- what decision each possible result enables.

An experiment is successful when it enables a decision, including rejection or
revision of the product hypothesis. It is not required to produce an impressive
demo or a positive metric.

## Repository Boundary

This repository is independent from Morrow. It must not inherit Morrow's
product, privacy, release, mobile, or local-first rules without an explicit
reason. Reusable working principles such as small experiments, proportional
verification, and documentation closure may be adapted to this laboratory.

The initial repository will contain:

```text
trend-signal-lab/
├── AGENTS.md
├── README.md
├── docs/
│   ├── experiment-log.md
│   └── superpowers/specs/
├── notebooks/
├── scripts/
├── data/
│   ├── samples/
│   └── raw/
├── artifacts/
└── tests/
```

Only the design document is created in this setup step. The remaining paths
will be added when the first experiment requires them.

## Notebook and Script Roles

- Notebooks are for observation, visualization, and exploratory decisions.
- Scripts are for repeatable collection, preprocessing, and evaluation.
- Logic moves from a notebook into a script only after reuse or reproducibility
  makes the promotion useful.
- Tests cover stabilized processing contracts, not every exploratory cell.

This avoids both notebook-only irreproducibility and premature production
architecture.

## Data and Git Policy

- The GitHub repository is public from its first commit so the experiment and
  its negative results can be shared as open work.
- Every committed dataset or artifact must still pass a provenance, license,
  privacy, and secret review before publication.
- Raw or large datasets are not committed by default.
- Small, redistributable samples may be committed when their provenance and
  license are recorded.
- Collection scripts, manifests, time ranges, parameters, and hashes should be
  sufficient to explain or reproduce a dataset when the source permits it.
- Generated artifacts are committed only when they are durable evidence worth
  reviewing; disposable outputs remain ignored.
- Secrets and source credentials must never enter Git history.

## Initial Workflow

The first research sequence is:

1. Define examples of useful emerging keywords, names, and cultural phenomena.
2. Check whether people can judge those outputs consistently.
3. Reproduce an established trend-detection baseline on a timestamped public
   dataset.
4. Test whether the baseline can rediscover historical Korean examples.
5. Only then choose and integrate a sustainable production data source.

The input source, algorithm, and output contract must not all change in the
same experiment.

## Explicit Non-Goals

The initial setup does not include:

- a crawler fleet or scheduled pipeline;
- a web or mobile product;
- a production database or cloud deployment;
- recommendation or personalization;
- a custom NLP model;
- Morrow's complete harness, hooks, agents, or release process;
- a commitment to a specific category taxonomy or the label `MZ`.

## Completion Conditions

The repository foundation is ready for its first experiment when:

- the repository boundary and experiment contract are reviewed;
- a minimal Python and Jupyter environment can be reproduced;
- raw data, artifacts, secrets, and samples have explicit Git policies;
- the first experiment has one question and predetermined evaluation criteria;
- a fresh Codex session can recover the purpose and current experiment without
  Morrow context.
