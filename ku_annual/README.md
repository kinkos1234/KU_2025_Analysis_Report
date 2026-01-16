# K UNIVERSITY 2025 연간 전적 분석 보고서

스타크래프트 크루 케이대(K University)의 2025년 연간 전적을 분석하는 자동화 파이프라인입니다.

## 📋 프로젝트 개요

- **목적**: 2025년 전적 분석 및 2026년 방향성 제시
- **대상**: 케이대 멤버 14명
- **기간**: 2025-01-01 ~ 2025-12-31
- **분석 대상**: 스폰 + 대회 (이벤트 제외)

## 🚀 빠른 시작

### 1. 필수 요구사항

- Python 3.8 이상
- 필요한 패키지: pandas, openpyxl, matplotlib, seaborn, numpy

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 데이터 준비

- **원본 데이터 파일**: `D:/ku_annual/kuniv_2025_data.xlsx`
- 2026-01-01에 최종 데이터로 업데이트 필요

### 4. 원클릭 실행

#### Windows

```bash
run_report.bat
```

#### Python 직접 실행

```bash
python run_report.py
```

## 📂 프로젝트 구조

```
ku_annual/
├─ scripts/
│  ├─ config.py                    # 설정 파일
│  ├─ 01_validate_data.py          # 데이터 검증
│  ├─ 02_analyze_team.py           # 팀 분석
│  ├─ 03_analyze_members.py        # 멤버별 분석
│  ├─ 04_generate_charts.py        # 차트 생성
│  ├─ 05_analyze_mvp.py            # MVP 선정 분석
│  └─ 06_generate_report.py        # 보고서 생성 (Markdown)
├─ output/
│  ├─ data/                        # 분석 결과 JSON
│  ├─ charts/                      # 생성된 차트 이미지
│  └─ reports/                     # 보고서 (Markdown)
│     ├─ 01_팀분석_보고서.md
│     ├─ 02_MVP_선정.md
│     └─ booklets/                 # 개인별 Booklet
├─ run_report.py                   # 마스터 실행 스크립트
├─ run_report.bat                  # Windows 배치 파일
├─ requirements.txt                # Python 패키지 목록
└─ README.md                       # 이 파일
```

## 📊 분석 내용

### 팀 분석
- 전체 통계 (총 경기, 승률)
- 월별/분기별 추이
- 종족별 성과
- 티어별 분포
- 경기 유형별 비교 (스폰 vs 대회)
- 맵별 승률
- 종족 상성 매트릭스

### 멤버별 분석 (14명 전원)
- 개인 전체 통계
- 종족별/티어별 세부 전적
- 경기 유형별 성과
- 월별 추이
- 강점/약점 파악
- 성장 곡선

### 🏆 MVP 선정 시스템 (7가지 기준)

| 항목 | 가중치 | 설명 |
|:-----|:------:|:-----|
| 활동량 & 일관성 | 15% | 총 경기수, 활동 월수, 월별 일관성 |
| 성장률 | 20% | 시즌 초반 대비 후반 승률 개선도 |
| 동티어 경쟁력 | 15% | 같은 티어 상대 승률 및 연승 기록 |
| 상위 도전 정신 | 15% | 상위 티어 도전 빈도 및 승률 |
| 하위 방어율 | 10% | 하위 티어 상대 승률 |
| 맵 적응력 | 15% | 다양한 맵에서의 균형 잡힌 성적 |
| 대회 성과 | 10% | 공식전에서의 클러치력 |

### 시각화 차트 (10종)
1. 멤버별 전적 비교
2. 월별 전적 추이
3. 종족별 성과 비교
4. 종족 상성 히트맵
5. 티어별 분포
6. 경기 유형별 비교
7. TOP 성과자
8. **MVP 레이더 차트** (7가지 지표)
9. **MVP 종합 순위**
10. **MVP 성장률 비교**

## ⚙️ 세부 설정

### 데이터 필터링
- **이벤트 전적 제외**: 분석 대상에서 자동 제외
- **분석 대상**: 스폰 + 대회만 포함

### 티어 순서
- 1티어 (최고) → 8티어 → 베이비 (최저)

### 멤버 이름 관리
- 원본 데이터에서 자동 추출 (오타 방지)
- `output/data/member_names.json`에 저장

## 📈 출력 파일

### JSON 분석 결과
- `output/data/validation_result.json` - 데이터 검증 결과
- `output/data/team_analysis.json` - 팀 분석 결과
- `output/data/member_analysis.json` - 멤버별 분석 결과
- `output/data/mvp_analysis.json` - **MVP 선정 분석 결과**

### 보고서 (Markdown)
- `output/reports/01_팀분석_보고서.md` - 팀 전체 분석 보고서
- `output/reports/02_MVP_선정.md` - MVP 상세 선정 보고서
- `output/reports/booklets/` - 개인별 Booklet (14명)

### 차트 이미지
- `output/charts/chart_member_comparison.png`
- `output/charts/chart_monthly_trend.png`
- `output/charts/chart_race_comparison.png`
- `output/charts/chart_matchup_heatmap.png`
- `output/charts/chart_tier_distribution.png`
- `output/charts/chart_game_type_comparison.png`
- `output/charts/chart_top_performers.png`
- `output/charts/chart_mvp_radar.png` - **MVP 7가지 지표 레이더**
- `output/charts/chart_mvp_ranking.png` - **MVP 종합 순위**
- `output/charts/chart_mvp_growth.png` - **MVP 성장률 비교**

## 🔧 개별 스크립트 실행

필요 시 각 단계를 개별적으로 실행할 수 있습니다:

```bash
# 1단계: 데이터 검증
python scripts/01_validate_data.py

# 2단계: 팀 분석
python scripts/02_analyze_team.py

# 3단계: 멤버별 분석
python scripts/03_analyze_members.py

# 4단계: MVP 선정 분석
python scripts/05_analyze_mvp.py

# 5단계: 차트 생성
python scripts/04_generate_charts.py

# 6단계: 보고서 생성
python scripts/06_generate_report.py
```

## 📝 주의사항

1. **데이터 경로**: `scripts/config.py`에서 `DATA_FILE` 경로 확인
2. **이름 오타**: 모든 멤버/상대 이름은 원본에서 자동 추출되므로 수동 입력 금지
3. **이벤트 전적**: 자동으로 분석에서 제외됨
4. **최종 실행일**: 2026-01-01 최종 데이터 투입 후 실행

## 🎯 2026-01-01 실행 체크리스트

- [ ] 최종 데이터 파일 업데이트 (`kuniv_2025_data.xlsx`)
- [ ] 결측치 없는지 확인
- [ ] `run_report.bat` 또는 `run_report.py` 실행
- [ ] `output/reports/` 보고서 확인
- [ ] `output/charts/` 차트 이미지 확인
- [ ] 분석 JSON 파일 확인

## 📊 최근 분석 결과 (2025-12-31 기준)

| 항목 | 값 |
|------|-----|
| 총 경기 | 7,419경기 |
| 팀 승률 | **53.5%** |
| 대회 승률 | **56.8%** |
| 멤버 수 | 14명 |

### 🏆 2025 MVP
- 🥇 **정서린** (76.8점)
- 🥈 내가먼지 (72.2점)
- 🥉 규리야 (66.1점)

## 👤 개발자

- **분석 총괄**: AI Assistant
- **기획 총괄**: 사용자
- **보고서 작성자**: HMD

---

**Last Updated**: 2026-01-05
**Version**: 2.0
