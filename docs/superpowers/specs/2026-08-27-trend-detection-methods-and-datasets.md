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

## 6. E002 두 번째 데이터 소스 선택 전의 확립된 관행 (2026-08-28, Asia/Seoul)

### 6.1 용어와 융합 시점

문헌에서 **early fusion**은 여러 입력의 원자료 또는 낮은 수준의 특징을 하나의 특징 공간으로 합친 뒤 공동 처리하는 방식(feature-level/raw-data fusion)이고, **late fusion**은 각 입력/모달리티를 별도로 처리한 뒤 의미 공간의 판정·점수·순위에서 결합하는 방식(decision-level/score-level fusion)이다. Snoek, Worring, Smeulders의 원 논문은 이 구분을 feature space 대 semantic space로 명시한다([Snoek et al., *Early versus Late Fusion in Semantic Video Analysis*](https://doi.org/10.1145/1101149.1101236), ACM Multimedia 2005). 다중 검색 결과의 점수/증거를 결합하는 관행도 TREC-2의 Fox–Shaw 실험에서 독립 검색 결과를 합치는 **data fusion**으로 다뤄졌다([Fox and Shaw, *Combination of Multiple Searches*](https://www.govinfo.gov/content/pkg/GOVPUB-C13-6a6b0268e3a4a50f5ac0652f0b8a50b3/pdf/GOVPUB-C13-6a6b0268e3a4a50f5ac0652f0b8a50b3.pdf)). 따라서 “두 API를 호출한다”는 것만으로 early/late fusion이 되는 것은 아니며, 실제 결합 지점을 기록해야 한다.

| 선택 | 성립하려면 | 기대하는 정보/비용 | E002에서의 의미 |
|---|---|---|---|
| early/raw-data fusion | 두 소스의 기록을 같은 관측 단위·시간축·표현 공간으로 정렬하고, 누락/비동기/출처별 척도를 처리해야 한다. | 기록 사이의 상호작용을 직접 학습할 여지가 있지만, 한 소스의 형식·커버리지·결측이 공동 표현에 섞이고 source-specific 처리와 감사를 어렵게 한다. | 두 번째 소스가 E001과 동일한 의미의 기록·시간·텍스트를 제공한다는 것이 먼저 입증되기 전에는 선택하지 않는다. |
| source-local processing → late fusion/comparison | 각 소스에서 독립적으로 후보·점수·근거를 만들고, 공통 후보/시간/평가 계약에서 결과를 비교한다. | 출처별 언어·선택 편향·결측을 보존하고 어느 소스가 무엇을 기여했는지 추적하기 쉽다. 소스 사이의 상호작용은 각 로컬 출력에서 사라질 수 있고 점수 척도 비교가 필요하다. | **첫 순서로 권고.** E001의 기존 결과를 통제군으로 유지하면서 두 번째 소스의 독립 신호, 겹침, 선행/지연을 관찰할 수 있다. 새로운 결합 규칙을 발명하지 않는다. |

이 선택은 “late가 항상 우월하다”는 결론이 아니다. 원래의 비디오 실험도 late가 대부분 개념에서 약간 더 좋았지만 early가 이긴 개념에서는 차이가 더 컸다고 보고했으며([Snoek et al.](https://doi.org/10.1145/1101149.1101236)), 다중 모달 표현 학습의 원 실험은 모달리티가 학습·훈련·시험 중 언제 제공되는지를 별도 조건으로 구분했다([Ngiam et al., *Multimodal Deep Learning*](https://icml.cc/Conferences/2011/papers/399_icmlpaper.pdf), ICML 2011). 즉, 융합 성능은 과제의 정렬 수준, 소스의 가용 시점, 척도, 라벨에 의존한다.

**E001에 확인된 사실:** 현재 4,286개와 직전 4,040개의 YouTube 트렌딩 snapshot, 1,078개 고유 영상(정확한 `(video_id, trending_date)` 중복 제거)을 사용했고, 같은 입력에서 Ranking B가 Ranking A보다 시기 특이적인 목록을 만들었다. Ranking B의 사용자 질적 평가는 긍정적이었지만 세 분류 human label은 아직 없으며, 데이터 자체가 이미 YouTube가 고른 트렌딩 목록이다. **이 조사에서의 추론:** B의 apparent quality 중 얼마가 랭킹 변화 신호이고 얼마가 YouTube의 upstream selection인지 E001만으로 분리할 수 없다. 따라서 E002의 첫 질문은 “결합 점수가 좋아지는가”가 아니라 “비선정 텍스트/다른 선택 메커니즘에서도 동일한 로컬 기준선이 재현되는가”여야 한다.

### 6.2 표본 프레임과 prospective timestamped stream의 운영 관행

두 번째 소스는 이름이나 다운로드 편의보다 먼저 **sampling frame**을 명시해야 한다. 즉, 무엇이 전체 모집단인지, 어떤 지역·언어·기간·카테고리·계정/매체가 포함되는지, 표본률·endpoint 제한·누락/삭제·갱신 주기가 무엇인지, 그리고 관측 가능한 범위가 시간에 따라 바뀌었는지를 기록한다. NIST TREC 2017 Real-Time Summarization은 Twitter public stream이 약 1% sample인 “spritzer”임을 명시하고, 평가 참가자가 같은 기간에 각자 live stream을 수집하도록 했다([NIST TREC 2017 RTS overview](https://trec.nist.gov/pubs/trec26/papers/Overview-RT.pdf), §§2.1, lines 69–100). 이는 1%가 보편적으로 충분하다는 근거가 아니라, 표본률과 실시간 수집 조건을 숨은 구현 세부가 아닌 평가 입력의 일부로 선언하는 사례다.

prospective 수집에서는 최소한 다음을 raw 또는 변경 불가 manifest에 남긴다.

- source-native stable ID, 원문/제목과 언어·분류, `published_at`/event time, `collected_at`/ingestion time, timezone과 timestamp precision;
- 요청 시각, endpoint와 query/filter, 페이지 크기·page token/cursor, 응답의 next/previous token, rate/quota 오류, timeout·삭제·누락 기록;
- source/API/data-set 버전, coverage와 update schedule, 원출처·license/terms, raw response 또는 그 해시, 수집 코드의 revision;
- 동일 소스 내 exact duplicate/repost 규칙과, 소스 간에 동일 원문/항목으로 식별된 경우의 linkage 근거.

이 체크리스트의 provenance·version·coverage 원칙은 W3C Data on the Web Best Practices가 원자료의 기원과 변경, version indicator/history, coverage를 제공하라고 한 권고에 근거한다([W3C DWBP](https://www.w3.org/TR/dwbp/), Best Practices 5, 7, 8, 28). W3C PROV-DM도 데이터 산출물을 entity, 그것을 만든 activity, 관여한 agent의 관계로 표현한다([W3C PROV-DM](https://www.w3.org/TR/prov-dm/)). endpoint·cursor·오류를 manifest에 남기는 구체적 형식은 이 원칙과 source API의 pagination 계약을 E002에 적용한 프로젝트 판단이지 W3C가 지정한 schema는 아니다. 거창한 provenance graph는 만들지 않되, 최소 manifest가 출처·수집 행위·산출물의 관계를 잃지 않게 한다.

**event time과 collection time은 분리한다.** 예를 들어 YouTube 공식 문서는 `snippet.publishedAt`가 공개된 시각이며 업로드 시각과 다를 수 있다고 설명한다([YouTube video resource](https://developers.google.com/youtube/v3/docs/videos)). `search.list`의 `publishedAfter`/`publishedBefore`는 RFC 3339 필터이고, 응답의 `totalResults`는 근사치이므로 pagination은 `nextPageToken`/`prevPageToken`을 사용해야 한다([YouTube `search.list`](https://developers.google.com/youtube/v3/docs/search/list)). 따라서 E002의 historical replay는 가능한 한 source가 말하는 event/publication time으로 window를 자르고, collection time은 지연·재수집 분석에만 쓴다. source가 event time을 제공하지 않으면 “발견 시각”과 “사건 발생 시각”을 같은 것으로 부르지 않는다.

중복은 **같은 source의 같은 관측**과 **서로 다른 source의 독립 확인**을 구분한다. E001처럼 native ID와 날짜가 있는 exact duplicate만 제거하되, 다른 날짜의 동일 영상은 지속성을 보존하기 위해 남긴다. E002에서 두 소스에 같은 기사·영상이 복제되어 있으면, linkage가 확인된 기록을 독립적인 두 번의 관심으로 세지 않는다. 반대로 동일 사건을 서로 다른 원출처가 보도했다는 사실은 그 자체로 “문화적 중요성”의 gold label이 아니다.

### 6.3 cross-source trend/event 평가에서 이미 쓰이는 단위

NIST의 Topic Detection and Tracking(TDT)은 서로 다른 broadcast/news 매체의 multilingual text를 대상으로 **topic tracking, link detection, topic detection, first story detection, story segmentation**을 별도 과제로 정의한다([Fiscus and Doddington, NIST TDT evaluation overview](https://www.nist.gov/publications/topic-detection-and-tracking-evaluation-overview)). E002에서 “trend detection”을 말할 때 최소한 다음 중 무엇을 측정하는지 고정해야 한다.

| 평가 단위 | 확인할 것 | E001과의 관계 |
|---|---|---|
| record/document | 특정 시점에 후보가 맞는지, false alarm/miss가 무엇인지 | E001의 top-20 후보와 snapshot support는 이 단위의 일부 신호지만, record-level event label은 없다. |
| event/topic cluster | 여러 기록이 같은 사건·현상을 가리키는지, follow-up 중복을 어떻게 처리하는지 | `오징어 게임` anchor는 알려진 역사 사례에 대한 sanity check일 뿐 cluster gold가 아니다. |
| first appearance / lead–lag | 어느 source에서 먼저 관측되었는지, source latency가 얼마인지 | 두 번째 소스가 독립적인 조기 신호인지, 단지 YouTube 목록을 재진술하는지 판단하는 핵심이다. |
| ranked output | top-k의 specific signal, generic/artifact, coverage 및 source contribution | E001의 기존 사용자 label 계약을 유지하되, 아직 label이 없으므로 성공 선언은 보류한다. |

NIST evaluation cookbook은 과제, 핵심 metric, scoring protocol, train/development/evaluation corpus를 먼저 명시하고 metric을 과도하게 늘리지 말라고 권고한다([NIST Language Technology Evaluation Cookbook](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=150472), §§1–5). TDT 계열의 기본 관행은 detection을 miss와 false alarm의 trade-off로 보고, 한 operating point만으로 결론내리지 않는 것이다. E002에서는 새로운 정교한 detector를 도입하자는 뜻이 아니라, 적어도 고정 historical window에서 `top-k`, event/anchor coverage, first-observed source와 lead/lag, source별 false alarm/miss 사례를 같은 표에 남기자는 뜻이다.

prospective stream 평가에는 **relevance/novelty/timeliness를 분리**하는 관행도 유용하다. NIST RTS는 quality(관련성·새로움)와 latency를 별도로 측정하고, latency를 원 tweet 또는 cluster의 첫 tweet 시각 기준으로 정의한다([NIST TREC 2017 RTS overview](https://trec.nist.gov/pubs/trec26/papers/Overview-RT.pdf), §§4–5). 또 같은 cluster의 후속 기록은 먼저 본 기록과 비교해 시간적으로 비대칭인 redundancy가 될 수 있다고 명시한다. 이를 E002에 옮길 때는 그대로 점수식을 복사하지 않고, (1) 후보가 당시 질문에 맞는지, (2) 이미 관측된 같은 사건의 재게시가 아닌지, (3) 첫 관측 이후 얼마나 늦었는지를 별도 열로 둔다. 이 세 가지를 하나의 임의 가중합으로 합치지 않는다.

### 6.4 E002 source decision matrix

| 항목 | 두 번째 소스가 **반드시 보존할 것** | E002에서 **의도적으로 달라야 할 것** | 판정/중단 조건 |
|---|---|---|---|
| 질문과 output | 한국어 문화 후보라는 범위, 역사 window, 후보명/근거를 읽을 수 있는 ranked output, E001의 A/B를 재현하는 기준선 | source-native text field와 upstream selection mechanism | 같은 질문을 평가할 수 없으면 source 비교가 아니라 새 과제로 기록하고 중단한다. |
| 시간 | E001과 겹치는 historical period 또는 명시된 anchor date, source timezone/precision, event/publication time와 collection time의 분리 | source가 관측을 생성·갱신하는 방식과 latency | window별 record count와 time coverage를 설명할 수 없으면 prospective 수집 전에 중단한다. |
| 모집단/coverage | 포함 규칙, 표본률 또는 API limitation, 누락/삭제/변경 이력 | YouTube가 이미 고른 trending list가 아닌 독립적인 선택 메커니즘(그 차이를 문서화) | 두 번째 소스도 동일한 큐레이션의 재게시라면 독립 신호로 해석하지 않는다. |
| 텍스트/처리 | candidate 단위, 정규화·stopword·최소 support, source별 raw text와 전처리 version | 제목-only가 아닌 본문/게시물 등 source 고유 텍스트는 그대로 기록하되, 그 변화가 비교 가능성에 미치는 영향을 표시 | text representation을 맞출 수 없으면 “동일 알고리즘 비교”가 아니라 source-local descriptive comparison으로 제한한다. |
| ID·중복 | native stable ID, exact duplicate/repost 규칙, 동일 source의 반복 관측 보존 여부 | source-native ID 체계와 cross-source linkage 난이도 | ID 또는 중복 근거가 없으면 count/rank를 합치지 않는다. |
| provenance·권리 | 원출처, version/snapshot, license/terms, request manifest와 해시 | provider/API/수집 비용·접근 경로 | 원문 보관·재사용 권한 또는 재현 가능한 접근을 확인하지 못하면 원문을 저장소에 넣지 않는다. |
| fusion timing | E001 로컬 결과를 변경 없이 control로 보존하고 source-local 결과를 먼저 낸다 | 두 번째 소스 자체와 source별 lead/lag/overlap | 로컬 결과를 보기 전에 early 결합으로 넘어가지 않는다. 로컬 비교가 source 기여를 설명하지 못하면 fusion 결론을 내리지 않는다. |
| evaluation | 동일 anchor/reference와 human usefulness label 절차, 결과를 보기 전의 window·top-k 규칙 | 독립 source에서의 recall/overlap, first-observed source, latency 및 중복 양상 | gold label·event cluster를 만들 수 없으면 “문화적 중요도” 또는 알고리즘 우열을 선언하지 않는다. |

### 6.5 E002의 구체적 순서와 비결론

1. **Source qualification:** 후보 source의 sampling frame, timestamp semantics, stable ID, coverage, API/다운로드 조건, license/provenance를 먼저 확인한다. E001의 Kaggle archive는 version 1346, 고정 파일, SHA-256 manifest가 있는 control로 남긴다.
2. **Historical slice와 capture contract 고정:** E001과 겹치는 기간/anchor를 정하고 event/publication time, collection time, timezone, 누락·중복·page token을 기록한다. prospective API라면 작은 dry capture에서 표본/지연/삭제 양상을 확인한 뒤 평가 snapshot을 얼린다.
3. **Source-local replay:** 기존 E001 전처리와 Ranking A/B를 그대로 control로 보존하고, 두 번째 source는 가능한 범위에서 같은 후보·시간·최소 support 계약으로 별도 처리한다. source가 제목을 갖지 않으면 body/post를 제목처럼 숨겨 바꾸지 말고 차이를 명시한다.
4. **비결합 비교:** top-k overlap, source별 support, first-observed source와 lead/lag, specific/generic/artifact 및 false alarm/miss 사례를 비교한다. 이것은 새 알고리즘 제안이 아니라 source contribution을 관찰하기 위한 평가 순서다.
5. **그 이후에만 fusion 질문:** 두 로컬 결과가 서로 다른 정보와 같은 평가 단위를 충분히 보존하고, score semantics와 gold/reference를 설명할 수 있을 때에만 early/raw 결합을 별도 실험으로 검토한다. 그 전에는 late fusion도 하나의 새 ranking algorithm으로 구현하지 않고, 로컬 결과의 비교/감사 단계로 한정한다.

다음은 이 조사로 **결론내릴 수 없는 것**이다.

- Snoek의 broadcast-video 결과를 한국어 문화 trend나 YouTube/뉴스 조합에 일반화할 수 없다. “late가 관행적으로 정의되어 있다”는 것과 “이 프로젝트에서 더 정확하다”는 것은 다르다.
- TREC RTS의 Twitter 약 1% sample은 운영 사례이지 대표성 보장이나 E002의 표본률 권고가 아니다. 동일 source라도 API 정책·지역·시점에 따라 coverage가 달라질 수 있다.
- E001의 Ranking B가 더 시기 특이적으로 보였다는 관찰은 upstream YouTube selection과 Ranking B의 인과적 기여를 분리하지 못한다. human label이 없으므로 preregistered usefulness threshold도 아직 통과/실패로 선언하지 않는다.
- 두 소스의 동시 상승이나 한 소스의 선행은 문화적 중요성, 인과관계, 전체 대중의 관심을 증명하지 않는다. 검색량·게시량·플랫폼 노출은 서로 다른 proxy다.
- `published_at`/게시 시각은 사건 발생 시각과 자동으로 같지 않다. source가 사건 시각을 제공하지 않으면 “first observed”만 말한다.

2026-08-28 현재, **E001의 curated YouTube snapshot과 독립적인 timestamped text stream을 한국어 신흥 문화 keyword ranking으로 직접 비교한 1차 문헌은 찾지 못했다.** 따라서 위 권고는 (i) early/late fusion을 직접 정의·비교한 원 연구, (ii) NIST의 stream sampling·TDT/RTS 평가 관행, (iii) W3C provenance/versioning 표준, (iv) YouTube 공식 API의 실제 timestamp/pagination 제한을 E002의 좁은 질문에 매핑한 것이다. 직접 일치하는 benchmark가 없으므로 source 선택과 최종 fusion 우열은 E002의 관찰·라벨·coverage 기록이 생긴 뒤에만 판단한다.

### 6.6 2026-08-28에 확인한 1차 출처

- [Snoek, Worring, Smeulders — *Early versus Late Fusion in Semantic Video Analysis*](https://doi.org/10.1145/1101149.1101236), ACM Multimedia 2005.
- [Ngiam et al. — *Multimodal Deep Learning*](https://icml.cc/Conferences/2011/papers/399_icmlpaper.pdf), ICML 2011 공식 proceedings PDF.
- [Fox and Shaw — *Combination of Multiple Searches*](https://www.govinfo.gov/content/pkg/GOVPUB-C13-6a6b0268e3a4a50f5ac0652f0b8a50b3/pdf/GOVPUB-C13-6a6b0268e3a4a50f5ac0652f0b8a50b3.pdf), TREC-2/NIST proceedings.
- [Fiscus and Doddington — *Topic Detection and Tracking Evaluation Overview*](https://www.nist.gov/publications/topic-detection-and-tracking-evaluation-overview), NIST 2002.
- [Martin et al. — *NIST Language Technology Evaluation Cookbook*](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=150472), NIST.
- [Lin et al. — *Overview of the TREC 2017 Real-Time Summarization Track*](https://trec.nist.gov/pubs/trec26/papers/Overview-RT.pdf), NIST/TREC 2017.
- [W3C — Data on the Web Best Practices](https://www.w3.org/TR/dwbp/) 및 [W3C — PROV-DM](https://www.w3.org/TR/prov-dm/).
- [Google — YouTube Data API `search.list`](https://developers.google.com/youtube/v3/docs/search/list) 및 [video resource](https://developers.google.com/youtube/v3/docs/videos).

## 7. E002 후보 source의 실제 적합성 점검 (2026-08-28, Asia/Seoul)

### 7.1 판정 기준과 조사 결론

이 절의 **확인된 사실**은 제공기관/데이터셋 소유자가 공개한 페이지·스키마·라이선스와, 접근 가능한 파일의 헤더/일부 행을 직접 확인한 것이다. **프로젝트 추론**은 그 사실을 E001/E002 질문에 적용한 문장으로 구분한다. 2026-08-28 현재, “한국어 문화·제목의 비트렌딩 timestamped stream”과 “원문 재사용권·고정 historical window·stable ID·재현 가능한 coverage”를 동시에 만족하는 공개 후보는 찾지 못했다. 따라서 E002의 두 번째 source를 곧바로 확정하기보다, cross-source transfer와 same-platform curation ablation을 먼저 분리해 승인받아야 한다.

E001의 고정 control은 그대로 둔다. 프로젝트에서 확인한 범위는 Kaggle YouTube Trending Dataset v1346의 `KR_youtube_trending_data.csv`, 2021-08-18–2021-10-16, 8,326 snapshot rows, exact `(video_id, trending_date)` pair 기준 1,078 unique videos이다. 이것은 이미 YouTube가 trending으로 선택한 영상의 제목 stream이지, 한국 YouTube 업로드 모집단이 아니다. 아래 후보를 이 control에 붙여 합산하지 않고, 먼저 각 source-local 결과와 source 선택 규칙을 별도로 보존한다.

### 7.2 후보별 실제 selection, schema, scale, 권리

| 후보 | 정확한 selection mechanism과 time coverage | 확인된 row schema / ID / timestamp / scale | 권리·접근 및 실제 관찰 | 시험하는 불확실성 / disqualifier |
|---|---|---|---|---|
| **YouTube Trending control (E001, second source 아님)** | Kaggle archive의 한국 파일에 들어 있는 일별 trending snapshot. E001 고정 window는 2021-08-18–10-16. | `video_id`, `title`, `categoryId`, `trending_date` 등; 영상 ID와 trending 날짜를 pair로 보존. 8,326 rows, 1,078 unique videos (프로젝트 확인). | 고정 version/file/hash manifest가 있는 control. | **시험하지 않는 것:** 비선정 업로드에서의 발견과 source transfer. E002에서 다른 source처럼 재수집하거나 early 결합하면 안 된다. |
| **YouTube Data API `search.list` (same-platform sensitivity probe)** | 공식 문서는 `q`를 검색어, `regionCode`를 해당 국가에서 시청 가능한 결과, `relevanceLanguage`를 우선 관련 언어로 정의하며 다른 언어도 반환될 수 있다고 명시한다. `order=date`, RFC 3339 `publishedAfter`/`publishedBefore`, `maxResults<=50`, page token을 제공하지만, 검색어를 쓰면 keyword-selected frame이 되고 검색어를 생략해도 전체 한국 업로드 열거 계약은 문서에 없다. ([공식 `search.list` 문서](https://developers.google.com/youtube/v3/docs/search/list)) | Search response는 `items[].id.videoId`, `items[].snippet.title`, `channelId`, `publishedAt` 등을 갖는다. `publishedAt`은 공개된 시각이며 업로드 시각과 다를 수 있다. ([공식 video resource](https://developers.google.com/youtube/v3/docs/videos)) `totalResults`는 근사치(최대 1,000,000)이므로 pagination 기준으로 쓰지 않고 page token을 써야 한다. 1 page 최대 50건이다. | API key/quota와 서비스 조건 확인이 필요하다. **프로젝트 추론:** 검색어·정렬·지역/언어 관련성에 의해 다시 선택된 결과이므로 모든 한국 업로드를 열거하지 않는다. E001 영상이 다른 search contract에서 얼마나 재발견되는지 보는 selection sensitivity probe일 수는 있지만, 비트렌딩 모집단 control이나 독립 cross-source evidence로는 부적합하다. |
| **KCTI 문화예술지식 게시판 CSV** | 공공데이터포털이 제공하는 현재 snapshot 파일 `한국문화관광연구원_문화예술지식_게시판_20251218`. 기관 시스템에서 현재 제공 중인 게시글에 대한 정보라고 설명하며 업데이트는 수시(시스템 데이터)다. 시간범위는 포털에 기재되어 있지 않다. ([공식 파일·스키마 페이지](https://www.data.go.kr/data/15155439/fileData.do)) | `POST_NO`(게시글 번호), `BBS_TYPE_CD`, `POST_SUBJ`, `POST_CTN`, `LKUP_CNT`, `POST_DESC`(hashtags), `REG_DTTM`(등록일자, 최대 10자). 포털은 1,774 rows를 명시한다. 직접 CSV 다운로드의 헤더는 이 7개 필드였고, 앞부분에는 `POST_NO=212/189/167`, 제목 “2010 국민여가활동조사 …”, `REG_DTTM=2012-06-29`가 관찰됐다. | 로그인 없이 CSV 다운로드 가능하고 “이용허락범위 제한 없음”이다. 포털은 본문이 이미지/첨부만이면 공란일 수 있고 hashtags 도입 전 설명도 공란일 수 있다고 명시한다. | 기관이 제공하는 문화·정책·통계 지식 게시물의 source-local ranking이 어떤지를 시험할 수 있다. **프로젝트 추론:** 독립 대중 관측 stream 또는 사용자 관심의 proxy가 아니라 institutional editorial output에 가깝다. 고정 historical window/연속 수집 frame이 없고 본문 결측이 있어, 일반적인 cultural trend transfer의 second source로는 disqualify한다. |
| **KCTI 문화예술지식정보 metadata** | 공공데이터포털의 연 1회 snapshot `한국문화관광연구원_문화예술지식정보_20260421`; 정책 연구·시장동향·통계·학술자료 목록이다. ([공식 파일 페이지](https://www.data.go.kr/data/15016595/fileData.do?recommendDataYn=Y)) | `호`, `등록일`, `제목`, `작성자`, `소속`, `국가`, `키워드`, `분류`, `데이터기준일`; 178 rows. 제목·키워드 중심이며 public conversation body stream이 아니다. | CSV·무료·이용허락범위 제한 없음. 포털 metadata의 시간범위는 비어 있다. | rights-clear한 metadata sanity check에는 쓸 수 있으나 178행·연 snapshot·기관 목록이라는 점이 disqualifier다. |
| **KCTI 관광이슈보고서 현황** | `한국문화관광연구원_관광이슈보고서 현황_20260605`, 전문가 보고서 목록의 연 1회 snapshot. ([공식 파일 페이지](https://www.data.go.kr/data/15016606/fileData.do?recommendDataYn=Y)) | 순번, 구분, 제목, 발행일(CHAR 최대 10), 저자, 키워드, URL; 456 rows. | CSV; 공공저작물 제1유형(출처표시). 시간범위는 포털에 명시되지 않음. | 보고서의 publication index이지 timestamped article/public stream이 아니므로, source transfer용 second source로 disqualify한다. |
| **NIKL 신문 말뭉치** | 국립국어원은 2022 corpus를 “2021년 생산된 신문 기사 중 매체로부터 저작권 이용을 허락받은 기사”라고 설명하고, 2020 corpus는 2019년 기사, 구 `신문 말뭉치` v2.0은 2009–2018년 기사로 설명한다. ([공식 corpus 목록](https://kli.korean.go.kr/main/requestMain.do)) 따라서 2021 corpus는 E001 window와 달력상 겹치지만, 2021 내부의 exact publication-date coverage와 매체별 포함 규칙은 신청 전 문서로 확인해야 한다. | 공식 공개 페이지에서 이 release의 모든 row schema와 실제 row를 내려받을 수 있는 상태는 확인하지 못했다. 국립국어원은 corpus가 제목·작성자·출처 등 자료 특성을 함께 갖춘다고 설명하지만([공식 corpus 소개](https://kli.korean.go.kr/corpus/introduce/introduceList.do)), 이를 해당 newspaper release의 완전한 row schema라고 간주하지 않는다. | 신청→관리자 승인→이용약정 서명 후 다운로드 절차이며, 승인된 목적/기간 밖 이용·제3자 이전이 제한된다. 외부 공개 전 국립국어원 사전 승인이 필요하다고 FAQ가 명시한다. ([공식 FAQ](https://kli.korean.go.kr/boards/faqList.do?lang=en)) 조사 시점 사이트에는 일부 기능 장애로 신청 불가 안내도 표시됐다. | **프로젝트 추론:** broad newspaper title/body stream, source/date/provenance가 가장 잘 갖춰질 가능성이 높아 cross-source 후보 1순위다. 다만 exact schema, row count, media/category coverage, E001 기간의 실제 overlap은 승인·설명자료 확인 전 미검증이다. 접근·재배포 조건과 현재 신청 장애가 즉시 실행의 disqualifier다(권리 확인 없는 원문 저장 금지). |
| **Donga_Article Hugging Face mirror** | dataset card에 따르면 Donga 기사 crawler로 2023년 업로드 기사와 2024년 1–7월 기사를 모은 fixed mirror이며 관련기사 검색/추천 용도다. ([dataset card](https://huggingface.co/datasets/kidong98/Donga_Article), [raw README](https://huggingface.co/datasets/kidong98/Donga_Article/raw/main/README.md)) | 실제 `2023.csv` 첫 줄은 `id,title,date,content,link`; 첫 row에는 `id=117245267`, `date=20230107`, 제목·본문·Donga URL이 있었다. README는 2023 약 45,000건, 2024년 1–7월 약 30,000건이라 설명하고, `_split`은 본문을 450자 단위로 나누며 ID suffix를 추가한다고 한다. | API metadata에서 2024-09-11 수정 시각과 약 1.4GB storage는 확인했지만 dataset license field는 확인되지 않았다. viewer도 파일 간 column 불일치(cast error)를 보고한다. | 규모와 `id/title/date/content/link`는 매력적이지만 E001(2021)과 historical overlap이 없고 단일 언론사다. **Disqualifier:** 원문 기사 재사용권·dataset license 불명, 파일 variant schema drift, category/coverage 계약 부재. 원문을 저장소에 복사하거나 broad Korean culture stream으로 해석하지 않는다. |
| **Naver News chronological crawler (prospective only)** | collector repository는 날짜(`YYYY`, `YYYY-MM`, `YYYY-MM-DD`)와 category(`생활문화` 포함)를 받아 Naver News 일별 section archive의 모든 page를 순회하고, page=2000에서 파악한 마지막 page까지 기사 link를 추출한다. `DOWNSAMPLE_FACTOR`로 발견 link를 건너뛸 수도 있다. ([collector README](https://github.com/bovwes/naver-news-crawler), [collector code](https://raw.githubusercontent.com/bovwes/naver-news-crawler/main/crawler.py)) | 출력은 `timestamp,category,outlet,headline,content,url`; parser는 article `data-date-time`, outlet, headline, `dic_area` 본문을 읽는다. native article ID field는 없고 URL이 dedup key 후보다. 고정 downloadable backfill/실측 row count는 없으며, 현재 HTML·누락·재시도 정책에 따라 달라진다. | repository의 MIT는 crawler code에 대한 것이며 Naver/각 언론사의 원문 권리를 부여하지 않는다. Naver 공식 API/이용조건·robots·언론사별 재사용 권한은 이 collector에서 확인되지 않는다. | historical replay가 아닌 최소 prospective alternative다. **프로젝트 추론:** section/date/category라는 frame을 명시하면 source-local stream과 lead/lag를 시험할 수 있다. 그러나 법적/약관 확인, request failure log, stable ID와 snapshot contract를 먼저 승인하지 않으면 결과를 평가할 수 없어 disqualify한다. |
| **BIGKinds/한국언론진흥재단 파리 올림픽 metadata** | 공공데이터포털의 1회성, Paris Olympics 관련 BIGKinds-derived domestic-news subset; media FTP로 수집했다고 명시한다. ([공식 파일 페이지](https://www.data.go.kr/data/15153594/fileData.do?recommendDataYn=Y)) | 기사 주소, 보도일자, 언론사, 기고자, 제목, 통합분류, 개체명, 키워드, 특성추출값, 본문 content를 포함하며 51,521 rows. | 무료 CSV, 공공저작물 제4유형(출처표시·상업적 이용금지·변경금지); 제공 페이지는 1회성이고 본문은 publisher copyright 때문에 최대 200자, 일부 field 결측 가능하다고 기록한다. | 알려진 단일 event의 event-cluster/lead-lag sanity check에는 유용하지만, general culture stream이 아니며 E001 window와 겹치지 않는다. **Disqualifier:** event-specific one-off와 rights restriction; E002의 일반 curation ablation 후보로 순위를 올리지 않는다. |

### 7.3 same-platform probe와 cross-source transfer의 분리

`search.list`를 둘째 source 또는 비트렌딩 모집단 control이라고 부르면 질문이 섞인다. YouTube Trending과 API search는 같은 platform이지만 서로 다른 upstream selection을 거친다. `search.list`는 query가 있으면 keyword-selected 결과이고, `regionCode=KR`, `relevanceLanguage=ko`도 한국어 업로드 모집단의 census를 뜻하지 않는다. API 결과에서 E001 영상 ID가 얼마나 재발견되는지는 curation overlap/selection sensitivity이며, 독립 source가 trend를 확인했다는 증거가 아니다. 모든 요청 parameter, page token, response time, quota 오류와 빈 page를 저장해도 이 selection 한계를 제거하지는 못한다.

반대로 NIKL·Naver·Donga·BIGKinds는 news/institutional media source와 YouTube 사이의 **cross-source transfer** 후보지만, 각각 source owner의 editorial frame·coverage·rights가 다르다. 두 source 결과의 top-k overlap, first-observed source, lead/lag는 비교할 수 있지만, 서로 다른 모집단의 count를 합쳐 early/raw fusion score를 만들 근거는 아니다. KCTI는 rights-clear지만 institutional board라서 source independence보다 “기관이 정리한 지식 목록에 기존 ranking이 어떻게 보이는가”를 시험하는 별도 audit에 가깝다.

### 7.4 순위와 선택, 그리고 권고 순서

1. **NIKL은 scientific-fit 1순위지만 즉시 경로에서는 제외 상태를 유지한다.** 사용자는 이미 신청·승인 대기가 긴 입력 대신 다른 후보를 찾기로 결정했다. 그 결정을 되돌리지 않으며, 사용자가 나중에 명시적으로 재검토할 때만 exact schema, media/category coverage, publication-date precision, E001 window overlap, 원문 보관·결과 공개 조건을 확인한다.
2. **현재 즉시 실행 가능한 기존 데이터 중 E002를 깨끗하게 답하는 후보는 없다.** KCTI는 rights-clear하지만 희소한 institutional output이고, Donga는 rights/schema/period, BIGKinds Olympics는 event-selected scope 때문에 제외된다.
3. **`search.list`는 curation ablation으로 승격하지 않는다.** 별도 승인 시 E001 영상의 재발견과 query/region/language contract 민감도를 보는 작은 same-platform probe는 가능하지만, 이것으로 비트렌딩 전체 업로드와 비교했다고 결론내리지 않는다.
4. **다음 실무 경로는 prospective chronological feed의 source qualification이다.** Naver crawler repository는 가능한 field와 section/date traversal의 참고 구현일 뿐 채택된 collector가 아니다. 먼저 공식 endpoint/feed 또는 source owner의 chronology, robots/terms, metadata 보관 권리, stable ID, page completeness를 확인하고, 만족하는 source가 있을 때만 metadata-only dry capture를 별도 승인한다.
5. **Donga mirror와 Paris Olympics metadata는 현재 E002의 일반 후보에서 제외한다.** 전자는 rights/schema/period, 후자는 event-specific scope가 해결되지 않는다.

이 순위는 알고리즘 추천이 아니다. 각 source가 보존하는 selection frame과 timestamp/ID/provenance를 기준으로 한 **접근 gate 순서**다. 현재 조사에는 “E001 curated YouTube snapshot과 독립적인 한국 문화 title stream의 curation ablation”을 직접 다룬 공개 1차 benchmark가 없었다. NIKL의 승인된 실제 schema와 Naver의 합법적 prospective capture가 없으므로, 어떤 source가 더 정확하거나 문화적으로 더 중요한지 결론내릴 수 없다.

### 7.5 E002 전에 필요한 가장 작은 승인

사용자가 승인할 것은 fusion 방식이나 새 ranking algorithm이 아니라 다음 중 **한 가지 source 목적**이다.

> **A. prospective source qualification (현재 권고):** 아직 수집기를 만들지 않고, 공식 chronological feed/endpoint가 sampling frame, timestamp, stable ID, pagination coverage, metadata 이용 조건을 만족하는지 조사한다. 적합한 source가 확인된 뒤 metadata-only dry capture를 별도로 승인한다.
>
> **B. same-platform sensitivity probe:** YouTube Data API `search.list`의 query/region/language/date contract가 E001 영상 재발견에 미치는 영향을 본다. 이는 curation ablation이나 second cross-source로 해석하지 않는다.
>
> **C. NIKL 재검토:** 사용자가 승인 대기를 감수하기로 명시적으로 바꿀 때만 신청·이용약정 확인을 재개한다.

그 승인 전에는 source rows를 결합하거나 early fusion을 구현하지 않는다.
