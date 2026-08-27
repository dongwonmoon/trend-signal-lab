# Trend Signal Lab Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a safe public research repository with a reproducible Python/Jupyter environment and one pre-registered output-calibration experiment, without building a crawler, NLP pipeline, or service.

**Architecture:** Repository-level documents define the lab boundary and evidence rules. `uv` owns the Python environment and lockfile, while Jupyter is used only for observation and visualization; reusable logic will move to scripts later. The first experiment validates the human-facing output contract before any detection algorithm is selected.

**Tech Stack:** Git/GitHub, Python 3.12–3.14, uv, JupyterLab 4, pandas 2, matplotlib 3

## Global Constraints

- The repository is public from its first commit.
- Never commit secrets, credentials, private data, raw bulk datasets, or artifacts without provenance and license review.
- Each experiment reduces one named uncertainty and pre-registers its input, output, baseline, evaluation, success, failure, stop, and decision conditions.
- Notebooks are for exploration; scripts are introduced only when repeatability or reuse makes them useful.
- Do not add a crawler, scheduler, production database, cloud deployment, custom NLP model, recommendation, or product UI in this plan.
- Do not transplant Morrow's complete harness, hooks, agents, release process, product rules, or `MZ` taxonomy.

---

## File Map

- `README.md`: public project overview, current status, and exact local commands.
- `AGENTS.md`: repository-specific recovery, experiment, evidence, data, and scope rules.
- `.gitignore`: prevents local environments, secrets, raw datasets, and disposable artifacts from entering the public repository.
- `pyproject.toml`: declares the non-package Python/Jupyter environment.
- `uv.lock`: pins the resolved environment for reproducibility.
- `docs/experiment-log.md`: append-only index of experiment questions, results, and decisions.
- `docs/experiments/001-output-calibration.md`: pre-registered first experiment contract.
- `data/samples/README.md`: rules for committing small redistributable samples.

### Task 1: Public Repository Operating Contract

**Files:**
- Create: `README.md`
- Create: `AGENTS.md`
- Create: `.gitignore`

**Interfaces:**
- Consumes: foundation design at `docs/superpowers/specs/2026-08-27-trend-signal-lab-foundation-design.md`
- Produces: recovery instructions and safety rules used by every later experiment

- [ ] **Step 1: Create the public README**

Create `README.md` with this content:

```markdown
# Trend Signal Lab

Trend Signal Lab tests whether emerging Korean keywords, names, and cultural
phenomena can be detected from time-ordered public data and explained with
source-backed evidence.

This repository is a research lab, not a production service. Positive and
negative results are both expected outputs.

## Current status

Repository foundation and first experiment design. No crawler, NLP pipeline,
or product has been validated yet.

## Research contract

Each experiment must define one uncertainty, its data provenance, expected
output, baseline, evaluation, success/failure/stop conditions, and the decision
enabled by each result before execution.

The initial output levels are:

1. an emerging keyword or name detected as an observable candidate;
2. a cultural phenomenon interpreted from related candidates and evidence.

See the [foundation design](docs/superpowers/specs/2026-08-27-trend-signal-lab-foundation-design.md)
and [experiment log](docs/experiment-log.md).

## Local environment

Requirements:

- Python 3.12, 3.13, or 3.14
- [uv](https://docs.astral.sh/uv/)

After Task 2 is complete:

```bash
uv sync
uv run jupyter lab
```

Raw datasets, credentials, and disposable artifacts are intentionally excluded
from Git. Only source-reviewed, redistributable samples may be committed.
```

- [ ] **Step 2: Create repository-specific agent instructions**

Create `AGENTS.md` with this content:

```markdown
# AGENTS.md

## Purpose

Work as an evidence-minded research engineering collaborator for Trend Signal
Lab. The goal is to learn whether useful emerging Korean cultural signals can
be detected and explained, not to defend the idea or rush into a service.

## Recover Context

At the start of a task:

1. Inspect `git status` and preserve unrelated changes.
2. Read `README.md`.
3. Read `docs/experiment-log.md`.
4. Read only the current experiment contract under `docs/experiments/`.
5. Read the foundation design when repository scope or data policy matters.

## Experiment Discipline

- One experiment reduces one named uncertainty.
- Pre-register input, provenance, output, baseline, evaluation, success,
  failure, stop, and decision conditions before seeing the result.
- Do not change input, process, and output contract in the same experiment.
- Distinguish sourced fact, direct observation, measurement, inference, and
  preference.
- Preserve negative results and rejected hypotheses in the experiment log.
- A successful experiment enables a decision; it does not need a positive
  metric or impressive demo.
- Prefer established baselines before inventing a new algorithm.

## Notebook and Script Boundary

- Use notebooks for observation, visualization, and exploratory decisions.
- Keep data acquisition, preprocessing, and reusable evaluation in scripts once
  repeatability or reuse is demonstrated.
- Do not hide authoritative logic only in executed notebook state.
- Add tests when a processing contract stabilizes; do not test disposable
  exploratory cells.

## Public Data Safety

- This repository is public. Never commit secrets, credentials, private data,
  raw bulk datasets, or unreviewed scraped content.
- Record source, time range, acquisition method, license or terms, and relevant
  hashes for every dataset.
- Commit only small samples that are redistributable and necessary for review.
- Keep `data/raw/` and disposable `artifacts/` out of Git.
- Do not bypass robots, authentication, rate limits, or access controls.

## Scope Control

- This is not Morrow and does not inherit Morrow's product or release rules.
- Do not add a crawler fleet, scheduler, production database, cloud deployment,
  custom NLP model, recommendation, or product UI without a successful prior
  experiment and an approved design.
- Stop when the current experiment's decision condition is satisfied.
```

