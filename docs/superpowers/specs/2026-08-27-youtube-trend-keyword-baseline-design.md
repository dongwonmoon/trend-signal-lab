# E001 YouTube 트렌딩 제목 키워드 기준선 설계

**날짜:** 2026-08-27
**상태:** 승인됨; 구현 및 결과 판정 대기

## 한 문장 질문

이미 한국 YouTube 트렌딩 목록에 오른 콘텐츠의 제목만 보았을 때, 단순한 현재 빈도와 직전 기간 대비 변화 기준선이 사람이 알아볼 수 있는 한국 문화 키워드·이름·다단어 표현을 상위 20개로 복원하는가?

이 실험은 YouTube 바깥의 후보를 먼저 발견하는 능력, 문화 현상을 설명하는 능력, 실시간 제품 입력의 적합성을 검증하지 않는다.

## 입력

- 데이터: Kaggle `YouTube Trending Video Dataset (updated daily)`의 `KR_youtube_trending_data.csv`
- 데이터셋 버전: Kaggle API version `1346`
- 라이선스 표기: `CC0: Public Domain`
- 실제 확인 범위: 265,754행, 2020-08-12~2024-04-15, 28,251개 고유 영상
- 사용할 필드: `video_id`, `title`, `categoryId`, `trending_date`
- 사용할 카테고리: Film & Animation(1), Music(10), People & Blogs(22), Comedy(23), Entertainment(24)
- 텍스트: 제목만 사용한다. 태그와 설명은 첫 실험에서 제외한다.
- 현재 구간: 2021-09-17~2021-10-16, 양 끝 포함 30일
- 직전 구간: 2021-08-18~2021-09-16, 양 끝 포함 30일

원본 CSV와 다운로드 ZIP은 공개 저장소에 커밋하지 않는다. 재현에 필요한 dataset slug, version, file name, URL, 파일 해시는 manifest에 기록한다.

### 입력이 답할 수 있는 것과 없는 것

각 행은 원본 영상 자체가 아니라 특정 날짜의 트렌딩 목록 snapshot이다. 같은 영상이 여러 날 남으면 여러 행으로 존재한다. 이는 “새로 상승함”뿐 아니라 “계속 상단에 남음”도 재미라는 제품 가설과 맞는다.

반면 이 데이터는 YouTube가 이미 선택한 트렌딩 목록이다. 따라서 결과가 좋아도 전체 공개 텍스트에서 트렌드를 찾아냈다고 결론 내릴 수 없다. YouTube의 선정 방식, 카테고리 분류, 수집 누락이 입력 편향으로 남는다.

## 전처리와 후보 단위

1. 완전히 같은 `(video_id, trending_date)` 행만 중복 제거한다.
2. 날짜가 다른 동일 영상 행은 유지해 지속성을 보존한다.
3. 제목을 Unicode NFKC로 정규화하고 공백을 정리한다. 영문 비교는 case-insensitive로 한다.
4. Kiwi로 형태소를 분석한다. 명사·고유명사·외국어 계열 토큰을 기본 후보로 보존한다.
5. 붙어 있는 후보 토큰으로 1~3-gram을 만든다. 조사·동사·문장부호를 건너뛰어 임의로 이어 붙이지 않는다.
6. URL 조각, 한 글자 일반어, 고정 stopword는 제거한다. 고유명사로 분석된 한 글자 토큰은 제거 이유와 사례를 결과에 남긴다.
7. 같은 snapshot 제목 안에서 같은 후보가 반복되어도 한 번만 센다.
8. 더 긴 후보가 짧은 후보와 완전히 같은 snapshot 집합을 가지면 더 긴 표현을 남겨 중복 순위 점유를 줄인다.

전처리 규칙과 stopword는 결과를 본 뒤 조용히 바꾸지 않는다. 변경이 필요하면 E001의 실패 원인으로 기록하고 후속 실험에서 바꾼다.

## 비교할 Process

### A. 현재 snapshot 문서 비중

각 후보가 현재 구간의 몇 개 snapshot 제목에 나타나는지 세고, 현재 구간 전체 snapshot 수로 나눈다.

```text
current_share(term) = current_snapshot_df(term) / current_snapshot_count
```

같은 영상이 여러 날 상단에 있으면 각 날짜가 지속 인기의 한 관측치가 된다.

### B. 직전 구간 대비 smoothed log 변화

