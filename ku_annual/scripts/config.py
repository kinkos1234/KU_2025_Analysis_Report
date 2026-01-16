# -*- coding: utf-8 -*-
"""
KU Annual 프로젝트 설정 파일
모든 경로, 스타일, 설정값을 중앙 관리
"""

import os
from pathlib import Path

# ==================== 경로 설정 ====================
# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
CHARTS_DIR = OUTPUT_DIR / "charts"
DATA_OUTPUT_DIR = OUTPUT_DIR / "data"
FINAL_DIR = OUTPUT_DIR / "final"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# 원본 데이터 경로
DATA_FILE = "D:/ku_annual/kuniv_2025_data.xlsx"

# ==================== 데이터 스키마 ====================
# Excel 컬럼명 (오타 방지를 위해 상수로 관리)
COL_DATE = "날짜"
COL_MEMBER_NAME = "멤버 이름"
COL_MEMBER_RACE = "멤버 종족"
COL_MEMBER_TIER = "멤버 티어"
COL_OPPONENT = "상대"
COL_OPPONENT_RACE = "상대 종족"
COL_OPPONENT_TIER = "상대 티어"
COL_MAP = "맵"
COL_RESULT = "결과"
COL_CATEGORY = "구분"
COL_TYPE = "구분2"

# 필수 컬럼 목록
REQUIRED_COLUMNS = [
    COL_DATE, COL_MEMBER_NAME, COL_MEMBER_RACE, COL_MEMBER_TIER,
    COL_OPPONENT, COL_OPPONENT_RACE, COL_OPPONENT_TIER,
    COL_MAP, COL_RESULT, COL_CATEGORY, COL_TYPE
]

# ==================== 분석 설정 ====================
# 결과 값 (대소문자 구분)
RESULT_WIN = "승"
RESULT_LOSE = "패"

# 종족
RACES = ["테란", "프로토스", "저그"]

# 경기 유형
GAME_TYPE_SPON = "스폰"
GAME_TYPE_TOURNAMENT = "대회"
GAME_TYPE_EVENT = "이벤트"

# 분석 대상 경기 유형 (이벤트 제외)
ANALYSIS_GAME_TYPES = [GAME_TYPE_SPON, GAME_TYPE_TOURNAMENT]

# 티어 순서 (상위티어 → 하위티어)
TIER_ORDER = ["1티어", "2티어", "3티어", "4티어", "5티어", "6티어", "7티어", "8티어", "베이비"]

# ==================== 시각화 스타일 ====================
# 기존 보고서 스타일 (어두운 배경, 밝은 텍스트)
CHART_STYLE = {
    "figure.facecolor": "#1a1a1a",
    "axes.facecolor": "#2a2a2a",
    "axes.edgecolor": "#ffffff",
    "axes.labelcolor": "#ffffff",
    "text.color": "#ffffff",
    "xtick.color": "#ffffff",
    "ytick.color": "#ffffff",
    "grid.color": "#404040",
    "grid.linestyle": "--",
    "grid.linewidth": 0.5,
    "font.family": "Malgun Gothic",  # 한글 폰트
    "font.size": 10,
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "figure.titlesize": 16
}

# 컬러 팔레트 (그라데이션)
COLOR_PRIMARY = "#4a9eff"      # 파란색
COLOR_SECONDARY = "#ff6b9d"    # 핑크색
COLOR_TERTIARY = "#ffd93d"     # 노란색
COLOR_SUCCESS = "#6bcf7f"      # 초록색 (승리)
COLOR_DANGER = "#ff6b6b"       # 빨간색 (패배)
COLOR_NEUTRAL = "#a0a0a0"      # 회색

# 종족별 색상
RACE_COLORS = {
    "테란": "#ff4444",         # 빨강
    "프로토스": "#4444ff",     # 파랑
    "저그": "#ff44ff"          # 보라
}

# ==================== 보고서 설정 ====================
# 보고서 제목
REPORT_TITLE = "K UNIVERSITY 2025년 전적 분석 보고서"
REPORT_PERIOD = "2025.01.01 ~ 2025.12.31"
REPORT_AUTHOR = "HMD"

# MVP 선정 기준 가중치
MVP_WEIGHTS = {
    "win_rate": 0.4,        # 승률 40%
    "game_count": 0.2,      # 경기 수 20%
    "tournament_wr": 0.3,   # 대회 승률 30%
    "growth": 0.1           # 성장률 10%
}

# ==================== 유틸리티 함수 ====================
def ensure_dirs():
    """필요한 디렉토리 생성"""
    for dir_path in [OUTPUT_DIR, CHARTS_DIR, DATA_OUTPUT_DIR, FINAL_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

def get_output_path(filename, subdir="data"):
    """출력 파일 경로 생성"""
    if subdir == "charts":
        return CHARTS_DIR / filename
    elif subdir == "final":
        return FINAL_DIR / filename
    else:
        return DATA_OUTPUT_DIR / filename