- [ ] **Step 3: Create the public-repository ignore policy**

Create `.gitignore` with this content:

```gitignore
# Python
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Jupyter
.ipynb_checkpoints/

# Local configuration and secrets
.env
.env.*
!.env.example

# Raw/private data and disposable outputs
data/raw/
data/private/
artifacts/

# Local editors and OS
.DS_Store
.idea/
.vscode/
```

- [ ] **Step 4: Verify the operating contract**

Run:

```bash
git diff --check
rg -n "One experiment|Pre-register|public|data/raw|crawler" README.md AGENTS.md .gitignore
git status --short
```

Expected: no whitespace errors; the required experiment, public-data, raw-data,
and scope terms are present; only the three task files are newly added.

- [ ] **Step 5: Commit the operating contract**

```bash
git add README.md AGENTS.md .gitignore
git commit -m "docs: define trend lab operating contract"
```

### Task 2: Reproducible Python and Jupyter Environment

**Files:**
- Create: `pyproject.toml`
- Create: `uv.lock` via `uv lock`

**Interfaces:**
- Consumes: Python 3.12–3.14 and uv available on the host
- Produces: `uv sync`, `uv run jupyter lab`, pandas, and matplotlib for later notebooks

- [ ] **Step 1: Confirm the missing project environment**

Run:

```bash
test ! -f pyproject.toml
jupyter --version
```

Expected: the first command passes and the second command fails because Jupyter
is not globally installed. This records why a repository-owned environment is
needed.

- [ ] **Step 2: Declare the minimal non-package environment**

Create `pyproject.toml` with this content:

```toml
[project]
name = "trend-signal-lab"
version = "0.1.0"
description = "Experiments for discovering emerging Korean trend signals"
requires-python = ">=3.12,<3.15"
dependencies = [
  "jupyterlab>=4.4,<5",
  "matplotlib>=3.10,<4",
  "pandas>=2.3,<3",
]

[tool.uv]
package = false
```

- [ ] **Step 3: Resolve and install the environment**

Run:

```bash
uv lock
uv sync
```

Expected: `uv.lock` is created and `.venv/` is created locally but remains
ignored by Git.

- [ ] **Step 4: Verify imports and the notebook entry point**

Run:

```bash
uv run python -c "import pandas as pd; import matplotlib; print(pd.__version__, matplotlib.__version__)"
uv run jupyter --version
git check-ignore .venv
git diff --check
```

Expected: pandas and matplotlib versions print, Jupyter components print,
`.venv` is reported as ignored, and no whitespace errors exist.

- [ ] **Step 5: Commit the reproducible environment**

```bash
git add pyproject.toml uv.lock
git commit -m "build: add reproducible notebook environment"
```

### Task 3: Pre-register Experiment E001

**Files:**
- Create: `docs/experiment-log.md`
- Create: `docs/experiments/001-output-calibration.md`
- Create: `data/samples/README.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: the two-level output hypothesis from the foundation design
- Produces: a bounded human-calibration experiment that must pass before an algorithm or crawler is selected

- [ ] **Step 1: Create the experiment log**

Create `docs/experiment-log.md` with this content:

```markdown
# Experiment Log

This file records decisions, including negative results. Execution details and
evidence belong in each experiment contract.

| ID | Question | Status | Decision |
| --- | --- | --- | --- |
| E001 | Can the owner apply one output rubric to candidate keywords, names, cultural phenomena, and controls without excessive ambiguity? | Ready | Pending execution |

## Status vocabulary

- `Draft`: the contract is incomplete and execution is forbidden.
- `Ready`: question and decision conditions are pre-registered.
- `Running`: input collection or evaluation has started.
- `Complete`: evidence and a decision are recorded.
- `Stopped`: the stop condition fired; retain the evidence and reason.
```

- [ ] **Step 2: Create the E001 output-calibration contract**

Create `docs/experiments/001-output-calibration.md` with this content:

```markdown
# E001: Output Calibration

**Status:** Ready
**Owner:** dongwonmoon

## Uncertainty