현재와 직전 구간의 snapshot 문서 비중을 0.5 pseudo-count로 완화한 뒤 log2 비율을 계산한다.

```text
change(term) = log2(
  ((current_df + 0.5) / (current_total + 1)) /
  ((previous_df + 0.5) / (previous_total + 1))
)
```

현재 구간에서 5개 snapshot 미만인 후보는 두 순위 모두에서 제외한다. A와 B는 합치지 않고 각각 top 20을 낸다. 동점은 현재 df, 더 긴 표현, 사전식 순서로 결정해 재현 가능하게 한다.

## 출력

각 기준선은 다음 열을 가진 상위 20개 표를 만든다.

- rank
- candidate
- current snapshot df 및 share
- previous snapshot df 및 share
- change score
- 서로 다른 video 수
- 대표 제목, 날짜, video id 최대 3개

사람이 원문을 모두 읽지 않아도 후보가 왜 순위에 왔는지 확인할 수 있어야 한다. 결과는 Markdown과 기계 판독 가능한 JSON으로 함께 저장한다.

## 사전 평가 계약

### 독립 역사 anchor

`오징어 게임`은 2021-09-17 공개되었고 Google Korea의 2021년 올해의 검색어 전체 3위·드라마 1위에 포함되었다. 결과를 보기 전에 다음 표기군을 하나의 anchor로 고정한다.

```text
오징어 게임, 오징어게임, squid game
```

anchor는 두 top-20 중 적어도 하나에서 사람이 읽을 수 있는 단일 또는 다단어 후보로 나타나야 한다. `게임`처럼 의미가 넓은 부분 토큰만 나온 경우는 통과가 아니다.

### 사용자와 함께 할 top-20 판정

각 결과의 후보를 다음 셋 중 하나로 분류한다.

- `specific cultural signal`: 당시의 작품·인물·그룹·밈·행사·명명된 현상을 가리킨다.
- `generic/artifact`: 영상·공식·방송·오늘처럼 어느 기간에도 흔하거나, 토큰화·업로더·플랫폼 형식 때문에 생겼다.
- `unclear`: 짧은 표만으로 판정하기 어렵다.

첫 Process 성공 조건은 다음과 같다.

1. anchor가 적어도 한 top-20에 온전한 표현으로 나타난다.
2. 적어도 한 기준선의 top-20 중 12개 이상이 `specific cultural signal`이다.
3. 같은 기준선에서 `generic/artifact`가 5개 이하이다.
4. 실행 manifest와 결과가 같은 원본 파일에서 재현된다.

기준선 선택은 specific signal 수가 더 많은 쪽을 우선하고, 같으면 artifact가 적은 쪽, 다시 같으면 설명이 단순한 A를 택한다. 이 선택은 E001에서 Process만 비교하기 위한 것이며 제품의 최종 ranking 계약이 아니다.

## 실패·중단·판단

- 입력 실패: 기간별 snapshot이 부족하거나 날짜·카테고리·중복이 설명과 다르다. Process를 고치지 않고 입력 문제를 기록한다.
- 출력 정의 실패: 사용자가 후보를 세 분류로 안정적으로 판정할 수 없다. 알고리즘 경쟁을 중단하고 출력·평가 언어를 다시 정의한다.
- 알고리즘 실패: 입력은 유효하지만 두 top-20 모두 성공 조건을 만족하지 못한다. temporal IDF, log-odds, 임베딩을 즉시 덧붙이지 않고 오탐 유형을 먼저 기록한다.
- 제품 가치 실패: 목록은 구체적이고 재현되지만 보는 재미나 유용성이 없다. 더 정교한 Process보다 제품 가설을 먼저 재검토한다.
- 권리/재현성 중단: Kaggle 버전·파일·라이선스 또는 원본 접근을 재확인할 수 없으면 원본을 저장소에 넣지 않고 실행을 중단한다.

성공해도 다음 단계가 자동 승인되지는 않는다. 이번 결과는 title-only baseline과 snapshot 입력의 가능성만 말한다.

## 근거

- [Kaggle, YouTube Trending Video Dataset](https://www.kaggle.com/datasets/rsrishav/youtube-trending-video-dataset)
- [Google Korea, 2021년 올해의 검색어](https://blog.google/intl/ko-kr/products/explore-get-answers/2021_12_2021yis/)
- [Netflix, 오징어 게임 제작 여정](https://about.netflix.com/ko/news/the-making-of-a-global-sensation-the-journey-to-creating-squid-game)
