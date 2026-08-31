# Public culture source gate — 2026-08-30

## Scope update — 2026-08-31

The [roadmap's current priorities](2026-08-30-product-roadmap-design.md#current-priorities--2026-08-31)
advance second-source investigation before public deployment. The findings below
remain dated historical evidence, not a new approval or permanent rejection.
For the next investigation, immediate 60-day backfill is not mandatory: record
actual history and acquisition cadence instead. Identity, event time, retention,
and permission checks remain required; delayed deployment does not grant data
rights. Verify current first-party conditions before recommending adoption.

The original gates and candidate findings are preserved to explain earlier
choices. No source has been newly researched, sampled, or selected by this
documentation update. Handoff B in the roadmap defines the bounded next task.

## Decision

No single evaluated candidate clears all five original gates at the requested
Korean culture/entertainment breadth. Wikimedia clears the operational and
public-use gates but is a broad Korean-Wikipedia readership lens. KOPIS clears
the gates for a narrower performing-arts subset, subject to production
approval. KOBIS is explicitly rejected because
its terms prohibit retention absent prior permission. This is a source-policy
decision, not legal advice.

The product boundary assumed here is narrow: expose only derived popular
keywords/names; do not expose article/video bodies or evidence content; do not
fuse sources or scores.

Access date for every source below: **2026-08-30**.

## Original gates — 2026-08-30

1. Korean culture/entertainment relevance.
2. At least the most recent 60 days can be backfilled immediately.
3. Stable item identity and event/publish time.
4. Daily incremental collection is possible.
5. Official terms explicitly support use/processing in an externally public
   product, with attribution/display/storage restrictions understood.

“Pass” means directly supported by first-party documentation. “Inference” is
called out and is not treated as permission.

## Compact comparison

| Candidate | 1 relevance | 2 60-day backfill | 3 identity + time | 4 daily increment | 5 public use terms | Decision |
|---|---|---|---|---|---|---|
| SBS News entertainment archive / RSS surface | Pass: SBS labels the `sectionType=14` page “연예” and lists dated stories ([official archive](https://news.sbs.co.kr/news/newsSection.do?sectionType=14)). | Pass in the repository’s E002 run: dated archive pages covered 60 requested dates; this is a code/run fact, not a promise by SBS. | Pass for the observed archive rows: `news_id`, link, title, and publication time are exposed by the first-party listing (the archive shows dated entries; [example dated archive](https://news.sbs.co.kr/news/newsSection.do?pageDate=20260828&pageIdx=2&sectionType=14)). | Pass operationally: the archive exposes date navigation and current-day listings ([archive](https://news.sbs.co.kr/news/newsSection.do?sectionType=14)). | **Unresolved / do not infer permission.** The reviewed SBS pages identify copyright ownership/site content but do not grant a licence for storing/processing metadata in a public product. SBS also publishes “무단 전재, 재배포 및 AI학습 이용 금지” on its pages ([example keyword page](https://news.sbs.co.kr/news/keywordList.do?keyword=%EC%A0%80%EC%9E%91%EA%B6%8C&pageIdx=3)). | Reject pending written permission or an explicit API/data licence. |
| KOBIS (Korean Film Council Open API) | Pass for Korean film/box-office culture: the official service provides daily and weekly box office, movie, company, and people services ([service home](https://www.kobis.or.kr/kobisopenapi/homepg/main/main.do)). | Pass technically by inference from the daily-box-office endpoint accepting a target date; a 60-day loop would be required ([service list](https://kobis.or.kr/kobisopenapi/webservice)). | Pass for API resources in principle; exact field-level identity/time contract should be confirmed from the endpoint schema ([service list](https://kobis.or.kr/kobisopenapi/webservice)). | Pass technically by inference: daily box-office retrieval is available. | **Fail.** Article 6(2) requires real-time use and prohibits copying, storing, or retransmitting results; Article 8(3)(2) bars use/reproduction/publication/broadcast/provision to third parties without prior permission. The official terms also require independent display and clear source attribution (Articles 3(2), 3(5), 6(5)) ([KOBIS Open API terms](https://kobis.or.kr/kobisopenapi/homepg/board/findProvisionInfo.do)). | Reject for a replayable retained pipeline unless written permission is obtained. |
| KOPIS 예매상황판 (Korean Performing Arts Integrated Data Network) | Pass for the explicit performing-arts subset of Korean culture: the official guide describes the box-office service as “예매상황판 조회 서비스” ([official KOPIS guide PDF](https://kopis.or.kr/upload/openApi/%EA%B3%B5%EC%97%B0%EC%98%88%EC%88%A0%ED%86%B5%ED%95%A9%EC%A0%84%EC%82%B0%EB%A7%9DOpenAPI%EA%B0%9C%EB%B0%9C%EA%B0%80%EC%9D%B4%EB%93%9C.pdf)). | Pass: `stdate`/`eddate` accept at most 31 days, so two requests cover 60 days ([guide, section 9](https://kopis.or.kr/upload/openApi/%EA%B3%B5%EC%97%B0%EC%98%88%EC%88%A0%ED%86%B5%ED%95%A9%EC%A0%84%EC%82%B0%EB%A7%9DOpenAPI%EA%B0%9C%EB%B0%9C%EA%B0%80%EC%9D%B4%EB%93%9C.pdf)). | Pass: response includes `basedate`, rank, performance name/period/venue/area, poster, and stable `mt20id` performance ID ([guide, section 9](https://kopis.or.kr/upload/openApi/%EA%B3%B5%EC%97%B0%EC%98%88%EC%88%A0%ED%86%B5%ED%95%A9%EC%A0%84%EC%82%B0%EB%A7%9DOpenAPI%EA%B0%9C%EB%B0%9C%EA%B0%80%EC%9D%B4%EB%93%9C.pdf)). | Pass technically: date-range requests support daily reruns; service-key authentication is required ([guide](https://kopis.or.kr/upload/openApi/%EA%B3%B5%EC%97%B0%EC%98%88%EC%88%A0%ED%86%B5%ED%95%A9%EC%A0%84%EC%82%B0%EB%A7%9DOpenAPI%EA%B0%9C%EB%B0%9C%EA%B0%80%EC%9D%B4%EB%93%9C.pdf)). | Pass at the portal level: dataset 15097812 currently states “이용허락범위 제한 없음”; production-stage approval and a key remain operational prerequisites ([data.go.kr record](https://www.data.go.kr/data/15097812/openapi.do)). | Strongest candidate for a performing-arts-only first source; not a general entertainment source, and source-provided rank would change the existing NLP input semantics. |
| Wikimedia Analytics API — Korean Wikipedia pageviews/top | **Scope mismatch.** Korean Wikipedia is a Korean-language readership lens, not culture/entertainment-only or Korean-geographic audience ([API getting started](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/documentation/getting-started.html)). | Pass: the top endpoint supports a day value and documentation states history since 2015-07-01 ([top endpoint](https://wikimedia.org/api/rest_v1/metrics/pageviews/top/ko.wikipedia.org/all-access/2024/01/01); [API reference](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/)). | Pass: daily top responses provide project/date/article snapshot identity; pageview concepts define the metric ([pageviews concepts](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/concepts/page-views.html)). | Pass: a daily top request can be repeated for each date ([API reference](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/)). | Pass: Analytics API data is CC0; requests require an identified User-Agent ([access policy](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/documentation/access-policy.html)). | Operational/legal pass, but reject for the original culture/entertainment breadth gate. |
| YouTube Data API / trending-video metadata | Pass for entertainment discovery; the API exposes video title, category, ID, and `snippet.publishedAt` ([videos resource](https://developers.google.com/youtube/v3/docs/videos)). | Fail for a general 60-day “trending” backfill: the API resource docs provide video metadata, while the documented quota/search model does not provide historical Trending snapshots equivalent to E001 ([API overview/quota](https://developers.google.com/youtube/v3/getting-started)). | Pass: YouTube documents a unique video ID and ISO-8601 `snippet.publishedAt` ([videos resource](https://developers.google.com/youtube/v3/docs/videos)). | Partial: API polling is possible, but a daily trending snapshot feed is not established by the reviewed docs. | **Fail for the current product shape without separate approval.** Developer Policies prohibit independently calculated/derived metrics that replace or provide new API data and prohibit compiling/aggregating authorized API data except for the owner/authorized representative; they also require attribution and preservation of notices ([Developer Policies](https://developers.google.com/youtube/terms/developer-policies); [API Terms](https://developers.google.com/youtube/terms/api-services-terms-of-service)). The proposed public popularity keywords are an independently calculated aggregate, so permission cannot be inferred. | Reject. Existing E001 is a reproducible historical experiment, not a public-source licence. |

## Candidate findings

### SBS

**Verified facts.** The first-party archive identifies the section as
entertainment (`연예`), exposes dated pages, and displays story entries with
links and publication times ([archive](https://news.sbs.co.kr/news/newsSection.do?sectionType=14)).
The repository’s E002 run directly observed a 60-date archive traversal and
retained only metadata; that is repository evidence, not an SBS contractual
grant.

**Policy boundary.** A public page being readable, or an RSS/archive endpoint
being technically collectible, does not itself grant permission to copy,
store, transform, or display it. The reviewed SBS material includes explicit
anti-redistribution/AI-training wording (“무단 전재, 재배포 및 AI학습 이용
금지”) ([SBS page](https://news.sbs.co.kr/news/keywordList.do?keyword=%EC%A0%80%EC%9E%91%EA%B6%8C&pageIdx=3)).
That wording is not a legal opinion about every metadata transformation, but it
is enough that gate 5 must remain unresolved.

### KOBIS (film)

**Verified facts.** KOBIS is an official Korean Film Council Open API and
lists daily box office, weekly box office, movie, company, and people services
([home](https://www.kobis.or.kr/kobisopenapi/homepg/main/main.do)). The official
service directory exposes REST endpoints, including box office ([directory](https://kobis.or.kr/kobisopenapi/webservice)).

**Terms blocker.** KOBIS terms permit web-service integration/re-distribution
with independent display and attribution, but Article 6(2) requires real-time
use and prohibits copying, storing, or retransmitting results. Article 8(3)(2)
also bars use, reproduction, publication, broadcast, or provision to third
parties without prior permission ([official terms](https://kobis.or.kr/kobisopenapi/homepg/board/findProvisionInfo.do)).
It therefore cannot supply a replayable retained collection without written
permission.

### KOPIS (performing arts)

**Verified facts.** The official guide’s section 9 describes the
“예매상황판 조회 서비스” at a REST endpoint, with service-key authentication,
`stdate`/`eddate` ranges of at most 31 days, and response fields including
`basedate`, rank, performance name/period/venue/area, poster, and `mt20id`
performance ID ([KOPIS guide PDF](https://kopis.or.kr/upload/openApi/%EA%B3%B5%EC%97%B0%EC%98%88%EC%88%A0%ED%86%B5%ED%95%A9%EC%A0%84%EC%82%B0%EB%A7%9DOpenAPI%EA%B0%9C%EB%B0%9C%EA%B0%80%EC%9D%B4%EB%93%9C.pdf)).
Two calls cover 60 days; repeated date-range calls support daily collection.

**Scope and operational condition.** This is evidence for performing arts,
not general entertainment. The source already supplies a rank, so using it as
text input would change the semantics of the existing NLP ranker. The
government portal record is dataset 15097812 and currently states “이용허락범위
제한 없음” (use-permission scope: no restriction); its record also distinguishes
development and operating approval, so a key and production-stage approval
remain prerequisites ([data.go.kr record](https://www.data.go.kr/data/15097812/openapi.do)).

### Wikimedia

**Verified facts.** Wikimedia’s Analytics API is open access to pageview and
related metrics and documents top-page and time-series endpoints ([overview](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/),
[examples](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/examples/project-metrics.html)). Its Terms allow
reuse of hosted content under the applicable underlying licence, require
attribution, and incorporate API etiquette/robot policies ([Terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content),
[API terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#12._API_Terms)).

**Why it does not clear the original gate.** The daily top endpoint supports a
date and the API documents history since 2015-07-01, so a 60-day backfill and
daily increment are available ([daily endpoint](https://wikimedia.org/api/rest_v1/metrics/pageviews/top/ko.wikipedia.org/all-access/2024/01/01);
[API reference](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/)).
Analytics data is CC0 and requests require an identified User-Agent ([access
policy](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/documentation/access-policy.html)).
The remaining failure is scope: Korean Wikipedia readership is not
culture/entertainment-only and is not a Korean-geographic audience measure.

### YouTube

**Verified facts.** The API supplies stable video IDs, titles, categories, and
publication timestamps ([videos resource](https://developers.google.com/youtube/v3/docs/videos)). The API has quota limits and
documented request costs ([getting started](https://developers.google.com/youtube/v3/getting-started)).

**Policy blocker.** YouTube’s Developer Policies say not to offer
independently calculated or derived metrics that replace or provide new API
data, and restrict compiling/aggregating authorized API data except for the
content/channel owner or an authorized representative ([policies](https://developers.google.com/youtube/terms/developer-policies)).
The proposed public keyword popularity output would need a written compliance
determination or an allowed use-case review. Attribution, links/notices, quota,
privacy, and deletion/update obligations also remain part of the API Terms
([API Terms](https://developers.google.com/youtube/terms/api-services-terms-of-service)).

## Recommendation and next evidence gate

Do not promote a broad culture source yet. Preserve the SBS source-local
experiment, but request an explicit SBS data/API licence before production use.
If performing arts is an acceptable narrowed scope, obtain KOPIS production
approval; otherwise retain the conclusion
that no candidate clears the original breadth gate. KOBIS remains rejected
unless written permission overrides its retention restrictions. Wikimedia is
operationally/licensing-ready but remains a readership-scope mismatch; YouTube
remains rejected under its aggregation policy.

## Broad Korean-document follow-up — 2026-08-30

### Question and sample rule

The target is **recently increasing mentions across diverse Korean-language
web/news documents**, using title/document-frequency changes while preserving
publisher/domain. A small live sample is evidence about access and fields only;
it is not a representativeness claim. No raw copyrighted sample was written to
the repository.

| Route | Diversity / fields | 60-day bootstrap + daily | Public-use gate | Bounded live observation | Decision |
|---|---|---|---|---|---|
| GDELT DOC 2.0 / GKG | Broad monitored news; DOC ArtList exposes article URL/title, source country/language, and publication date ([official DOC description](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/amp/)); GKG codebooks document URL/date fields ([GKG codebook](https://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook.pdf)). | DOC supports precise start/end times only within the last three months and GDELT data files update at high frequency ([DOC API description](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/amp/)); 60 days is technically within range, but ArtList is capped at 250 with no documented pagination. | GDELT states unlimited academic, commercial, and governmental use and permits redistribution of GDELT datasets with citation/link ([official terms](https://gdeltproject.org/about.html)). This covers GDELT data, not an automatic licence to republish third-party article text; retain metadata/derived terms only unless publisher rights are separately established. | **Unavailable in this environment:** two bounded Korean-language DOC requests timed out before HTTP response; no count/domains/quality result is claimed. | Not a drop-in source: query-selected and capped; bulk GKG lacks titles and requires a different process. |
| BIGKinds APIs / open data | BIGKinds is a Korean news archive/corpus candidate, but API access requires registration/key according to its official service surface ([BIGKinds](https://www.bigkinds.or.kr/)); pre-filtered public datasets and broad corpus/API access must not be treated as the same licence. | Broad archive backfill and daily API behavior cannot be verified without authorized access. | Dataset-level licence/terms must be checked per BIGKinds record; “public dataset” or searchable website does not itself grant storage/processing rights for a public product. | **Unavailable:** no key or signup was bypassed; no live sample. | Do not recommend until authorized API access and the exact dataset licence are verified. |
| Common Crawl / CC-News indexes | Index records expose URL, crawl timestamp, MIME/status, digest/length, WARC location, and language when available; one bounded query over `CC-MAIN-2026-34` for `*.kr/*` returned five records, all HTTP 200, with Korean language metadata (`kor` or `kor,eng`), crawl timestamps on 2026-08-10, and one distinct domain in this tiny slice ([official index](https://index.commoncrawl.org/); [overview](https://commoncrawl.org/overview)). This was mixed web content, not a news-quality sample. | Historical crawl snapshots enable backfill, but crawl cadence is not a daily news feed and freshness varies by URL ([overview](https://commoncrawl.org/overview)). | Common Crawl grants access to its service but states crawled content may have separate owner terms and rights; crawlability is not a content licence ([Terms](https://commoncrawl.org/terms-of-use)). It fails the explicit public-product rights gate for retaining article text. | **Observed:** bounded index query returned 5 records; Korean-language metadata was present; no article bodies fetched; no syndication judgment possible from index-only rows. | Reject for this product; use only after per-publisher rights clearance or metadata-only scope is explicitly approved. |
| Fixed multi-publisher RSS route | Can provide diverse publisher/domain identities, stable feed URLs/item links, titles, and publication timestamps when each publisher supplies them. The existing SBS archive demonstrates one publisher; a multi-publisher route is an acquisition class, not one shared licence ([SBS entertainment archive](https://news.sbs.co.kr/news/newsSection.do?sectionType=14)). | Usually backfillable only to each feed’s retained history; daily increment is technically straightforward, but 60-day coverage and fields vary by publisher. | **Unresolved by design:** each publisher’s RSS/terms must explicitly permit the retained fields and public processing. One publisher’s feed cannot authorize another. | No new multi-publisher sample taken: without a fixed approved publisher list and terms review, a sample would overstate the class. | Reject as a generic route; consider a small, explicitly licensed publisher set later. |

### GDELT DOC coverage correction

**Verified API contract.** The DOC 2.0 query is a search over matching
documents, not an unseeded corpus export. The official documentation says
`QUERY` is required and supports keywords/operators; `sourcelang:korean` is a
valid query operator by itself ([DOC query operators](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/amp/)).
Article-list mode returns matching articles, with RSS/JSON formats, and
`MAXRECORDS` defaults to 75 and is capped at 250 ([DOC modes and formats](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/amp/)).
The documentation describes no pagination parameter for ArtList. Precise
`STARTDATETIME`/`ENDDATETIME` searches are limited to the preceding three
months ([DOC time window](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/amp/)).
Therefore a daily Korean request can silently truncate at 250 and cannot be
treated as an exhaustive daily corpus; query results are also query-selected,
not a neutral sample.

**Live retry.** Two smallest requests were attempted on 2026-08-30:
`https://api.gdeltproject.org/api/v2/doc/doc?query=sourcelang%3Akorean&mode=artlist&format=json&maxrecords=5&timespan=1h&sort=datedesc`
and the same shape with `sourcelang:ko`. Both failed before HTTP response with
TLS connection timeout after approximately 5 seconds (`curl` status 000), so
there are no observed result fields, counts, domains, title-quality, or
duplicate/syndication findings to report.

### GDELT bulk alternatives

GDELT’s official data page describes downloadable daily/15-minute files and
BigQuery access ([data page](https://gdeltproject.org/data.html)). The GKG
codebook states that GKG graph records are grouped “namesets,” do not receive
unique identifier numbers, and are dated by the publication date of the news
media used to construct the file; fields include themes, persons,
organizations, locations, and source URLs ([GKG codebook](https://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook.pdf)).
It does not provide article titles, and the nameset representation is not a
row-per-document title corpus. The documented GKG publication process runs
after processing the previous day’s articles ([GKG codebook](https://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook.pdf)).
The primary event stream has source URL fields but is event-oriented rather
than a general title/document stream ([data-format codebook](https://data.gdeltproject.org/documentation/GDELT-Data_Format_Codebook.pdf)).

This leaves two non-drop-in choices: (a) use DOC with a new query/coverage
process and accept the 250-result ceiling, or (b) use GKG extracted
persons/organizations/themes and change the current title-based B process.
Neither is an exhaustive, title-preserving daily supplier for the existing
process. Bulk files are technically large and frequent; the official page
describes the availability, not a small local footprint, so no storage or
runtime estimate is asserted here.

### GDELT interpretation

GDELT has an explicit broad commercial-use statement, but DOC is query-selected
and capped rather than an unseeded daily corpus. Its bulk GKG alternative lacks
article titles and would require changing the current B process to use GDELT
entities/themes. The license statement applies to GDELT datasets; it does not
grant rights in the underlying publishers’ article bodies ([GDELT terms](https://gdeltproject.org/about.html)). The v0 contract should therefore
retain only the minimum licensed metadata needed for replay (identity, title
if permitted, event time, source/domain, URL, acquisition timestamp) and emit
derived keywords, with source boundaries visible. This is a product-scope
recommendation, not a legal conclusion.

### BIGKinds, Common Crawl, and RSS warnings

BIGKinds remains blocked by authorized-access and record-level licence
verification. Common Crawl’s index is technically queryable, but its terms
explicitly warn that crawled content remains subject to originating-site terms
([Common Crawl Terms](https://commoncrawl.org/terms-of-use)); an open index is
not permission to retain article text. A fixed RSS set could be excellent for
publisher diversity, but each feed needs its own rights check, coverage test,
and duplicate/syndication policy. None of those facts should be inferred from
feed availability.

### Recommendation

Do **not** recommend GDELT as a drop-in source for the current title/document-
frequency process. It may be a separate GDELT-specific experiment using
query-selected results or extracted GKG entities/themes, but that is a process
change rather than a source-compatible next step. Do not build a collector or
commit raw content yet. BIGKinds still requires authorized access and licence
verification; Common Crawl and generic RSS remain rights-gated.
