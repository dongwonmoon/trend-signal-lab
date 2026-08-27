# Trend Detection: 초기 방법·데이터셋 조사

**조사일:** 2026-08-27 (Asia/Seoul)
**범위:** timestamped text에서 현재/신흥 keyword·name을 찾기 위한 첫 작은 실험의 Input과 Process 선택
**상태:** 연구 노트; 후속 입력 조사로 E001은 YouTube 트렌딩 데이터로 결정

## 결론 요약

**권고:** 첫 실험은 한국어 신문 말뭉치처럼 문서별 `발행 시각 + 제목/본문 + 출처`가 있는 자료를 고르고, `현재 구간 빈도/문서 비중`을 첫 ranking signal로 삼는다. 사용자는 새로 상승한 대상뿐 아니라 계속 상위에 머무는 대상을 보는 데도 가치를 느끼므로, `현재 구간 대 직전 구간의 정규화된 변화`는 별도 비교군으로 둔다. 최소 출현량과 문서 수를 함께 두어 한두 건의 희귀어가 순위를 독점하지 않게 한다. 이 구성이 현재 Output인 “순위 + 키워드·이름”과 가장 직접적으로 대응한다.

**두 번째 비교군:** temporal IDF 또는 informative log-odds를 한 가지씩 추가한다. 두 방법 모두 시간 구간 간 차이를 희귀도·배경 빈도로 보정하는 데 근거가 있지만, 첫 실험에서 동시에 여러 방법을 섞으면 어느 선택이 결과를 바꿨는지 알 수 없다.

**후순위:** Kleinberg burst는 “급격한 활동 증가”를 정식화한 강한 비교군으로 유용하지만 rate/상태 전이 파라미터와 해석을 정해야 한다. LDA/동적 topic model은 키워드 후보를 직접 순위화하기보다 주제의 묶음과 시간 변화를 보여주는 도구이므로, 현재 Output을 검증한 뒤의 확장 질문으로 둔다.

**데이터 선택 갱신:** 국립국어원 신문 말뭉치는 공식 신청·승인·이용약정이 필요해 즉시 실행하는 E001에서는 제외했다. 후속 조사에서 Kaggle `YouTube Trending Video Dataset`의 한국 파일이 행별 영상 ID·제목·카테고리·trending date를 제공하고 CC0로 표시되며 로그인 없이 내려받을 수 있음을 확인했다. E001은 이를 사용해 “이미 트렌딩에 오른 한국 콘텐츠 제목에서 납득 가능한 후보를 추출할 수 있는가”만 검증한다. 이는 일반 뉴스나 전체 대중문화에서 upstream trend를 발견하는 실험이 아니다.

## 1. 방법 비교

### 1.1 비교 전에 고정할 것

여기서 “현재”는 관측 스트림의 마지막 시간 구간이고, “신흥”은 직전 구간 또는 과거 배경 대비 사용량·비중이 증가한 후보라는 operational definition으로 둔다. 이는 문화적 중요성의 판정이 아니다. 이벤트의 중요성, 사람의 관심, 언론 노출은 별도의 검증 대상이다.

모든 방법은 같은 문서 집합, 같은 시간 절단, 같은 한국어 tokenization/정규화, 같은 최소 출현량에서 비교해야 한다. 문서 발행 시각과 수집 시각을 섞으면 미래 문서가 과거 구간으로 새어 들어가는 temporal leakage가 생긴다.

### 1.2 사실과 방법별 판단

