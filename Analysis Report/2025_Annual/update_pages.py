#!/usr/bin/env python3
"""
보고서 페이지 업데이트 스크립트
- 매치업 페이지: (멤버 vs 상대) 표기 추가
- 대회 분석: 대학대전/CK 구분, 공식전 워딩
- 개인별 분석: 상대별 전적 페이지 추가, 저조 승률 원인 분석
- MVP/MIP/Ironwoman 선정 기준 변경
"""

import json
import asyncio
import pandas as pd
from pathlib import Path
from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "report_data.json"
EXCEL_PATH = BASE_DIR.parent / "ku_records.xlsx"
OUTPUT_DIR = BASE_DIR / "output"

WIDTH = 1920
HEIGHT = 1080


def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


COMMON_STYLE = '''
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    width: 1920px;
    height: 1080px;
    background: #1a1a1a;
    font-family: 'Pretendard', sans-serif;
    color: #fff;
    padding: 80px 120px;
}
.section-title { font-size: 64px; font-weight: 900; margin-bottom: 20px; }
.description { font-size: 22px; color: #aaa; margin-bottom: 10px; }
.footer {
    position: absolute;
    bottom: 60px;
    right: 120px;
    left: 120px;
    border-top: 1px solid #444;
    padding-top: 20px;
    text-align: right;
    font-size: 24px;
    color: #666;
}
.highlight { color: #4A90D9; font-weight: 700; }
'''


# ============================================================
# 1. 매치업 페이지 수정 (멤버 vs 상대 표기)
# ============================================================
def gen_02_06_matchup(data):
    """02-06. 매치업별 전적 (멤버 vs 상대 표기 추가)"""
    matchups = data['race_stats']['matchups']
    
    rows_html = ""
    for key in ['테v테', '테v저', '테v프', '저v테', '저v저', '저v프', '프v테', '프v저', '프v프']:
        stats = matchups.get(key, {})
        if not stats:
            continue
        wr = stats.get('winrate', 0)
        color = '#4A90D9' if wr >= 55 else '#e74c3c' if wr < 50 else '#fff'
        rows_html += f'''
        <tr>
            <td>{key}</td>
            <td>{stats.get('total', 0):,}</td>
            <td>{stats.get('wins', 0):,}</td>
            <td>{stats.get('losses', 0):,}</td>
            <td style="color: {color}; font-weight: 700;">{wr}%</td>
        </tr>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
table {{ width: 100%; border-collapse: collapse; margin-top: 40px; }}
th {{
    background: #2a2a2a;
    padding: 20px;
    text-align: center;
    font-size: 20px;
    border-bottom: 2px solid #4A90D9;
}}
td {{
    padding: 18px;
    text-align: center;
    font-size: 18px;
    border-bottom: 1px solid #333;
}}
tr:hover {{ background: rgba(74, 144, 217, 0.1); }}
.note {{
    margin-top: 30px;
    padding: 20px 30px;
    background: rgba(74, 144, 217, 0.1);
    border-left: 4px solid #4A90D9;
    font-size: 18px;
    color: #aaa;
}}
</style></head>
<body>
    <div class="section-title">매치업별 전적</div>
    <div class="description">테란반의 테v저, 테v프 매치업에서 높은 승률 기록</div>
    <div class="description">저그반의 저v테 매치업에서 상대적으로 고전</div>
    
    <table>
        <thead>
            <tr>
                <th>매치업</th>
                <th>경기수</th>
                <th>승</th>
                <th>패</th>
                <th>승률</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    
    <div class="note">
        ※ 매치업 표기: <strong>멤버 종족 vs 상대 종족</strong> (예: 테v저 = 테란 멤버가 저그 상대와 대전)
    </div>
    
    <div class="footer">HMD</div>
</body></html>'''