Before choosing data sources or algorithms, can the intended first user apply a
single concrete output rubric to emerging keywords, names, cultural phenomena,
and negative controls without excessive ambiguity?

## Why this comes first

An algorithm cannot be evaluated while a desirable output is undefined. This
experiment tests the output contract only; it does not test automatic discovery.

## Input

Exactly 15 manually sourced Korean-language candidates:

- 5 suspected emerging keywords or names;
- 5 suspected cultural phenomena;
- 5 established-popular, stale, duplicated, or noisy controls.

Use publicly accessible evidence from a fixed 30-day observation window. Every
candidate requires two timestamped URLs from independent publishers or
platforms. Do not collect private user data or bulk page content.

## Candidate record

Record these fields in a CSV under `data/samples/`:

```text
candidate_id,candidate_label,candidate_type,category,window_start,window_end,source_url_1,source_published_at_1,source_url_2,source_published_at_2,why_now,phenomenon_group,decision,rejection_reason
```

Allowed `candidate_type` values are `keyword_or_name`, `cultural_phenomenon`,
and `control`. Allowed `decision` values are `accept`, `reject`, and `unclear`.

## Output rubric

Accept a candidate only when:

1. its label is understandable without requiring the user to know it already;
2. both sources support that it matters inside the observation window;
3. `why_now` states a concrete recent change rather than general popularity;
4. the entry adds information beyond a duplicate spelling or source headline;
5. a cultural phenomenon names a shared pattern supported by at least two
   related signals, rather than merely renaming one keyword.

Reject stale popularity, advertisements without independent evidence, duplicate
spellings, isolated incidents, and candidates supported only by intuition.
Use `unclear` only when the evidence is insufficient to accept or reject under
the rubric.

## Baseline

The baseline is an unstructured list containing only candidate labels and URLs.
E001 compares whether the structured record and rubric make a decision possible;
it does not compare detection algorithms.

## Evaluation

After all 15 records are filled, count `accept`, `reject`, and `unclear`, then
write one sentence explaining each unclear decision and any rubric clause that
was interpreted inconsistently.

## Success condition

At least 12 of 15 candidates receive `accept` or `reject`, every accepted entry
has two independent timestamped sources, and no rubric clause requires two
conflicting interpretations.

## Failure condition

Four or more candidates remain `unclear`, an accepted entry lacks source-backed
`why_now`, or the same rubric clause is repeatedly interpreted in conflicting
ways.

## Stop condition

Stop after exactly 15 decisions. Do not add candidates to rescue the result and
do not change the rubric after evaluating the first candidate. Record a needed
revision as the experiment decision instead.

## Decision enabled

- On success: preserve the output schema and design a separate historical
  baseline-reproduction experiment.
- On failure: revise the output types or rubric, then run a newly numbered
  calibration experiment before selecting a crawler or algorithm.
```

- [ ] **Step 3: Document sample-data publication rules**

Create `data/samples/README.md` with this content:

```markdown
# Reviewable Data Samples

Only small samples needed to review an experiment belong here.

Before committing a sample, record in the experiment contract:

- source and canonical URL;
- acquisition date and observation window;
- license or terms assessment;
- fields retained and fields omitted;
- whether redistribution is permitted;
- a content hash when the source can be reacquired.

Do not commit private data, credentials, raw bulk pages, paywalled content,
or a sample whose redistribution status has not been reviewed.
```

- [ ] **Step 4: Link the current experiment from the README**

In `README.md`, add this paragraph after the current-status paragraph:

```markdown
The current experiment is [E001: Output Calibration](docs/experiments/001-output-calibration.md).
It validates what a useful result looks like before data-source or algorithm work.
```

- [ ] **Step 5: Verify the pre-registration is complete**

Run:

```bash
rg -n "Uncertainty|Input|Baseline|Evaluation|Success condition|Failure condition|Stop condition|Decision enabled" docs/experiments/001-output-calibration.md
rg -n "E001|Ready|Pending execution" docs/experiment-log.md README.md
git diff --check
git status --short
```

Expected: every pre-registration field is present, E001 is linked and marked
ready but unexecuted, and only the four task files are changed.

- [ ] **Step 6: Commit the first experiment contract**

```bash
git add README.md docs/experiment-log.md docs/experiments/001-output-calibration.md data/samples/README.md
git commit -m "docs: preregister output calibration experiment"
```

### Final Verification

- [ ] Run the full repository check:

```bash
uv sync --locked
uv run python -c "import pandas as pd; import matplotlib; print(pd.__version__, matplotlib.__version__)"
uv run jupyter --version
git diff --check HEAD~3..HEAD
git status --short
```

Expected: the locked environment installs, imports and Jupyter resolve, the
three implementation commits have no whitespace errors, and the worktree is
clean.

- [ ] Push only after the user explicitly approves publication of the implementation commits:

```bash
git push origin main
```