| 방법 | 무엇을 계산하는가 | 확인된 장점 | 초기 실험에서의 판단 |
|---|---|---|---|
| 단순 frequency/rank | 현재 구간의 term count 또는 문서 수를 세고 내림차순 순위화 | 설명이 가장 쉽고, Output의 순위와 직접 대응한다. 기준선으로 실패 양상(상시 고빈도어, 매체 반복)을 관찰하기 쉽다. | **필수 baseline.** 단, 전체 건수만 쓰지 말고 구간 문서 수로 정규화하고 stopword/상시어/최소 지지도를 사전에 고정한다. |
| 현재 구간 대 직전 구간 변화 | `현재 비중 - 직전 비중`, 비율, log-ratio 등으로 증가를 계산 | “현재 많이 보이는 말”과 “최근 새로 올라온 말”을 분리한다. 새 후보를 찾는 목적에 직접적이다. | **첫 비교군으로 권고.** 지속적으로 상위인 대상을 누락할 수 있으므로 현재 빈도 순위를 대체하지 않는다. 빈도가 낮은 단어의 큰 비율을 막을 최소 count와 smoothing이 필요하다. |
| temporal TF-IDF/temporal IDF | 최근 window에서 term/document frequency를 계산해 새로운 어휘에 더 높은 IDF를 주는 방식 | Karkali et al.은 시간 문서빈도(tDF)를 이용한 novelty score를 제안하고, 실제 뉴스 스트림과 주석된 cluster에서 기존 baseline보다 precision·실행시간 개선을 보고했다. 논문은 sliding window와 decay를 사용한다. | **두 번째 비교군으로 권고.** 논문은 문서 novelty 탐지 결과이므로, term rank에 그대로 적용된다고 말할 수는 없다. term-level 적용은 이 조사에서의 추론이며 동일한 historical 사례로 검증해야 한다. |
| informative log-odds | 두 구간의 term count 차이를 background corpus의 informative Dirichlet prior로 shrink하고 z-score화 | Monroe, Colaresi, Quinn은 두 말뭉치에서 차별적으로 많이 쓰인 lexical feature를 Bayesian shrinkage/regularization으로 고르는 방법을 제시했다. 희귀 count의 폭주를 줄이는 방향이다. | **변화 ranking의 안정화 비교군.** 시점별 corpus 비교로의 적용은 자연스럽지만 원 논문의 정치적 말뭉치 설정을 한국어 trend 검증 결과로 오해하지 않는다. |
| Kleinberg burst | 스트림에서 term의 생성률이 baseline에서 burst state로 전이되는지를 infinite-state automaton으로 모델링 | 원 논문은 burst를 시간에 따른 활동량 급증으로 정의하고, 효율적인 알고리즘과 중첩·계층적 burst 구조를 제시했다. 뉴스·이메일·연구문헌 스트림에서 의미 있는 구조를 보였다. | **강한 2차 baseline.** 급등 시점을 잘 포착할 가능성이 있지만, baseline rate, 상태 수/비용, 지속시간 해석을 정해야 한다. “순위 + 이름”만 필요한 첫 실험에는 다소 무겁다. |
| LDA / dynamic topic model | 문서를 잠재 topic 혼합으로 표현하고, 동적 모델은 시간 순서에 따라 topic multinomial의 변화를 모델링 | LDA는 문서별 topic 혼합을 제공한다. Blei–Lafferty 동적 topic model은 순차 corpus에서 topic evolution을 정량·정성적으로 살핀다. 주제 묶음과 맥락 탐색에 적합하다. | **후순위.** 단일 keyword/name 후보의 현재 순위를 직접 산출하지 않고, topic 수·초기값·라벨 해석·시간 정렬에 추가 판단이 필요하다. Output을 먼저 검증한 뒤 grouping/explanation 질문에서 시험한다. |

**해석의 경계:** “검증된 방법”은 해당 논문이 자기 task/dataset에서 평가했다는 뜻이다. 특정 방법이 한국어 문화 트렌드를 잘 맞힌다는 뜻은 아니다. 실제 한국어 후보의 품질은 별도 historical evaluation이 필요하다.

### 1.3 초기 ranking의 구체적 원칙

첫 비교는 아래 두 결과를 분리해 보존하는 것이 좋다.

1. **현재성:** 현재 구간에서 문서 비중 또는 문서 수가 높은 순위.
2. **상승성:** 현재 구간이 직전 구간보다 얼마나 증가했는지의 순위.

최종 한 순위가 필요하다면 먼저 두 순위를 독립적으로 평가하고, 그 다음에야 조합 규칙을 정한다. 시작부터 임의 가중합을 만들면 “높은 빈도”와 “빠른 증가” 중 무엇이 유효했는지 알 수 없다. `document frequency`를 우선 사용하면 한 기사의 반복 문장/같은 기사의 여러 문단이 신호를 과대 계상하는 문제를 줄일 수 있다. 제목과 본문을 함께 쓸 때는 둘의 역할을 별도 기록한다.

## 2. 첫 데이터에 필요한 필드와 조건

### 2.1 최소 필드