# ============================================================
# 2. 대회 분석 페이지 수정 (대학대전/CK 구분, 공식전 워딩)
# ============================================================
def get_official_match_data():
    """공식전 데이터 추출 (대학대전/CK 구분)"""
    df = pd.read_excel(EXCEL_PATH)
    df_2025 = df[(df['날짜'] >= '2025-01-01') & (df['날짜'] <= '2025-12-31')].copy()
    tour_df = df_2025[df_2025['구분2'] == '대회']
    
    # 대학대전: 대학 대전, 미니대학대전, LSSL, PL 등
    univ_keywords = ['대학', 'LSSL', 'PL']
    univ_df = tour_df[tour_df['구분'].str.contains('|'.join(univ_keywords), na=False)]
    
    # CK: CK로 표기된 경기
    ck_df = tour_df[tour_df['구분'] == 'CK']
    
    # 기타: 나머지
    other_df = tour_df[~tour_df['구분'].str.contains('|'.join(univ_keywords + ['CK']), na=False)]
    
    def calc_stats(df_subset):
        total = len(df_subset)
        wins = len(df_subset[df_subset['결과'] == '승'])
        losses = total - wins
        winrate = round(wins / total * 100, 2) if total > 0 else 0
        return {'total': total, 'wins': wins, 'losses': losses, 'winrate': winrate}
    
    # 멤버별 공식전 전적
    member_stats = {}
    for member in tour_df['멤버 이름'].unique():
        m_tour = tour_df[tour_df['멤버 이름'] == member]
        m_univ = univ_df[univ_df['멤버 이름'] == member]
        m_ck = ck_df[ck_df['멤버 이름'] == member]
        
        member_stats[member] = {
            'total': calc_stats(m_tour),
            'univ': calc_stats(m_univ),
            'ck': calc_stats(m_ck)
        }
    
    return {
        'overall': calc_stats(tour_df),
        'univ': calc_stats(univ_df),
        'ck': calc_stats(ck_df),
        'other': calc_stats(other_df),
        'member_stats': member_stats,
        'by_type': {
            '대학대전': calc_stats(univ_df),
            'CK': calc_stats(ck_df)
        }
    }


