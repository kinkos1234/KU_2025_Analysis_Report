#!/usr/bin/env python3
"""
K UNIVERSITY 2025 연간 보고서 전체 이미지 생성기
- 모든 섹션 페이지 생성
"""

import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# 경로 설정
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "report_data.json"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

WIDTH = 1920
HEIGHT = 1080


def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================
# 공통 스타일
# ============================================================
COMMON_STYLE = '''
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    width: 1920px;
    height: 1080px;
    background: #1a1a1a;
    font-family: 'Pretendard', sans-serif;
    color: #fff;
    padding: 80px 120px;
}
.section-label { font-size: 20px; color: #888; margin-bottom: 10px; }
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
# 02. 전체 전적 분석 섹션
# ============================================================

def gen_02_03_quarterly(data):
    """02-03. 분기별 전적 비교"""
    q = data['quarterly']
    
    bars_html = ""
    for qname in ['Q1', 'Q2', 'Q3', 'Q4']:
        stats = q[qname]
        height = stats['winrate'] * 4  # 스케일
        bars_html += f'''
        <div class="bar-group">
            <div class="bar-label">{stats['winrate']}%</div>
            <div class="bar" style="height: {height}px;">
                <div class="bar-inner"></div>
            </div>
            <div class="bar-name">{qname}</div>
            <div class="bar-detail">{stats['total']:,}전</div>
        </div>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.chart-container {{
    display: flex;
    justify-content: center;
    align-items: flex-end;
    gap: 100px;
    margin-top: 80px;
    height: 500px;
}}
.bar-group {{ text-align: center; }}
.bar {{
    width: 150px;
    background: linear-gradient(180deg, #4A90D9 0%, #2a5a8a 100%);
    border-radius: 10px 10px 0 0;
    margin: 0 auto 15px;
}}
.bar-label {{
    font-family: 'Montserrat', sans-serif;
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 15px;
}}
.bar-name {{ font-size: 28px; font-weight: 700; }}
.bar-detail {{ font-size: 18px; color: #888; margin-top: 5px; }}
</style></head>
<body>
    <div class="section-label">분기별 분석</div>
    <div class="section-title">분기별 전적 비교</div>
    <div class="description">Q3 시즌(7~9월)에 55.18%로 가장 높은 승률을 기록했습니다.</div>
    
    <div class="chart-container">{bars_html}</div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_02_04_type_detail(data):
    """02-04. 타입별 전적 상세"""
    spon = data['summary']['by_type'].get('스폰', {'total': 0, 'winrate': 0})
    tour = data['summary']['by_type'].get('대회', {'total': 0, 'winrate': 0})
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.content {{ display: flex; gap: 60px; margin-top: 60px; }}
.card {{
    flex: 1;
    background: rgba(255,255,255,0.03);
    border: 1px solid #333;
    border-radius: 15px;
    padding: 40px;
}}
.card-title {{ font-size: 24px; font-weight: 700; margin-bottom: 30px; }}
.pie-container {{ display: flex; justify-content: center; margin-bottom: 30px; }}
.pie {{
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: conic-gradient(#4A90D9 0% {spon['total']/(spon['total']+tour['total'])*100}%, #666 {spon['total']/(spon['total']+tour['total'])*100}% 100%);
    display: flex;
    align-items: center;
    justify-content: center;
}}
.pie-inner {{
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background: #1a1a1a;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    color: #aaa;
    text-align: center;
    line-height: 1.5;
}}
.bar-compare {{ display: flex; gap: 40px; justify-content: center; align-items: flex-end; }}
.compare-bar {{ text-align: center; }}
.compare-bar-inner {{
    width: 120px;
    border-radius: 8px 8px 0 0;
    margin: 0 auto 10px;
}}
.compare-value {{ font-family: 'Montserrat'; font-size: 28px; font-weight: 700; }}
.compare-label {{ font-size: 16px; color: #888; }}
</style></head>
<body>
    <div class="section-title">전체 전적 상세</div>
    <div class="description">월 평균 {spon['total']//12}회의 스폰 게임 진행</div>
    <div class="description">대회 및 CK 승률이 스폰 게임 승률보다 높은 점은 상당히 고무적</div>
    
    <div class="content">
        <div class="card">
            <div class="card-title">타입 별 경기 수 비중</div>
            <div class="pie-container">
                <div class="pie">
                    <div class="pie-inner">
                        스폰 {spon['total']:,} ({spon['total']/(spon['total']+tour['total'])*100:.1f}%)<br>
                        대회 및 CK {tour['total']:,} ({tour['total']/(spon['total']+tour['total'])*100:.1f}%)
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">타입 별 승률 비교</div>
            <div class="bar-compare">
                <div class="compare-bar">
                    <div class="compare-value">{spon['winrate']}%</div>
                    <div class="compare-bar-inner" style="height: {spon['winrate']*3}px; background: linear-gradient(180deg, #666 0%, #444 100%);"></div>
                    <div class="compare-label">스폰 승률</div>
                </div>
                <div class="compare-bar">
                    <div class="compare-value">{tour['winrate']}%</div>
                    <div class="compare-bar-inner" style="height: {tour['winrate']*3}px; background: linear-gradient(180deg, #888 0%, #555 100%);"></div>
                    <div class="compare-label">대회 및 CK 승률</div>
                </div>
            </div>
        </div>
    </div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_02_05_race(data):
    """02-05. 종족별 전적 비교"""
    race = data['race_stats']['member_race']
    
    race_data = [
        ('테란', race.get('테란', {})),
        ('저그', race.get('저그', {})),
        ('프로토스', race.get('프로토스', {}))
    ]
    
    bars_html = ""
    for name, stats in race_data:
        if not stats:
            continue
        bars_html += f'''
        <div class="race-group">
            <div class="race-bar-container">
                <div class="race-bar" style="height: {stats.get('total', 0) / 50}px;">
                    <span class="race-games">{stats.get('total', 0):,}</span>
                </div>
                <div class="race-name">{name}</div>
            </div>
            <div class="race-wr-container">
                <div class="race-wr-bar" style="height: {stats.get('winrate', 0) * 3}px;">
                    <span class="race-wr">{stats.get('winrate', 0)}%</span>
                </div>
                <div class="race-name">{name}</div>
            </div>
        </div>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.content {{ display: flex; gap: 60px; margin-top: 60px; }}
.card {{
    flex: 1;
    background: rgba(255,255,255,0.03);
    border: 1px solid #333;
    border-radius: 15px;
    padding: 40px;
}}
.card-title {{ font-size: 24px; font-weight: 700; margin-bottom: 40px; }}
.bars {{ display: flex; justify-content: center; align-items: flex-end; gap: 40px; height: 350px; }}
.bar-item {{ text-align: center; }}
.bar-inner {{
    width: 100px;
    border-radius: 8px 8px 0 0;
    margin-bottom: 15px;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 15px;
    font-family: 'Montserrat';
    font-weight: 700;
}}
.bar-name {{ font-size: 18px; color: #888; }}
</style></head>
<body>
    <div class="section-title">종족별 전적 비교</div>
    <div class="description">1인 평균 월 경기수, 승률 모두 가장 우수한 테란반</div>
    <div class="description">반면 전반적으로 다소 저조한 성적의 저그반</div>
    
    <div class="content">
        <div class="card">
            <div class="card-title">종족별 1인 평균 경기 수</div>
            <div class="bars">
                <div class="bar-item">
                    <div class="bar-inner" style="height: {race.get('테란', {}).get('total', 0) / 10}px; background: linear-gradient(180deg, #888 0%, #555 100%); font-size: 24px;">
                        {race.get('테란', {}).get('total', 0) // 3}
                    </div>
                    <div class="bar-name">테란</div>
                </div>
                <div class="bar-item">
                    <div class="bar-inner" style="height: {race.get('저그', {}).get('total', 0) / 20}px; background: linear-gradient(180deg, #777 0%, #444 100%); font-size: 24px;">
                        {race.get('저그', {}).get('total', 0) // 6}
                    </div>
                    <div class="bar-name">저그</div>
                </div>
                <div class="bar-item">
                    <div class="bar-inner" style="height: {race.get('프로토스', {}).get('total', 0) / 15}px; background: linear-gradient(180deg, #666 0%, #333 100%); font-size: 24px;">
                        {race.get('프로토스', {}).get('total', 0) // 6}
                    </div>
                    <div class="bar-name">프로토스</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">종족별 승률 비교</div>
            <div class="bars">
                <div class="bar-item">
                    <div class="bar-inner" style="height: {race.get('테란', {}).get('winrate', 0) * 4}px; background: linear-gradient(180deg, #888 0%, #555 100%); font-size: 24px;">
                        {race.get('테란', {}).get('winrate', 0)}%
                    </div>
                    <div class="bar-name">테란</div>
                </div>
                <div class="bar-item">
                    <div class="bar-inner" style="height: {race.get('저그', {}).get('winrate', 0) * 4}px; background: linear-gradient(180deg, #777 0%, #444 100%); font-size: 24px;">
                        {race.get('저그', {}).get('winrate', 0)}%
                    </div>
                    <div class="bar-name">저그</div>
                </div>
                <div class="bar-item">
                    <div class="bar-inner" style="height: {race.get('프로토스', {}).get('winrate', 0) * 4}px; background: linear-gradient(180deg, #666 0%, #333 100%); font-size: 24px;">
                        {race.get('프로토스', {}).get('winrate', 0)}%
                    </div>
                    <div class="bar-name">프로토스</div>
                </div>
            </div>
        </div>
    </div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_02_06_matchup(data):
    """02-06. 매치업별 전적"""
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
table {{ width: 100%; border-collapse: collapse; margin-top: 60px; }}
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
    <div class="footer">HMD</div>
</body></html>'''


# ============================================================
# 03. 멤버별 상세 분석
# ============================================================

def gen_member_monthly(data, member_name):
    """멤버 월별 전적 추이"""
    member = data['member_details'][member_name]
    monthly = member['monthly']
    
    if not monthly:
        return None
    
    max_games = max((m.get('total', 0) for m in monthly.values()), default=1)
    
    bars_html = ""
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    
    for i in range(1, 13):
        stats = monthly.get(i, monthly.get(str(i), {}))
        if not stats:
            bars_html += f'<div class="month-bar"><div class="bar-empty"></div><div class="month-name">{months[i-1]}</div></div>'
            continue
        
        height = (stats.get('total', 0) / max_games) * 250 if max_games > 0 else 0
        bars_html += f'''
        <div class="month-bar">
            <div class="wr-point" style="bottom: {stats.get('winrate', 0) * 2.5}px;">{stats.get('winrate', 0)}%</div>
            <div class="bar" style="height: {height}px;">
                <span class="bar-value">{stats.get('total', 0)}</span>
            </div>
            <div class="month-name">{months[i-1]}</div>
        </div>
        '''
    
    avg_games = sum(m.get('total', 0) for m in monthly.values()) / len(monthly) if monthly else 0
    avg_wr = sum(m.get('winrate', 0) for m in monthly.values()) / len(monthly) if monthly else 0
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.chart {{ display: flex; justify-content: space-around; align-items: flex-end; height: 400px; margin-top: 60px; position: relative; }}
.month-bar {{ text-align: center; position: relative; }}
.bar {{
    width: 80px;
    background: linear-gradient(180deg, #555 0%, #333 100%);
    border-radius: 6px 6px 0 0;
    margin: 0 auto 10px;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 10px;
}}
.bar-empty {{ width: 80px; height: 10px; background: #333; margin: 0 auto 10px; }}
.bar-value {{ font-size: 14px; font-weight: 700; }}
.month-name {{ font-size: 14px; color: #888; }}
.wr-point {{
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    background: #4A90D9;
    color: #fff;
    padding: 4px 8px;
    border-radius: 10px;
    font-size: 12px;
    white-space: nowrap;
}}
</style></head>
<body>
    <div class="section-title">월별 전적 추이</div>
    <div class="description">월 평균 {avg_games:.1f}회 게임 진행</div>
    <div class="description">승률 평균 {avg_wr:.2f}%</div>
    
    <div class="chart">{bars_html}</div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_member_vs_race(data, member_name):
    """멤버 상대 종족별 전적"""
    member = data['member_details'][member_name]
    vs_race = member['vs_race']
    top_opps = member['top_opponents'][:10]
    
    race_bars = ""
    for race in ['테란', '저그', '프로토스']:
        stats = vs_race.get(race, {})
        if not stats:
            continue
        race_bars += f'''
        <div class="race-bar">
            <div class="race-info">
                <span class="race-games">{stats.get('total', 0)}</span>
                <span class="race-name">{race}</span>
            </div>
            <div class="race-wr">{stats.get('winrate', 0)}%</div>
        </div>
        '''
    
    opp_rows = ""
    for opp in top_opps[:6]:
        wr = opp.get('winrate', 0)
        color = '#4A90D9' if wr >= 55 else '#e74c3c' if wr < 50 else '#fff'
        opp_rows += f'''
        <div class="opp-row">
            <span class="opp-name">{opp.get('name', '')} ({opp.get('race', '')})</span>
            <span class="opp-games">{opp.get('total', 0)}전</span>
            <span class="opp-wr" style="color: {color};">{wr}%</span>
        </div>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.content {{ display: flex; gap: 60px; margin-top: 60px; }}
.card {{
    flex: 1;
    background: rgba(255,255,255,0.03);
    border: 1px solid #333;
    border-radius: 15px;
    padding: 40px;
}}
.card-title {{ font-size: 24px; font-weight: 700; margin-bottom: 30px; }}
.race-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #333;
}}
.race-info {{ display: flex; align-items: center; gap: 20px; }}
.race-games {{ font-size: 32px; font-weight: 700; }}
.race-name {{ font-size: 18px; color: #888; }}
.race-wr {{ font-size: 28px; font-weight: 700; color: #4A90D9; }}
.opp-row {{
    display: flex;
    justify-content: space-between;
    padding: 15px 0;
    border-bottom: 1px solid #333;
    font-size: 18px;
}}
.opp-name {{ flex: 2; }}
.opp-games {{ flex: 1; text-align: center; color: #888; }}
.opp-wr {{ flex: 1; text-align: right; font-weight: 700; }}
</style></head>
<body>
    <div class="section-title">상대 종족별 비교</div>
    
    <div class="content">
        <div class="card">
            <div class="card-title">종족별 전적 비교</div>
            {race_bars}
        </div>
        
        <div class="card">
            <div class="card-title">주요 상대별 전적</div>
            {opp_rows}
        </div>
    </div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_member_by_map(data, member_name):
    """멤버 맵별 전적"""
    member = data['member_details'][member_name]
    by_map = member['by_map']
    
    if not by_map:
        return None
    
    bars_html = ""
    for map_name, stats in list(by_map.items())[:6]:
        wr = stats.get('winrate', 0)
        bars_html += f'''
        <div class="map-bar">
            <div class="map-name">{map_name}</div>
            <div class="map-stats">
                <span class="map-games">{stats.get('total', 0)}전</span>
                <span class="map-wr">{wr}%</span>
            </div>
            <div class="map-bar-bg">
                <div class="map-bar-fill" style="width: {wr}%;"></div>
            </div>
        </div>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.map-list {{ margin-top: 60px; }}
.map-bar {{
    display: flex;
    align-items: center;
    gap: 30px;
    padding: 25px 0;
    border-bottom: 1px solid #333;
}}
.map-name {{ width: 150px; font-size: 22px; font-weight: 600; }}
.map-stats {{ width: 150px; text-align: right; }}
.map-games {{ font-size: 18px; color: #888; margin-right: 20px; }}
.map-wr {{ font-size: 22px; font-weight: 700; color: #4A90D9; }}
.map-bar-bg {{
    flex: 1;
    height: 20px;
    background: #333;
    border-radius: 10px;
    overflow: hidden;
}}
.map-bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, #4A90D9 0%, #2a5a8a 100%);
    border-radius: 10px;
}}
</style></head>
<body>
    <div class="section-title">주요 맵별 비교</div>
    
    <div class="map-list">{bars_html}</div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_member_vs_tier(data, member_name):
    """멤버 상대 티어별 전적"""
    member = data['member_details'][member_name]
    vs_tier = member['vs_tier']
    member_tier = member['tier_end']
    
    tier_order = ['1티어', '2티어', '3티어', '4티어', '5티어', '6티어', '7티어', '8티어', '베이비']
    
    # 상위/동일/하위 분류
    tier_idx = tier_order.index(member_tier) if member_tier in tier_order else 5
    
    upper_total, upper_wins = 0, 0
    same_total, same_wins = 0, 0
    lower_total, lower_wins = 0, 0
    
    for i, tier in enumerate(tier_order):
        stats = vs_tier.get(tier, {})
        if not stats:
            continue
        if i < tier_idx:
            upper_total += stats.get('total', 0)
            upper_wins += stats.get('wins', 0)
        elif i == tier_idx:
            same_total += stats.get('total', 0)
            same_wins += stats.get('wins', 0)
        else:
            lower_total += stats.get('total', 0)
            lower_wins += stats.get('wins', 0)
    
    upper_wr = round(upper_wins / upper_total * 100, 2) if upper_total > 0 else 0
    same_wr = round(same_wins / same_total * 100, 2) if same_total > 0 else 0
    lower_wr = round(lower_wins / lower_total * 100, 2) if lower_total > 0 else 0
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.tier-cards {{ display: flex; gap: 40px; margin-top: 60px; }}
.tier-card {{
    flex: 1;
    background: rgba(255,255,255,0.03);
    border: 1px solid #333;
    border-radius: 15px;
    padding: 40px;
    text-align: center;
}}
.tier-label {{ font-size: 20px; color: #888; margin-bottom: 20px; }}
.tier-games {{ font-size: 48px; font-weight: 900; margin-bottom: 10px; }}
.tier-wr {{ font-size: 32px; font-weight: 700; color: #4A90D9; }}
.tier-detail {{ font-size: 16px; color: #666; margin-top: 10px; }}
</style></head>
<body>
    <div class="section-title">상대 티어별 비교</div>
    <div class="description">현재 티어: {member_tier}</div>
    
    <div class="tier-cards">
        <div class="tier-card">
            <div class="tier-label">상위 티어</div>
            <div class="tier-games">{upper_total}</div>
            <div class="tier-wr">{upper_wr}%</div>
            <div class="tier-detail">{upper_wins}승 {upper_total - upper_wins}패</div>
        </div>
        <div class="tier-card">
            <div class="tier-label">동일 티어 ({member_tier})</div>
            <div class="tier-games">{same_total}</div>
            <div class="tier-wr">{same_wr}%</div>
            <div class="tier-detail">{same_wins}승 {same_total - same_wins}패</div>
        </div>
        <div class="tier-card">
            <div class="tier-label">하위 티어</div>
            <div class="tier-games">{lower_total}</div>
            <div class="tier-wr">{lower_wr}%</div>
            <div class="tier-detail">{lower_wins}승 {lower_total - lower_wins}패</div>
        </div>
    </div>
    <div class="footer">HMD</div>
</body></html>'''


# ============================================================
# 04. 대회 분석
# ============================================================

def gen_04_01_tournament_overview(data):
    """04-01. 대회별 전적 요약"""
    tour = data['tournament_stats']
    overall = tour['overall']
    by_tour = tour['by_tournament']
    
    rows_html = ""
    for name, stats in sorted(by_tour.items(), key=lambda x: x[1].get('total', 0), reverse=True):
        wr = stats.get('winrate', 0)
        color = '#4A90D9' if wr >= 55 else '#e74c3c' if wr < 50 else '#fff'
        rows_html += f'''
        <tr>
            <td>{name}</td>
            <td>{stats.get('total', 0)}</td>
            <td>{stats.get('wins', 0)}</td>
            <td>{stats.get('losses', 0)}</td>
            <td style="color: {color}; font-weight: 700;">{wr}%</td>
        </tr>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.overview {{
    display: flex;
    gap: 60px;
    margin-bottom: 40px;
    padding: 30px;
    background: rgba(74, 144, 217, 0.1);
    border-radius: 15px;
}}
.overview-item {{ text-align: center; }}
.overview-value {{ font-size: 48px; font-weight: 900; color: #4A90D9; }}
.overview-label {{ font-size: 18px; color: #888; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
th {{ background: #2a2a2a; padding: 18px; text-align: center; font-size: 18px; border-bottom: 2px solid #4A90D9; }}
td {{ padding: 16px; text-align: center; font-size: 16px; border-bottom: 1px solid #333; }}
</style></head>
<body>
    <div class="section-title">대회별 전적 요약</div>
    
    <div class="overview">
        <div class="overview-item">
            <div class="overview-value">{overall.get('total', 0)}</div>
            <div class="overview-label">총 대회 경기</div>
        </div>
        <div class="overview-item">
            <div class="overview-value">{overall.get('winrate', 0)}%</div>
            <div class="overview-label">대회 승률</div>
        </div>
        <div class="overview-item">
            <div class="overview-value">{overall.get('wins', 0)}</div>
            <div class="overview-label">승리</div>
        </div>
        <div class="overview-item">
            <div class="overview-value">{overall.get('losses', 0)}</div>
            <div class="overview-label">패배</div>
        </div>
    </div>
    
    <table>
        <thead><tr><th>대회명</th><th>경기수</th><th>승</th><th>패</th><th>승률</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    <div class="footer">HMD</div>
</body></html>'''


def gen_04_02_tournament_members(data):
    """04-02. 대회 멤버별 기여도"""
    by_member = data['tournament_stats']['by_member']
    
    rows_html = ""
    for i, stats in enumerate(by_member, 1):
        wr = stats.get('winrate', 0)
        color = '#4A90D9' if wr >= 55 else '#e74c3c' if wr < 50 else '#fff'
        rows_html += f'''
        <tr>
            <td>{i}</td>
            <td>{stats.get('name', '')}</td>
            <td>{stats.get('total', 0)}</td>
            <td>{stats.get('wins', 0)}</td>
            <td>{stats.get('losses', 0)}</td>
            <td style="color: {color}; font-weight: 700;">{wr}%</td>
        </tr>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
table {{ width: 100%; border-collapse: collapse; margin-top: 50px; }}
th {{ background: #2a2a2a; padding: 18px; text-align: center; font-size: 18px; border-bottom: 2px solid #4A90D9; }}
td {{ padding: 16px; text-align: center; font-size: 16px; border-bottom: 1px solid #333; }}
</style></head>
<body>
    <div class="section-title">대회 멤버별 기여도</div>
    <div class="description">대회 출전 횟수 및 승률 순위</div>
    
    <table>
        <thead><tr><th>순위</th><th>닉네임</th><th>경기수</th><th>승</th><th>패</th><th>승률</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    <div class="footer">HMD</div>
</body></html>'''


# ============================================================
# 05. 맵 분석
# ============================================================

def gen_05_01_map_overview(data):
    """05-01. 맵별 전적 개요"""
    maps = data['map_stats']
    
    # 상위 10개 맵
    sorted_maps = sorted(maps.items(), key=lambda x: x[1].get('total', 0), reverse=True)[:10]
    
    rows_html = ""
    for name, stats in sorted_maps:
        wr = stats.get('winrate', 0)
        color = '#4A90D9' if wr >= 55 else '#e74c3c' if wr < 50 else '#fff'
        rows_html += f'''
        <tr>
            <td>{name}</td>
            <td>{stats.get('total', 0):,}</td>
            <td>{stats.get('wins', 0):,}</td>
            <td>{stats.get('losses', 0):,}</td>
            <td style="color: {color}; font-weight: 700;">{wr}%</td>
        </tr>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
table {{ width: 100%; border-collapse: collapse; margin-top: 50px; }}
th {{ background: #2a2a2a; padding: 18px; text-align: center; font-size: 18px; border-bottom: 2px solid #4A90D9; }}
td {{ padding: 16px; text-align: center; font-size: 16px; border-bottom: 1px solid #333; }}
</style></head>
<body>
    <div class="section-title">맵별 전적 개요</div>
    <div class="description">2025년 사용된 전체 맵 승률 순위</div>
    
    <table>
        <thead><tr><th>맵 이름</th><th>경기수</th><th>승</th><th>패</th><th>승률</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    <div class="footer">HMD</div>
</body></html>'''


# ============================================================
# 06. 상대 분석
# ============================================================

def gen_06_01_opponent_overview(data):
    """06-01. 주요 상대 전적"""
    opps = data['opponent_stats']['top_opponents'][:20]
    
    rows_html = ""
    for opp in opps:
        wr = opp.get('winrate', 0)
        color = '#4A90D9' if wr >= 55 else '#e74c3c' if wr < 50 else '#fff'
        rows_html += f'''
        <tr>
            <td>{opp.get('name', '')}</td>
            <td>{opp.get('race', '')}</td>
            <td>{opp.get('tier', '')}</td>
            <td>{opp.get('total', 0)}</td>
            <td>{opp.get('wins', 0)}</td>
            <td>{opp.get('losses', 0)}</td>
            <td style="color: {color}; font-weight: 700;">{wr}%</td>
        </tr>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
table {{ width: 100%; border-collapse: collapse; margin-top: 40px; }}
th {{ background: #2a2a2a; padding: 16px; text-align: center; font-size: 16px; border-bottom: 2px solid #4A90D9; }}
td {{ padding: 14px; text-align: center; font-size: 15px; border-bottom: 1px solid #333; }}
</style></head>
<body>
    <div class="section-title">주요 상대 전적</div>
    <div class="description">2025년 30경기 이상 대전한 상대 (경기수 순)</div>
    
    <table>
        <thead><tr><th>상대</th><th>종족</th><th>티어</th><th>경기수</th><th>승</th><th>패</th><th>승률</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    <div class="footer">HMD</div>
</body></html>'''


def gen_06_02_vs_tier(data):
    """06-02. 상대 티어별 분석"""
    by_tier = data['opponent_stats']['by_tier']
    
    bars_html = ""
    for tier in ['1티어', '2티어', '3티어', '4티어', '5티어', '6티어', '7티어', '8티어', '베이비']:
        stats = by_tier.get(tier, {})
        if not stats:
            continue
        wr = stats.get('winrate', 0)
        height = min(wr * 3, 200)
        color = '#4A90D9' if wr >= 55 else '#e74c3c' if wr < 50 else '#888'
        bars_html += f'''
        <div class="tier-bar">
            <div class="tier-wr" style="color: {color};">{wr}%</div>
            <div class="tier-bar-inner" style="height: {height}px; background: {color};"></div>
            <div class="tier-name">{tier}</div>
            <div class="tier-games">{stats.get('total', 0)}전</div>
        </div>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.chart {{ display: flex; justify-content: center; align-items: flex-end; gap: 30px; height: 400px; margin-top: 80px; }}
.tier-bar {{ text-align: center; }}
.tier-wr {{ font-size: 18px; font-weight: 700; margin-bottom: 10px; }}
.tier-bar-inner {{ width: 80px; border-radius: 6px 6px 0 0; margin: 0 auto 10px; }}
.tier-name {{ font-size: 16px; font-weight: 600; }}
.tier-games {{ font-size: 14px; color: #888; }}
</style></head>
<body>
    <div class="section-title">상대 티어별 분석</div>
    <div class="description">상위 티어 상대로는 고전, 하위 티어 상대로는 우세한 경향</div>
    
    <div class="chart">{bars_html}</div>
    <div class="footer">HMD</div>
</body></html>'''


# ============================================================
# 메인 실행
# ============================================================

async def generate_all(data):
    """모든 페이지 생성"""
    pages = []
    
    # 02. 전체 전적 분석 추가 페이지
    pages.append(("02-03_quarterly", gen_02_03_quarterly(data)))
    pages.append(("02-04_type_detail", gen_02_04_type_detail(data)))
    pages.append(("02-05_race", gen_02_05_race(data)))
    pages.append(("02-06_matchup", gen_02_06_matchup(data)))
    
    # 03. 멤버별 상세 (14명 × 4페이지 추가)
    members_sorted = sorted(
        data['member_details'].items(),
        key=lambda x: x[1]['overall']['total'],
        reverse=True
    )
    
    for idx, (member_name, _) in enumerate(members_sorted, 1):
        # 월별 전적
        html = gen_member_monthly(data, member_name)
        if html:
            pages.append((f"03-{idx:02d}-1_{member_name}_monthly", html))
        
        # 상대 종족별
        html = gen_member_vs_race(data, member_name)
        if html:
            pages.append((f"03-{idx:02d}-2_{member_name}_vs_race", html))
        
        # 맵별
        html = gen_member_by_map(data, member_name)
        if html:
            pages.append((f"03-{idx:02d}-3_{member_name}_by_map", html))
        
        # 티어별
        html = gen_member_vs_tier(data, member_name)
        if html:
            pages.append((f"03-{idx:02d}-4_{member_name}_vs_tier", html))
    
    # 04. 대회 분석
    pages.append(("04-01_tournament_overview", gen_04_01_tournament_overview(data)))
    pages.append(("04-02_tournament_members", gen_04_02_tournament_members(data)))
    
    # 05. 맵 분석
    pages.append(("05-01_map_overview", gen_05_01_map_overview(data)))
    
    # 06. 상대 분석
    pages.append(("06-01_opponent_overview", gen_06_01_opponent_overview(data)))
    pages.append(("06-02_vs_tier", gen_06_02_vs_tier(data)))
    
    print(f"\n총 {len(pages)}개 페이지 렌더링 시작...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        for name, html in pages:
            if html is None:
                continue
            output_path = OUTPUT_DIR / f"{name}.png"
            page = await browser.new_page(viewport={'width': WIDTH, 'height': HEIGHT})
            await page.set_content(html)
            await page.screenshot(path=str(output_path), type='png')
            await page.close()
            print(f"  ✓ {name}.png")
        
        await browser.close()
    
    print(f"\n모든 페이지 생성 완료! 출력: {OUTPUT_DIR}")


def main():
    print("K UNIVERSITY 2025 연간 보고서 전체 생성 시작...")
    data = load_data()
    asyncio.run(generate_all(data))


if __name__ == "__main__":
    main()