| 필드 | 필요한 이유 | 없을 때의 문제 |
|---|---|---|
| stable `document_id` | 중복 제거, 재현 가능한 문서 단위 평가 | 같은 기사의 재수집/재게시를 새 사건으로 셀 수 있다. |
| `published_at` 또는 발행일 | 문서를 시간 구간에 배치 | 수집일만 있으면 과거 사건의 현재 유입 시점을 잘못 표현한다. 정밀도가 날짜뿐인지 시각까지인지 기록한다. |
| `collected_at`/snapshot time | source latency와 재수집 시점을 분리 | “언제 관측했는가”와 “언제 발생했는가”를 혼동한다. |
| title/headline 및 body/paragraph | keyword 후보와 문맥을 계산 | 제목만 있으면 짧은 신호에 편향되고, 본문만 있으면 boilerplate·반복 보도가 늘 수 있다. |
| publisher/source, URL 또는 원자료 식별자 | 출처 편향·재게시·근거 추적 | 한 매체의 편집 정책을 전체 사회의 추세로 오해할 수 있다. |
| language, category/topic (가능하면) | 한국어 tokenization과 범위 제한, 층화 평가 | 언어 혼입·섹션별 보도량 차이를 설명할 수 없다. |
| duplicate/repost 정보 | 동일 기사 군집화와 문서 수 보정 | 통신사 전재가 “관심 증가”처럼 보인다. |
| dataset version, coverage, license/access terms, provenance | 재현·공개·향후 source 선정 | Kaggle uploader의 설명만으로 원출처 권리를 판단하게 된다. |

국립국어원 신문 말뭉치의 편의 wrapper 예시에는 `document_id`, `title`, `author`, `publisher`, `date`, `topic`, `paragraph`가 보인다. 이 필드 예시는 wrapper 문서의 확인사항이고, 사용 권한·최신 버전·배포 조건은 반드시 국립국어원 공식 신청 화면과 이용약정이 기준이다.

### 2.2 시간·텍스트 조건

- 각 record의 event time이 최소한 일 단위로 유효하고, 시간대와 날짜 정밀도를 기록해야 한다.
- 각 비교 구간에 충분한 문서 수가 있어야 한다. 구간별 전체 document count와 source별 count를 함께 저장할 수 있어야 한다.
- collection coverage가 기간 중 급격히 바뀌지 않아야 한다. 매체 추가, 수집 누락, API ranking 변경은 실제 trend와 구분한다.
- 한국어 형태소 분석/표기 정규화(띄어쓰기, 고유명사, 한자·영문, 이형태)를 선행 결정으로 기록한다. 후보가 “키워드·이름”이므로 어근만 남기면 사람 이름과 고유명사가 망가질 수 있다.
- 제목·본문·snippet을 혼용하지 않고 어느 field를 score에 사용했는지 고정한다. Karkali et al.의 novelty 실험에서도 snippet과 full content가 서로 다른 난이도와 결과를 보였다.
- 최소 출현 문서 수, 상시 stopword, URL/기자명/매체 boilerplate 제거 규칙을 사전에 고정한다.

### 2.3 provenance/license/역사 reference 조건

**Provenance/license:** 원출처 기관, 수집 방식, 원자료의 copyright/licence, dataset version/snapshot date, 허용되는 연구·재배포 범위를 별도로 기록한다. “Kaggle 페이지가 CC BY/CC0라고 표시한다”는 재배포 권리의 충분한 증명이 아니다. 원문 제공자, aggregator/API, uploader의 권리가 서로 다를 수 있다.

**Historical event reference:** label leakage를 피하려면 관측 corpus와 별도로, 각 검증 기간에 이미 알려진 사건/인물의 기준일(anchor date), 후보 표현(동의어·표기 변형), 근거 URL, 사건의 공개 시점을 기록한다. 기준일 이후 자료로 후보명을 만들고 같은 자료로 정답을 작성하면 회고적 누출이 생긴다. 사건이 실제로 중요했는지와 단지 많이 보도되었는지는 별도 human judgment로 둔다.

NIST의 TDT 평가 개요는 topic detection, topic tracking, link detection, **first story detection**, story segmentation을 구별하고 corpus와 평가 지표를 함께 다룬다. 따라서 이 프로젝트의 “신흥”을 평가할 때도 단순 현재 빈도뿐 아니라 최초 등장/최초 상승 시점, false alarm, 놓친 사례를 정의해야 한다. Karkali et al. 역시 annotated news clusters를 ground truth로 사용했지만, 그 주석과 한국 문화 relevance는 자동으로 이전되지 않는다.

## 3. 후보 데이터셋과 접근성 점검

### 3.1 한국어·한국 뉴스에 가까운 후보

#### A. 국립국어원 모두의 말뭉치 — 신문 말뭉치 v2.0

