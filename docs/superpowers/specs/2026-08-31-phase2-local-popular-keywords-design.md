# Phase 2 — Local daily popular-keyword page

**Date:** 2026-08-31
**Status:** Approved by user on 2026-08-31
**Parent:** [Product roadmap](2026-08-30-product-roadmap-design.md)
**Plan:** [Implementation handoff](../plans/2026-08-31-phase2-local-popular-keywords.md)

## Purpose and decision

Turn retained Wikimedia data into a small, real browsing experience: open a
local page and see which names and topics received many views on one day.
Familiar names remaining popular can be interesting; novelty is not required.

Phase 1 established that the source can surface recognizable topics. The user
judged its results broadly positive. That supports building a local product,
not claiming that daily rankings or a final trend algorithm are validated.

The first product view uses **one completed UTC day, ranked by views**. It does
not reuse the two 30-day averages or growth Ranking B as a daily result. This
is an explicit product choice to show popularity, not a finding that growth is
unhelpful. Keep the historical experiments and their artifacts intact.

Phase 2 ends at a usable local page. Automatic collection, public deployment,
and daily refresh remain Phase 3 work.

## Chosen approach

Generate a source-local JSON result, then render it into self-contained static
HTML. The browser does not fetch raw data or call an API. The HTML can be opened
as a local file without a running application server.

- **Static HTML — selected:** sufficient for a fixed read-only list, with no
  new runtime dependency or frontend build tooling.
- **Streamlit — deferred:** reconsider if real date selection or other Python-
  driven interaction becomes necessary. It is not required just to show a table.
- **Separate frontend/backend — deferred:** no current API or interactive
  behavior justifies these additional components.

Keep the work in this repository. Neither a new production repository nor a
future framework rewrite is required by this phase.

## Input and date selection

Reuse the daily files under `data/raw/wikimedia/ko.wikipedia.org/` and the
existing collector's stored contract. Generation is offline and never collects
data as a side effect of opening or building the page.

- Default to the most recent retained date strictly before the current UTC
  date. This is the latest locally available completed day, not necessarily
  yesterday or the newest date available upstream.
- Permit an explicit completed date for replay and checking historical samples.
- After selecting a file, validate its object/row shapes, source, project,
  matching filename and snapshot date, UTC time zone, collection metadata,
  nonempty article list, unique article names, nonnegative integer views, and
  positive integer source ranks. Tied or skipped source ranks remain valid.
- A missing explicitly requested file, invalid selected file, or no eligible
  snapshot is an error. Do not silently fall back to an older file.
- Do not scan or aggregate 60 days merely to display one day. An older missing
  day outside the selected input is irrelevant to this calculation.

The display must retain the actual measurement date and UTC label. A snapshot
does not become current because the page was regenerated. Korean-language
Wikipedia readership is the source scope, not Korean geography or culture-wide
attention. Top-list absence is not evidence of zero actual views.

## Selection and output contract

Process the selected day's articles without NLP or cross-source normalization:

1. Exclude exact source-title prefixes `위키백과:`, `특수:`, and `파일:`.
2. Sort remaining articles by views descending, then original page name
   ascending for deterministic ties.
3. Take at most 20 and assign consecutive display positions starting at 1.

These exclusions are a limited Wikimedia display policy, not a universal noise
filter or a complete namespace resolver. Do not reject every title containing
a colon. Do not add aliases, other namespaces, topic stopwords, or subjective
content filtering just because an implementation agent dislikes a result.
Revisit the policy when actual remaining noise or an incorrect exclusion is
observed. Never edit the retained raw files.

The generated JSON contains:

- `source`, `project`, `snapshot_date`, `time_zone`, `collected_at`, and
  `request_url`, carried from the validated input;
- `ranking`: `daily_views`, to make the measurement explicit;
- `items`: objects with `rank` (display position), `source_rank`, `page`
  (unaltered source title), and `views` (the selected day's integer count).

The browser label replaces underscores with spaces; this does not change page
identity, sorting, or merge two titles. No previous-window count, growth score,
rank-change arrow, or inferred explanation belongs in this output.

Write generated results under ignored `artifacts/`; do not commit raw data or
generated source-content lists. This is an internal file contract, not a public
API schema or a generic multi-source model.

## Page and failure behavior

Show only:

- title `인기 키워드`;
- explanation `한국어 위키백과 조회수 기준`;
- actual data date, labeled as a one-day UTC measurement;
- a table of position, display name, and daily views.

Use semantic headings and table headers, readable default styling, and HTML
escaping for source-derived text. No JavaScript, remote assets, detail links,
accounts, search, animation, or custom design system is needed.

If fewer than 20 entries remain, show only those present. If none remain after
the specified exclusions, show an explicit empty-state message with the source
and date; do not relax the filter or fabricate items.

Validate and render before replacing accepted output. Replace individual files
atomically and publish the self-contained HTML last, after JSON generation
succeeds. A failed build must return a nonzero exit status and must not truncate
the existing page. No two-file transaction manager is required: an interrupted
write may leave newer JSON beside older HTML, but the old page remains internally
consistent with its own date and values. Rerunning repairs the pair.

## Code boundary and verification

Reuse the existing collector contract and suitable small helpers after reading
their actual behavior. Do not force this daily path through Phase 1's first/
last-30-day window splitter or change the historical algorithm to serve the UI.
A small generator with ranking and rendering functions is sufficient; no
adapter hierarchy, package reorganization, or new dependency is required.

Use the existing pytest setup for a focused check of date selection, source
validation, exact-prefix exclusions, stable ties, original-name preservation,
escaping, and safe failure. Group related assertions rather than building a
separate test architecture. Repeat generation from a fixed snapshot and compare
JSON and HTML bytes; do not insert wall-clock generation time into the artifacts.

Before declaring the phase complete:

1. Generate the latest retained day and two earlier retained days into separate
   ignored output locations. Record the actual dates and lists; these are smoke
   observations, not preregistered trend-quality evidence.
2. Open the resulting HTML in a real browser and confirm the date, source,
   ordering, names, counts, and basic readability. Report if browser inspection
   is unavailable rather than equating tests with visual verification.
3. Obtain the user's judgment of whether the daily list is understandable and
   worth browsing. A positive 30-day result does not substitute for this check.
4. Run the relevant tests and the documented broad gate, inspect the final diff,
   and confirm raw inputs and disposable outputs remain untracked.
5. Update the experiment log with observations and limitations, and README with
   the actual local generation/opening instructions.

No requirement demands a perfectly clean top 20. Stop and discuss if the daily
list is unintelligible, source integrity is uncertain, or making it useful
requires an unapproved ranking change. Preserve the disappointing output; do
not silently tune until it looks positive.

## Deferred decisions and reconsideration triggers

- **Growth B and persistent-versus-rising presentation:** revisit when choosing
  how users should distinguish those signals. Missing historical top-list rows
  must not become claims of zero audience interest.
- **Weekly/monthly views:** revisit after the daily view is useful and a longer
  period answers a concrete user question.
- **Semantic filtering and namespace expansion:** revisit observed errors, not
  hypothetical noise from sources not yet selected.
- **Additional sources and shared processing:** keep each source's identities
  and semantics separate until a second implemented source demonstrates reuse.
- **Collection scheduling, stale-refresh alerts, and hosting:** Phase 3; Phase 2
  does not promise an automatically current page.
- **Keyword history and why-it-is-popular explanations:** later detail work;
  neither is necessary to complete the current list.

The linked implementation plan follows the roadmap's purpose, ownership,
verification, and escalation handoff format. Approval of this written spec
does not mean runtime implementation or daily-output acceptance is complete.