def gen_04_01_official_overview():
    """04-01. 공식전 전적 요약"""
    stats = get_official_match_data()
    overall = stats['overall']
    univ = stats['univ']
    ck = stats['ck']
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.stats-header {{
    display: flex;
    gap: 80px;
    background: rgba(255,255,255,0.03);
    border-radius: 15px;
    padding: 40px 60px;
    margin-bottom: 50px;
}}
.stat-item {{ text-align: center; }}
.stat-value {{ font-size: 64px; font-weight: 900; color: #4A90D9; }}
.stat-label {{ font-size: 18px; color: #888; margin-top: 10px; }}
.category-cards {{
    display: flex;
    gap: 40px;
    margin-top: 40px;
}}
.category-card {{
    flex: 1;
    background: rgba(255,255,255,0.03);
    border: 1px solid #333;
    border-radius: 15px;
    padding: 40px;
}}
.card-title {{ font-size: 28px; font-weight: 700; margin-bottom: 30px; color: #4A90D9; }}
.card-stat {{ display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px solid #333; }}
.card-stat:last-child {{ border-bottom: none; }}
.card-label {{ color: #888; font-size: 18px; }}
.card-value {{ font-size: 20px; font-weight: 700; }}
</style></head>
<body>
    <div class="section-title">공식전 전적 요약</div>
    <div class="description">대학대전 및 CK 리그 통합 분석</div>
    
    <div class="stats-header">
        <div class="stat-item">
            <div class="stat-value">{overall['total']}</div>
            <div class="stat-label">총 공식전 경기</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{overall['winrate']}%</div>
            <div class="stat-label">공식전 승률</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{overall['wins']}</div>
            <div class="stat-label">승리</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{overall['losses']}</div>
            <div class="stat-label">패배</div>
        </div>
    </div>
    
    <div class="category-cards">
        <div class="category-card">
            <div class="card-title">대학대전</div>
            <div class="card-stat">
                <span class="card-label">경기수</span>
                <span class="card-value">{univ['total']}전</span>
            </div>
            <div class="card-stat">
                <span class="card-label">전적</span>
                <span class="card-value">{univ['wins']}승 {univ['losses']}패</span>
            </div>
            <div class="card-stat">
                <span class="card-label">승률</span>
                <span class="card-value highlight">{univ['winrate']}%</span>
            </div>
            <div class="card-stat">
                <span class="card-label">포함 대회</span>
                <span class="card-value" style="font-size: 14px;">대학 대전, 미니대학대전, LSSL, PL</span>
            </div>
        </div>
        <div class="category-card">
            <div class="card-title">CK 리그</div>
            <div class="card-stat">
                <span class="card-label">경기수</span>
                <span class="card-value">{ck['total']}전</span>
            </div>
            <div class="card-stat">
                <span class="card-label">전적</span>
                <span class="card-value">{ck['wins']}승 {ck['losses']}패</span>
            </div>
            <div class="card-stat">
                <span class="card-label">승률</span>
                <span class="card-value highlight">{ck['winrate']}%</span>
            </div>
            <div class="card-stat">
                <span class="card-label">설명</span>
                <span class="card-value" style="font-size: 14px;">크루 간 리그전</span>
            </div>
        </div>
    </div>
    
    <div class="footer">HMD</div>
</body></html>'''


def gen_04_02_official_members():
    """04-02. 공식전 멤버별 전적"""
    stats = get_official_match_data()
    member_stats = stats['member_stats']
    
    # 전체 공식전 경기수 기준 정렬
    sorted_members = sorted(member_stats.items(), key=lambda x: x[1]['total']['total'], reverse=True)
    
    rows_html = ""
    for member, m_stats in sorted_members:
        total = m_stats['total']
        univ = m_stats['univ']
        ck = m_stats['ck']
        
        if total['total'] == 0:
            continue
        
        wr_color = '#4A90D9' if total['winrate'] >= 55 else '#e74c3c' if total['winrate'] < 50 else '#fff'
        univ_wr_color = '#4A90D9' if univ['winrate'] >= 55 else '#e74c3c' if univ['winrate'] < 50 else '#888'
        ck_wr_color = '#4A90D9' if ck['winrate'] >= 55 else '#e74c3c' if ck['winrate'] < 50 else '#888'
        
        rows_html += f'''
        <tr>
            <td>{member}</td>
            <td>{total['total']}</td>
            <td>{total['wins']}</td>
            <td>{total['losses']}</td>
            <td style="color: {wr_color}; font-weight: 700;">{total['winrate']}%</td>
            <td>{univ['total']}전 <span style="color: {univ_wr_color};">{univ['winrate']}%</span></td>
            <td>{ck['total']}전 <span style="color: {ck_wr_color};">{ck['winrate']}%</span></td>
        </tr>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
table {{ width: 100%; border-collapse: collapse; margin-top: 40px; }}
th {{
    background: #2a2a2a;
    padding: 18px;
    text-align: center;
    font-size: 18px;
    border-bottom: 2px solid #4A90D9;
}}
td {{
    padding: 16px;
    text-align: center;
    font-size: 16px;
    border-bottom: 1px solid #333;
}}
tr:hover {{ background: rgba(74, 144, 217, 0.1); }}
</style></head>
<body>
    <div class="section-title">공식전 멤버별 전적</div>
    <div class="description">대학대전 및 CK 리그 멤버별 기여도</div>
    
    <table>
        <thead>
            <tr>
                <th>멤버</th>
                <th>총 경기</th>
                <th>승</th>
                <th>패</th>
                <th>승률</th>
                <th>대학대전</th>
                <th>CK</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    
    <div class="footer">HMD</div>
</body></html>'''


# ============================================================
# 3. 개인별 분석 - 상대별 전적 페이지
# ============================================================
def get_member_opponent_data(member_name):
    """멤버별 상대 전적 데이터"""
    df = pd.read_excel(EXCEL_PATH)
    df_2025 = df[(df['날짜'] >= '2025-01-01') & (df['날짜'] <= '2025-12-31')].copy()
    m_df = df_2025[df_2025['멤버 이름'] == member_name]
    
    opponent_stats = {}
    for _, row in m_df.iterrows():
        opp = row['상대']
        opp_race = row['상대 종족']
        result = 1 if row['결과'] == '승' else 0
        
        if opp not in opponent_stats:
            opponent_stats[opp] = {'race': opp_race, 'wins': 0, 'losses': 0}
        
        if result:
            opponent_stats[opp]['wins'] += 1
        else:
            opponent_stats[opp]['losses'] += 1
    
    # 전적 계산 및 정렬
    for opp in opponent_stats:
        s = opponent_stats[opp]
        s['total'] = s['wins'] + s['losses']
        s['winrate'] = round(s['wins'] / s['total'] * 100, 2) if s['total'] > 0 else 0
    
    return opponent_stats


def gen_member_opponents(data, member_name):
    """멤버 상대별 전적 페이지"""
    opp_stats = get_member_opponent_data(member_name)
    
    # 경기수 기준 정렬
    sorted_opps = sorted(opp_stats.items(), key=lambda x: x[1]['total'], reverse=True)
    
    # 상위 12명만 표시
    top_opps = sorted_opps[:12]
    
    # 강한 상대 (승률 60% 이상, 5경기 이상)
    strong_against = [(n, s) for n, s in sorted_opps if s['winrate'] >= 60 and s['total'] >= 5][:5]
    
    # 약한 상대 (승률 40% 이하, 5경기 이상)
    weak_against = [(n, s) for n, s in sorted_opps if s['winrate'] <= 40 and s['total'] >= 5][:5]
    
    rows_html = ""
    for opp, stats in top_opps:
        wr = stats['winrate']
        color = '#4A90D9' if wr >= 55 else '#e74c3c' if wr < 50 else '#fff'
        rows_html += f'''
        <tr>
            <td>{opp}</td>
            <td>{stats['race']}</td>
            <td>{stats['total']}</td>
            <td>{stats['wins']}</td>
            <td>{stats['losses']}</td>
            <td style="color: {color}; font-weight: 700;">{wr}%</td>
        </tr>
        '''
    
    strong_html = ""
    for opp, stats in strong_against:
        strong_html += f'<div class="opp-item good">{opp} ({stats["race"]}) - {stats["total"]}전 {stats["winrate"]}%</div>'
    
    weak_html = ""
    for opp, stats in weak_against:
        weak_html += f'<div class="opp-item bad">{opp} ({stats["race"]}) - {stats["total"]}전 {stats["winrate"]}%</div>'
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.content {{ display: flex; gap: 40px; }}
.main-table {{ flex: 2; }}
.side-panel {{ flex: 1; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
th {{
    background: #2a2a2a;
    padding: 14px;
    text-align: center;
    font-size: 16px;
    border-bottom: 2px solid #4A90D9;
}}
td {{
    padding: 12px;
    text-align: center;
    font-size: 15px;
    border-bottom: 1px solid #333;
}}
tr:hover {{ background: rgba(74, 144, 217, 0.1); }}
.panel-card {{
    background: rgba(255,255,255,0.03);
    border: 1px solid #333;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
}}
.panel-title {{ font-size: 18px; font-weight: 700; margin-bottom: 15px; }}
.opp-item {{ padding: 8px 0; font-size: 14px; border-bottom: 1px solid #333; }}
.opp-item:last-child {{ border-bottom: none; }}
.opp-item.good {{ color: #4A90D9; }}
.opp-item.bad {{ color: #e74c3c; }}
</style></head>
<body>
    <div class="section-title">상대별 전적</div>
    <div class="description">주요 상대와의 대전 기록</div>
    
    <div class="content">
        <div class="main-table">
            <table>
                <thead>
                    <tr>
                        <th>상대</th>
                        <th>종족</th>
                        <th>경기수</th>
                        <th>승</th>
                        <th>패</th>
                        <th>승률</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        <div class="side-panel">
            <div class="panel-card">
                <div class="panel-title">🔥 강한 상대 (5전 이상)</div>
                {strong_html if strong_html else '<div class="opp-item">해당 없음</div>'}
            </div>
            <div class="panel-card">
                <div class="panel-title">⚠️ 약한 상대 (5전 이상)</div>
                {weak_html if weak_html else '<div class="opp-item">해당 없음</div>'}
            </div>
        </div>
    </div>
    
    <div class="footer">HMD</div>
</body></html>'''


# ============================================================
# 4. MVP/MIP/Ironwoman 선정 기준 변경
# ============================================================
def calculate_poty_scores():
    """POTY 점수 계산 (새 기준)"""
    df = pd.read_excel(EXCEL_PATH)
    df_2025 = df[(df['날짜'] >= '2025-01-01') & (df['날짜'] <= '2025-12-31')].copy()
    
    tier_order = {'1티어': 1, '2티어': 2, '3티어': 3, '4티어': 4, '5티어': 5, 
                  '6티어': 6, '7티어': 7, '8티어': 8, '베이비': 9}
    
    members = df_2025['멤버 이름'].unique()
    scores = []
    
    for member in members:
        m_df = df_2025[df_2025['멤버 이름'] == member]
        
        # 기본 통계
        total = len(m_df)
        wins = len(m_df[m_df['결과'] == '승'])
        winrate = round(wins / total * 100, 2) if total > 0 else 0
        
        # 월별 경기수 (꾸준함 측정)
        monthly_games = m_df.groupby(m_df['날짜'].dt.month).size()
        months_played = len(monthly_games)
        monthly_avg = monthly_games.mean() if len(monthly_games) > 0 else 0
        monthly_std = monthly_games.std() if len(monthly_games) > 1 else 0
        
        # 대학대전 전적
        univ_keywords = ['대학', 'LSSL', 'PL']
        tour_df = m_df[m_df['구분2'] == '대회']
        univ_df = tour_df[tour_df['구분'].str.contains('|'.join(univ_keywords), na=False)]
        univ_total = len(univ_df)
        univ_wins = len(univ_df[univ_df['결과'] == '승'])
        univ_winrate = round(univ_wins / univ_total * 100, 2) if univ_total > 0 else 0
        
        # CK 전적
        ck_df = tour_df[tour_df['구분'] == 'CK']
        ck_total = len(ck_df)
        ck_wins = len(ck_df[ck_df['결과'] == '승'])
        ck_winrate = round(ck_wins / ck_total * 100, 2) if ck_total > 0 else 0
        
        # 공식전 전체
        official_total = len(tour_df)
        official_wins = len(tour_df[tour_df['결과'] == '승'])
        official_winrate = round(official_wins / official_total * 100, 2) if official_total > 0 else 0
        
        # 상위 티어 상대 전적
        top_tier_df = m_df[m_df['상대 티어'].isin(['1티어', '2티어', '3티어', '4티어'])]
        top_tier_total = len(top_tier_df)
        top_tier_wins = len(top_tier_df[top_tier_df['결과'] == '승'])
        top_tier_winrate = round(top_tier_wins / top_tier_total * 100, 2) if top_tier_total > 0 else 0
        
        # 티어 변동
        start_tier = m_df.iloc[0]['멤버 티어']
        end_tier = m_df.iloc[-1]['멤버 티어']
        tier_growth = tier_order.get(start_tier, 9) - tier_order.get(end_tier, 9)
        
        # MVP 점수 계산 (가중치 적용)
        mvp_score = (
            winrate * 0.20 +                    # 전체 승률 20%
            official_winrate * 0.25 +           # 공식전 승률 25%
            top_tier_winrate * 0.15 +           # 상위 티어 승률 15%
            min(total / 10, 100) * 0.15 +       # 경기수 (최대 100점) 15%
            min(official_total * 2, 100) * 0.15 + # 공식전 경기수 15%
            tier_growth * 10 * 0.10             # 성장폭 10%
        )
        
        # Ironwoman 점수 (꾸준함)
        consistency_score = (
            min(total / 5, 100) * 0.40 +        # 총 경기수 40%
            min(months_played * 10, 100) * 0.30 + # 활동 월수 30%
            max(0, 100 - monthly_std * 5) * 0.30  # 편차 낮을수록 높음 30%
        )
        
        scores.append({
            'name': member,
            'total': total,
            'winrate': winrate,
            'monthly_avg': round(monthly_avg, 1),
            'monthly_std': round(monthly_std, 1),
            'months_played': months_played,
            'univ_total': univ_total,
            'univ_winrate': univ_winrate,
            'ck_total': ck_total,
            'ck_winrate': ck_winrate,
            'official_total': official_total,
            'official_winrate': official_winrate,
            'top_tier_total': top_tier_total,
            'top_tier_winrate': top_tier_winrate,
            'tier_growth': tier_growth,
            'start_tier': start_tier,
            'end_tier': end_tier,
            'mvp_score': round(mvp_score, 2),
            'consistency_score': round(consistency_score, 2)
        })
    
    return scores


def gen_07_poty_intro():
    """07. POTY 인트로"""
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
body {{ display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }}
.main-title {{ font-size: 120px; font-weight: 900; letter-spacing: -3px; margin-bottom: 30px; }}
.sub-title {{ font-size: 36px; color: #888; margin-bottom: 60px; }}
.awards {{ display: flex; gap: 60px; margin-top: 40px; }}
.award {{ text-align: center; }}
.award-icon {{ font-size: 64px; margin-bottom: 15px; }}
.award-name {{ font-size: 24px; font-weight: 700; }}
.award-desc {{ font-size: 16px; color: #888; margin-top: 8px; }}
</style></head>
<body>
    <div class="main-title">PLAYER OF THE YEAR</div>
    <div class="sub-title">2025 K UNIVERSITY 우수 학생 시상</div>
    
    <div class="awards">
        <div class="award">
            <div class="award-icon">🏆</div>
            <div class="award-name">MVP</div>
            <div class="award-desc">Most Valuable Player</div>
        </div>
        <div class="award">
            <div class="award-icon">⭐</div>
            <div class="award-name">MIP</div>
            <div class="award-desc">Most Impressive Player</div>
        </div>
        <div class="award">
            <div class="award-icon">💪</div>
            <div class="award-name">IRONWOMAN</div>
            <div class="award-desc">꾸준함의 아이콘</div>
        </div>
    </div>
    
    <div class="footer">HMD</div>
</body></html>'''


def gen_07_01_criteria():
    """07-01. 평가 기준"""
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.criteria-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; margin-top: 50px; }}
.criteria-card {{
    background: rgba(255,255,255,0.03);
    border: 1px solid #333;
    border-radius: 15px;
    padding: 35px;
}}
.card-header {{ display: flex; align-items: center; gap: 15px; margin-bottom: 25px; }}
.card-icon {{ font-size: 40px; }}
.card-title {{ font-size: 28px; font-weight: 700; }}
.criteria-item {{ padding: 12px 0; border-bottom: 1px solid #333; font-size: 16px; }}
.criteria-item:last-child {{ border-bottom: none; }}
.weight {{ color: #4A90D9; font-weight: 700; float: right; }}
</style></head>
<body>
    <div class="section-title">평가 기준</div>
    <div class="description">각 시상별 선정 기준 및 가중치</div>
    
    <div class="criteria-grid">
        <div class="criteria-card">
            <div class="card-header">
                <span class="card-icon">🏆</span>
                <span class="card-title">MVP</span>
            </div>
            <div class="criteria-item">전체 승률 <span class="weight">20%</span></div>
            <div class="criteria-item">공식전 승률 <span class="weight">25%</span></div>
            <div class="criteria-item">상위 티어 승률 <span class="weight">15%</span></div>
            <div class="criteria-item">총 경기수 <span class="weight">15%</span></div>
            <div class="criteria-item">공식전 경기수 <span class="weight">15%</span></div>
            <div class="criteria-item">티어 성장폭 <span class="weight">10%</span></div>
        </div>
        <div class="criteria-card">
            <div class="card-header">
                <span class="card-icon">⭐</span>
                <span class="card-title">MIP</span>
            </div>
            <div class="criteria-item" style="padding: 20px 0;">
                <strong>대학대전 승률 1위</strong><br><br>
                대학대전 단일 항목에서<br>
                가장 높은 승률을 기록한 멤버<br><br>
                <span style="color: #888; font-size: 14px;">
                    ※ 최소 10경기 이상 참여 필수
                </span>
            </div>
        </div>
        <div class="criteria-card">
            <div class="card-header">
                <span class="card-icon">💪</span>
                <span class="card-title">IRONWOMAN</span>
            </div>
            <div class="criteria-item">총 경기수 <span class="weight">40%</span></div>
            <div class="criteria-item">활동 월수 <span class="weight">30%</span></div>
            <div class="criteria-item">월별 편차 (낮을수록 ↑) <span class="weight">30%</span></div>
            <div class="criteria-item" style="color: #888; font-size: 14px; padding-top: 20px;">
                꾸준히 많은 경기를 치른 멤버
            </div>
        </div>
    </div>
    
    <div class="footer">HMD</div>
</body></html>'''


def gen_07_02_rankings():
    """07-02. MVP 평가표"""
    scores = calculate_poty_scores()
    sorted_scores = sorted(scores, key=lambda x: x['mvp_score'], reverse=True)
    
    rows_html = ""
    for i, s in enumerate(sorted_scores, 1):
        highlight = 'style="background: rgba(74, 144, 217, 0.2);"' if i == 1 else ''
        rows_html += f'''
        <tr {highlight}>
            <td>{i}</td>
            <td>{s['name']}</td>
            <td>{s['total']}</td>
            <td>{s['winrate']}%</td>
            <td>{s['official_total']}전 {s['official_winrate']}%</td>
            <td>{s['top_tier_total']}전 {s['top_tier_winrate']}%</td>
            <td>{s['start_tier']}→{s['end_tier']}</td>
            <td style="color: #4A90D9; font-weight: 700;">{s['mvp_score']}</td>
        </tr>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
table {{ width: 100%; border-collapse: collapse; margin-top: 40px; }}
th {{
    background: #2a2a2a;
    padding: 16px 10px;
    text-align: center;
    font-size: 15px;
    border-bottom: 2px solid #4A90D9;
}}
td {{
    padding: 14px 10px;
    text-align: center;
    font-size: 14px;
    border-bottom: 1px solid #333;
}}
tr:hover {{ background: rgba(74, 144, 217, 0.1); }}
</style></head>
<body>
    <div class="section-title">MVP 평가표</div>
    <div class="description">가중치 기반 종합 점수 산출</div>
    
    <table>
        <thead>
            <tr>
                <th>순위</th>
                <th>멤버</th>
                <th>경기수</th>
                <th>승률</th>
                <th>공식전</th>
                <th>상위티어전</th>
                <th>티어변동</th>
                <th>MVP점수</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    
    <div class="footer">HMD</div>
</body></html>'''


def gen_07_03_mvp():
    """07-03. MVP 수상자"""
    scores = calculate_poty_scores()
    mvp = max(scores, key=lambda x: x['mvp_score'])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
body {{ display: flex; flex-direction: column; justify-content: center; align-items: center; }}
.award-badge {{ font-size: 100px; margin-bottom: 20px; }}
.award-title {{ font-size: 48px; color: #4A90D9; font-weight: 700; margin-bottom: 40px; }}
.winner-name {{ font-size: 96px; font-weight: 900; margin-bottom: 30px; }}
.winner-stats {{
    display: flex;
    gap: 60px;
    background: rgba(255,255,255,0.03);
    padding: 40px 80px;
    border-radius: 20px;
    margin-top: 30px;
}}
.stat {{ text-align: center; }}
.stat-value {{ font-size: 36px; font-weight: 700; color: #4A90D9; }}
.stat-label {{ font-size: 16px; color: #888; margin-top: 8px; }}
.score {{ font-size: 28px; color: #888; margin-top: 40px; }}
</style></head>
<body>
    <div class="award-badge">🏆</div>
    <div class="award-title">MOST VALUABLE PLAYER</div>
    <div class="winner-name">{mvp['name']}</div>
    
    <div class="winner-stats">
        <div class="stat">
            <div class="stat-value">{mvp['total']}</div>
            <div class="stat-label">총 경기수</div>
        </div>
        <div class="stat">
            <div class="stat-value">{mvp['winrate']}%</div>
            <div class="stat-label">전체 승률</div>
        </div>
        <div class="stat">
            <div class="stat-value">{mvp['official_winrate']}%</div>
            <div class="stat-label">공식전 승률</div>
        </div>
        <div class="stat">
            <div class="stat-value">{mvp['top_tier_winrate']}%</div>
            <div class="stat-label">상위티어 승률</div>
        </div>
    </div>
    
    <div class="score">MVP Score: {mvp['mvp_score']}</div>
    
    <div class="footer">HMD</div>
</body></html>'''


def gen_07_04_mip():
    """07-04. MIP 수상자 (대학대전 승률 1위)"""
    scores = calculate_poty_scores()
    # 대학대전 10경기 이상 참여자 중 승률 1위
    eligible = [s for s in scores if s['univ_total'] >= 10]
    if not eligible:
        eligible = [s for s in scores if s['univ_total'] >= 5]
    
    mip = max(eligible, key=lambda x: x['univ_winrate']) if eligible else scores[0]
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
body {{ display: flex; flex-direction: column; justify-content: center; align-items: center; }}
.award-badge {{ font-size: 100px; margin-bottom: 20px; }}
.award-title {{ font-size: 48px; color: #F1C40F; font-weight: 700; margin-bottom: 40px; }}
.winner-name {{ font-size: 96px; font-weight: 900; margin-bottom: 30px; }}
.winner-stats {{
    display: flex;
    gap: 60px;
    background: rgba(255,255,255,0.03);
    padding: 40px 80px;
    border-radius: 20px;
    margin-top: 30px;
}}
.stat {{ text-align: center; }}
.stat-value {{ font-size: 36px; font-weight: 700; color: #F1C40F; }}
.stat-label {{ font-size: 16px; color: #888; margin-top: 8px; }}
.reason {{ font-size: 24px; color: #888; margin-top: 40px; text-align: center; }}
</style></head>
<body>
    <div class="award-badge">⭐</div>
    <div class="award-title">MOST IMPRESSIVE PLAYER</div>
    <div class="winner-name">{mip['name']}</div>
    
    <div class="winner-stats">
        <div class="stat">
            <div class="stat-value">{mip['univ_total']}</div>
            <div class="stat-label">대학대전 경기수</div>
        </div>
        <div class="stat">
            <div class="stat-value">{mip['univ_winrate']}%</div>
            <div class="stat-label">대학대전 승률</div>
        </div>
        <div class="stat">
            <div class="stat-value">{mip['total']}</div>
            <div class="stat-label">총 경기수</div>
        </div>
        <div class="stat">
            <div class="stat-value">{mip['winrate']}%</div>
            <div class="stat-label">전체 승률</div>
        </div>
    </div>
    
    <div class="reason">대학대전 단일 항목 승률 1위 달성</div>
    
    <div class="footer">HMD</div>
</body></html>'''


def gen_07_05_ironwoman():
    """07-05. Ironwoman 수상자"""
    scores = calculate_poty_scores()
    ironwoman = max(scores, key=lambda x: x['consistency_score'])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
body {{ display: flex; flex-direction: column; justify-content: center; align-items: center; }}
.award-badge {{ font-size: 100px; margin-bottom: 20px; }}
.award-title {{ font-size: 48px; color: #9B59B6; font-weight: 700; margin-bottom: 40px; }}
.winner-name {{ font-size: 96px; font-weight: 900; margin-bottom: 30px; }}
.winner-stats {{
    display: flex;
    gap: 60px;
    background: rgba(255,255,255,0.03);
    padding: 40px 80px;
    border-radius: 20px;
    margin-top: 30px;
}}
.stat {{ text-align: center; }}
.stat-value {{ font-size: 36px; font-weight: 700; color: #9B59B6; }}
.stat-label {{ font-size: 16px; color: #888; margin-top: 8px; }}
.reason {{ font-size: 24px; color: #888; margin-top: 40px; text-align: center; }}
</style></head>
<body>
    <div class="award-badge">💪</div>
    <div class="award-title">IRONWOMAN</div>
    <div class="winner-name">{ironwoman['name']}</div>
    
    <div class="winner-stats">
        <div class="stat">
            <div class="stat-value">{ironwoman['total']}</div>
            <div class="stat-label">총 경기수</div>
        </div>
        <div class="stat">
            <div class="stat-value">{ironwoman['months_played']}</div>
            <div class="stat-label">활동 월수</div>
        </div>
        <div class="stat">
            <div class="stat-value">{ironwoman['monthly_avg']}</div>
            <div class="stat-label">월평균 경기</div>
        </div>
        <div class="stat">
            <div class="stat-value">±{ironwoman['monthly_std']}</div>
            <div class="stat-label">월별 편차</div>
        </div>
    </div>
    
    <div class="reason">가장 꾸준히 많은 경기를 치른 멤버</div>
    
    <div class="footer">HMD</div>
</body></html>'''


# ============================================================
# 메인 실행
# ============================================================
def get_sorted_members():
    """최종 티어 및 달성일 기준으로 멤버 정렬"""
    df = pd.read_excel(EXCEL_PATH)
    df_2025 = df[(df['날짜'] >= '2025-01-01') & (df['날짜'] <= '2025-12-31')].copy()
    
    tier_order = {'1티어': 1, '2티어': 2, '3티어': 3, '4티어': 4, '5티어': 5, 
                  '6티어': 6, '7티어': 7, '8티어': 8, '베이비': 9}
    
    member_tier_info = []
    
    for member in df_2025['멤버 이름'].unique():
        m_data = df_2025[df_2025['멤버 이름'] == member].sort_values('날짜')
        final_tier = m_data.iloc[-1]['멤버 티어']
        final_tier_order = tier_order.get(final_tier, 10)
        tier_first_date = m_data[m_data['멤버 티어'] == final_tier]['날짜'].min()
        
        member_tier_info.append({
            'name': member,
            'final_tier': final_tier,
            'tier_order': final_tier_order,
            'tier_achieved_date': tier_first_date
        })
    
    return sorted(member_tier_info, key=lambda x: (x['tier_order'], x['tier_achieved_date']))


async def main():
    data = load_data()
    sorted_members = get_sorted_members()
    
    pages = []
    
    # 1. 매치업 페이지 수정
    pages.append(("02-06_matchup", gen_02_06_matchup(data)))
    
    # 2. 공식전 분석 페이지
    pages.append(("04-01_official_overview", gen_04_01_official_overview()))
    pages.append(("04-02_official_members", gen_04_02_official_members()))
    
    # 3. 개인별 상대 전적 페이지
    for idx, member_info in enumerate(sorted_members, 1):
        member_name = member_info['name']
        pages.append((f"03-{idx:02d}-5_{member_name}_opponents", gen_member_opponents(data, member_name)))
    
    # 4. POTY 페이지
    pages.append(("07_poty_intro", gen_07_poty_intro()))
    pages.append(("07-01_criteria", gen_07_01_criteria()))
    pages.append(("07-02_rankings", gen_07_02_rankings()))
    pages.append(("07-03_mvp", gen_07_03_mvp()))
    pages.append(("07-04_mip", gen_07_04_mip()))
    pages.append(("07-05_ironwoman", gen_07_05_ironwoman()))
    
    print(f"총 {len(pages)}개 페이지 생성 중...")
    
    # 기존 04-01, 04-02 삭제
    for old_file in OUTPUT_DIR.glob("04-01_tournament*.png"):
        old_file.unlink()
    for old_file in OUTPUT_DIR.glob("04-02_tournament*.png"):
        old_file.unlink()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        for name, html in pages:
            output_path = OUTPUT_DIR / f"{name}.png"
            page = await browser.new_page(viewport={'width': WIDTH, 'height': HEIGHT})
            await page.set_content(html)
            await page.screenshot(path=str(output_path), type='png')
            await page.close()
            print(f"  ✓ {name}.png")
        
        await browser.close()
    
    print("\n페이지 업데이트 완료!")
    
    # 수상자 출력
    scores = calculate_poty_scores()
    mvp = max(scores, key=lambda x: x['mvp_score'])
    eligible_mip = [s for s in scores if s['univ_total'] >= 10]
    if not eligible_mip:
        eligible_mip = [s for s in scores if s['univ_total'] >= 5]
    mip = max(eligible_mip, key=lambda x: x['univ_winrate']) if eligible_mip else scores[0]
    ironwoman = max(scores, key=lambda x: x['consistency_score'])
    
    print("\n=== 2025 POTY 수상자 ===")
    print(f"🏆 MVP: {mvp['name']} (점수: {mvp['mvp_score']})")
    print(f"⭐ MIP: {mip['name']} (대학대전 {mip['univ_total']}전 {mip['univ_winrate']}%)")
    print(f"💪 IRONWOMAN: {ironwoman['name']} ({ironwoman['total']}경기, 월평균 {ironwoman['monthly_avg']})")


if __name__ == "__main__":
    asyncio.run(main())