**사실:** 국립국어원 공식 검색 화면은 신문 말뭉치 v2.0을 “종합지, 전문지, 인터넷 기반 신문 매체의 기사(2009년~2018년)”로 설명한다. 같은 화면은 말뭉치 신청 후 관리자 검토, 이용약정서 동의·서명 뒤 다운로드할 수 있고, 이용 기간은 원자료의 이용 허락 기간 이내로 제한된다고 안내한다. wrapper의 공개 예시에는 날짜, 제목, 발행인, topic, paragraph가 있다.

**판단:** 기간이 길고 한국어 뉴스 문서 단위 time/text가 있어 첫 historical trend 실험에 가장 적합한 후보다. 다만 파일을 저장소에 재배포할 수 있다고 가정하면 안 된다. 작은 sample을 commit할지 여부도 원자료 허용 범위와 개인정보/저작권 검토 뒤에 결정한다.

#### B. 국립국어원 신문 말뭉치 2020–2025 연도별 판

**사실:** 공식 화면은 2020년부터 2024년 생산 기사에 대응하는 연도별 corpus를 별도로 나열하며, 최근 판은 매체로부터 저작권 이용 허락을 받은 기사를 기계 분석 가능한 형식으로 정제한 것이라고 설명한다. 각 판도 신청·승인 절차를 따른다.

**판단:** 최신 한국어 표현에 더 가깝지만 연도별로 나뉘어 있어 작은 historical 실험의 시간 폭은 v2.0보다 짧다. v2.0으로 방법을 고정한 뒤 최신성/도메인 이동을 점검하는 후속 비교 후보로 둔다.

#### C. AI-Hub “뉴스 기사 기계독해 데이터”

**사실:** AI-Hub 페이지는 한국어 뉴스 기사 데이터, 2021년 구축, 400,056건, 출처를 한국언론진흥재단·중앙일보로 설명한다. 메타데이터 구조에는 `doc_id`, `doc_title`, `doc_source`, `doc_published`(YYYYMMDD), `created`(데이터셋 생성일시), 분류, paragraph/context가 구분되어 있다. 페이지는 내국인만 데이터 신청이 가능하다고 안내한다.

**판단:** 날짜·제목·출처·본문이 있어 schema sanity check에는 유용하지만, Q&A 학습용으로 만들어진 corpus이고 한 구축 연도 중심이다. `created`를 사건 시각으로 사용하면 안 되며 `doc_published`의 coverage와 누락을 확인해야 한다. 첫 trend benchmark의 주 데이터보다는 대체/교차 검증 후보가 안전하다.

#### D. Naver DataLab Search Trend

**사실:** 공식 API는 `startDate`, `endDate`, `timeUnit`과 keyword groups를 요청하고, 기간별 `ratio`를 반환한다. 즉 이미 알고 있는 keyword 묶음의 정규화 검색 추이를 얻는 API이지, raw text에서 후보를 발견하는 corpus가 아니다. 2026-08-27 현재 네이버 공지는 Search Trend API가 NAVER API HUB로 이관 중이며, 기존 개발자센터의 신규 신청은 2026-07-31 차단, 기존 이용은 2027-06-30까지 지원된다고 안내한다.

**판단:** historical keyword가 정해진 뒤 외부 관심 신호로 비교하는 데는 쓸 수 있다. 그러나 검색어 후보를 자동 발견하는 첫 Input으로 삼으면 사전에 넣은 keyword만 평가하게 되며, text provenance와 사건 문맥도 없다. API 이관/자격·요금 정책은 실제 사용 시 다시 확인한다.

#### E. BIG KINDS (한국언론진흥재단)

**사실:** BIG KINDS는 한국언론진흥재단의 뉴스 검색·분석 서비스로, 공식 서비스 안내는 주요 이슈·언론사별 뉴스·주요 키워드 등의 분석 화면을 제공한다고 설명한다.

**판단:** 미래 production source 후보로는 가깝지만, 웹 화면에 접근할 수 있다는 사실과 raw article corpus를 연구·재배포할 권리가 있다는 사실은 다르다. API 계약, 원문/메타데이터 제공 범위, 기간별 coverage, 중복 제거 규칙, 라이선스를 확인하기 전에는 첫 실험의 committed dataset으로 취급하지 않는다.

### 3.2 Kaggle 후보와 함정

#### KcBERT Pre-Training Corpus (Korean News Comments)

**사실:** KcBERT의 원 제작자 저장소는 온라인 뉴스에서 댓글·대댓글을 수집했으며, raw collection 기간을 2019-01-01–2020-06-15로 설명한다. 공개된 cleaned corpus는 정제된 대규모 txt이며, 저장소는 날짜별 stratified sampling을 tokenizer 학습에 사용했다고 설명한다. Kaggle dataset 페이지는 이 배포본의 license를 CC BY-SA 4.0으로 표시한다.

**함정과 판단:** 기간 범위가 있다는 것과 각 comment/document에 관측 timestamp가 있다는 것은 다르다. 정제 txt 배포본은 공개 설명상 행별 `published_at`, 원 기사 id, publisher, URL이 보장되지 않는다. 댓글은 뉴스 “본문”이 아니라 반응 텍스트이고, 반복·삭제·댓글 노출 정책의 영향을 받는다. 따라서 이 데이터는 한국어 신조어/구어체 tokenization 연구에는 흥미롭지만, 현재/신흥 keyword의 시간 ranking 첫 실험에는 **선정하지 않는다**. Kaggle의 uploader license 표시는 원 댓글·원 기사 제공자의 권리와 동일하다고 가정하지 않는다.

#### 비한국어 대조 후보: Kaggle Global News Dataset

**사실:** Kaggle 페이지는 NewsAPI에서 가져온 뉴스에 publication date/time과 source information이 있다고 설명하면서, dataset 자체 license를 CC0로 표시한다. 동시에 NewsAPI 이용약관을 확인하라는 주의도 적고 있다.

**판단:** timestamped text baseline의 형식 점검에는 후보가 될 수 있으나 한국어·한국 문화 relevance가 없다. 더 중요하게는 aggregator가 CC0라고 표시해도 NewsAPI와 원문 매체의 수집·재배포 조건이 자동으로 CC0가 되지 않는다. provenance/terms를 확인하지 않고 저장소에 원문을 넣지 않는다.

## 4. Input과 Process를 고르는 의사결정 순서

아래는 구현 계획이 아니라, 어떤 불확실성을 어떤 순서로 줄일지에 대한 결정 순서다.

1. **Output 판정 가능성 확인:** 사람에게 `순위 + 키워드·이름` 예시를 보여주고, “유용한 신흥 후보/단순 상시어/오탐”을 일관되게 구분할 수 있는지 먼저 확인한다. 이 단계가 불가능하면 알고리즘 선택을 미룬다.
2. **historical reference와 평가 단위 고정:** 기간, 기준일, known event/candidate reference, top-k와 lead-time/false-alarm 같은 평가 단위를 자료를 보기 전에 고정한다.
3. **Provenance가 분명한 Input 선택:** 문서별 발행시각·text·출처·중복·이용권한이 있는 후보만 남긴다. 한국어 첫 후보는 신청 가능한 NIKL 신문 corpus v2.0이고, Kaggle convenience보다 권리와 timestamp completeness를 우선한다.
4. **시간 slice와 text representation 고정:** 예를 들어 현재/직전 구간을 정하고 document-level count인지 token count인지, 제목/본문 중 무엇인지, 한국어 정규화 규칙과 최소 지지도를 고정한다.
5. **가장 해석 가능한 baseline 검증:** 현재 구간 frequency/rank가 historical reference를 top-k에 올리는지, 상시어·매체 편향이 어떤지 먼저 확인한다. 그다음 같은 Input에서 현재 대 직전 변화 순위를 별도 비교해 지속 인기와 신규 상승이 어떻게 달라지는지 본다.
6. **한 가지 보정 방법만 추가:** 두 단순 순위의 실패 원인에 따라 temporal IDF/log-odds 또는 Kleinberg burst 중 하나를 선택해 추가한다. 성능 향상뿐 아니라 결과의 안정성, 설명 가능성, 파라미터 민감도를 기록한다.
7. **Input 이동성 점검:** 방법을 고정한 채 다른 연도/출처/말뭉치에서 같은 평가를 반복한다. 여기서만 source coverage와 domain shift를 판단한다. Input과 Process를 동시에 바꾸지 않는다.
8. **topic/grouping 필요성 판단:** 단일 후보 순위가 충분히 검증된 뒤에도 “왜 함께 뜨는가/어떤 문화 현상인가”가 남는 경우에만 LDA 또는 dynamic topic model을 별도 질문으로 검토한다.
9. **production source 결정:** historical 재현성과 평가가 통과한 후에야 BIG KINDS, Naver DataLab, 기타 API의 지속성·비용·권리·갱신지연을 비교한다. 최신 API가 있다는 이유로 첫 검증 Input을 바꾸지 않는다.

이 순서의 핵심은 **Output → 평가 가능성 → 권리와 시간축이 검증된 Input → 단순 Process → 보정 Process → source 확장**이다. “최신 데이터가 아니어도 historical dataset으로 먼저 검증하고, 검증된 Process를 고른 뒤 sustainable source를 택한다”는 저장소의 초기 workflow와 일치한다.

## 5. 남은 불확실성 / 중단 조건

- NIKL corpus 신청 승인 여부와 실제 파일의 record-level timestamp 정밀도는 다운로드 전까지 확인되지 않았다.
- NIKL corpus가 기사 원문을 어느 범위까지 연구 결과에 포함·재배포할 수 있는지는 이용약정 원문 확인이 필요하다.
- 한국어 형태소 분석기/고유명사 정규화 선택은 이 조사 범위를 넘어가며, 임의로 특정 도구를 채택하지 않는다.
- “문화적으로 중요한 신흥어”의 gold label은 빈도만으로 만들 수 없다. 합의된 annotator 판단과 역사 reference가 없으면 알고리즘 우열 결론을 중단한다.
- Naver DataLab의 검색 ratio는 관심도 proxy이지 text prevalence나 원인 증거가 아니다.
- 상기 조건을 충족하는 작은 subset을 확보하지 못하면 구현·Notebook·Script를 시작하지 않고, 데이터 접근/권리 문제를 먼저 해결한다.

## 출처 및 접근일

### 방법론·평가 (1차 자료)

- [Kleinberg, “Bursty and Hierarchical Structure in Streams,” Cornell author PDF](https://www.cs.cornell.edu/info/people/kleinber/bhs.pdf), 2002. 접근일 2026-08-27.
- [Karkali et al., “Using temporal IDF for efficient novelty detection in text streams,” arXiv:1401.1456](https://arxiv.org/abs/1401.1456), 2014. 접근일 2026-08-27.
- [Monroe, Colaresi, Quinn, “Fightin’ words,” DOI 10.1093/pan/mpn018](https://doi.org/10.1093/pan/mpn018), *Political Analysis* 16(4), 2008. 접근일 2026-08-27.
- [Blei, Ng, Jordan, “Latent Dirichlet Allocation,” JMLR](https://www.jmlr.org/papers/v3/blei03a.html), 2003. 접근일 2026-08-27.
- [Blei and Lafferty, “Dynamic Topic Models,” ML Anthology / DOI](https://mlanthology.org/icml/2006/blei2006icml-dynamic/), 2006. 접근일 2026-08-27.
- [NIST, “Topic Detection and Tracking Evaluation Overview”](https://www.nist.gov/publications/topic-detection-and-tracking-evaluation-overview), 2002. 접근일 2026-08-27.

### 한국어 데이터·공식 플랫폼

- [국립국어원 모두의 말뭉치 공식 검색 — 신문 말뭉치](https://kli.korean.go.kr/main/requestMain.do?keyword=%EC%8B%A0%EB%AC%B8+%EB%A7%90%EB%AD%89%EC%B9%98&lang=ko&tabType=thumb), 접근일 2026-08-27.
- [Korpora의 신문 말뭉치 field 예시](https://ko-nlp.github.io/Korpora/ko-docs/corpuslist/modu_news.html), wrapper 문서, 접근일 2026-08-27.
- [AI-Hub, 뉴스 기사 기계독해 데이터](https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=577), 접근일 2026-08-27.
- [NAVER Developers, 통합 검색어 트렌드 API](https://developers.naver.com/docs/serviceapi/datalab/search/search.md), 접근일 2026-08-27.
- [NAVER Developers, Search Trend API 이관 공지](https://developers.naver.com/notice/article/32530), 접근일 2026-08-27.
- [BIG KINDS 서비스 안내](https://bigkinds.or.kr/v2/intro/service.do), 한국언론진흥재단, 접근일 2026-08-27.

### Kaggle 및 원 제작자 자료

- [Beomi/KcBERT 원 제작자 저장소](https://github.com/Beomi/KcBERT), raw collection 기간·정제·Kaggle 배포 설명, 접근일 2026-08-27.
- [KcBERT Pre-Training Corpus — Kaggle](https://www.kaggle.com/datasets/junbumlee/kcbert-pretraining-corpus-korean-news-comments), uploader license/data card, 접근일 2026-08-27.
- [Global News Dataset — Kaggle](https://www.kaggle.com/datasets/everydaycodings/global-news-dataset), NewsAPI provenance/license caveat, 접근일 2026-08-27.
