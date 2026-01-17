#!/usr/bin/env python3
"""
멤버 순서 변경 및 전체 재생성
- 최종 티어 기준 정렬
- 동일 티어는 해당 티어 달성일 기준 정렬
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
            'tier_achieved_date': tier_first_date,
            'race': m_data['멤버 종족'].iloc[0]
        })
    
    return sorted(member_tier_info, key=lambda x: (x['tier_order'], x['tier_achieved_date']))


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
'''


def get_race_color(race):
    colors = {'테란': '#4A90D9', '저그': '#9B59B6', '프로토스': '#F1C40F'}
    return colors.get(race, '#4A90D9')


def gen_profile(data, member_name, rank, member_info):
    """멤버 프로필 페이지"""
    member = data['member_details'][member_name]
    overall = member['overall']
    spon = member['by_type'].get('스폰', {'total': 0, 'wins': 0, 'losses': 0, 'winrate': 0})
    tour = member['by_type'].get('대회', {'total': 0, 'wins': 0, 'losses': 0, 'winrate': 0})
    
    tier_display = member['tier_end']
    if member['tier_start'] != member['tier_end']:
        tier_display = f"{member['tier_start']} → {member['tier_end']}"
    
    race_color = get_race_color(member['race'])
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    width: {WIDTH}px; height: {HEIGHT}px;
    background: #1a1a1a;
    font-family: 'Pretendard', sans-serif;
    color: #fff;
    display: flex;
}}
.left {{
    width: 500px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px;
}}
.profile-image {{
    width: 350px; height: 450px;
    background: linear-gradient(135deg, #333 0%, #222 100%);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 120px;
    color: {race_color};
    margin-bottom: 30px;
    border: 3px solid {race_color}33;
}}
.member-name {{ font-size: 48px; font-weight: 900; margin-bottom: 10px; }}
.member-meta {{ font-size: 24px; color: {race_color}; }}
.right {{
    flex: 1;
    padding: 80px 80px 80px 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}
.section-label {{ font-size: 18px; color: #888; margin-bottom: 10px; }}
.stats-box {{
    background: rgba(255,255,255,0.03);
    border: 1px solid #333;
    border-radius: 15px;
    padding: 35px 45px;
    margin-bottom: 30px;
}}
.stats-title {{ font-size: 22px; font-weight: 700; margin-bottom: 25px; color: {race_color}; }}
.stats-row {{
    display: flex;
    justify-content: space-between;
    padding: 15px 0;
    border-bottom: 1px solid #333;
    font-size: 20px;
}}
.stats-row:last-child {{ border-bottom: none; }}
.stats-label {{ color: #888; }}
.stats-value {{ font-weight: 700; }}
.highlight {{ color: {race_color}; }}
.rank-badge {{
    position: absolute;
    top: 60px;
    right: 120px;
    font-size: 18px;
    color: #666;
}}
.footer {{
    position: absolute;
    bottom: 60px;
    right: 120px;
    left: 120px;
    border-top: 1px solid #444;
    padding-top: 20px;
    text-align: right;
    font-size: 24px;
    color: #666;
}}
</style></head>
<body>
    <div class="rank-badge">#{rank} / 14</div>
    <div class="left">
        <div class="profile-image">👤</div>
        <div class="member-name">{member_name}</div>
        <div class="member-meta">{tier_display} {member['race']}</div>
    </div>
    <div class="right">
        <div class="section-label">2025년 연간 전적</div>
        <div class="stats-box">
            <div class="stats-title">전적 요약</div>
            <div class="stats-row">
                <span class="stats-label">전체</span>
                <span class="stats-value">{overall['total']}전 {overall['wins']}승 {overall['losses']}패 <span class="highlight">{overall['winrate']}%</span></span>
            </div>
            <div class="stats-row">
                <span class="stats-label">스폰</span>
                <span class="stats-value">{spon['total']}전 {spon['wins']}승 {spon['losses']}패 {spon['winrate']}%</span>
            </div>
            <div class="stats-row">
                <span class="stats-label">대회 및 CK</span>
                <span class="stats-value">{tour['total']}전 {tour['wins']}승 {tour['losses']}패 {tour['winrate']}%</span>
            </div>
        </div>
        <div class="stats-box">
            <div class="stats-title">상대 종족별 전적</div>
            {''.join(f"""<div class="stats-row"><span class="stats-label">vs {race}</span><span class="stats-value">{member['vs_race'].get(race, {}).get('total', 0)}전 {member['vs_race'].get(race, {}).get('winrate', 0)}%</span></div>""" for race in ['테란', '저그', '프로토스'] if member['vs_race'].get(race))}
        </div>
    </div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_monthly(data, member_name):
    """월별 전적 추이"""
    member = data['member_details'][member_name]
    monthly = member['monthly']
    
    if not monthly:
        return None
    
    max_games = max((m.get('total', 0) for m in monthly.values()), default=1)
    
    bars_html = ""
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    
    # 승률 포인트 좌표 계산 (SVG 라인용)
    chart_width = 1680  # 전체 차트 너비
    chart_height = 300  # 승률 라인이 그려질 높이
    bar_spacing = chart_width / 12  # 각 막대 간격
    
    line_points = []
    
    for i in range(1, 13):
        stats = monthly.get(i, monthly.get(str(i), {}))
        if not stats:
            bars_html += f'<div class="month-bar"><div class="bar-empty"></div><div class="month-name">{months[i-1]}</div></div>'
            continue
        
        height = (stats.get('total', 0) / max_games) * 250 if max_games > 0 else 0
        wr = stats.get('winrate', 0)
        
        # SVG 좌표 계산 (x: 막대 중앙, y: 승률에 비례)
        x = (i - 0.5) * bar_spacing
        y = chart_height - (wr * 2.5)  # 위로 갈수록 y 감소
        line_points.append((x, y, wr))
        
        bars_html += f'''
        <div class="month-bar">
            <div class="wr-point" style="bottom: {wr * 2.5}px;">{wr}%</div>
            <div class="bar" style="height: {height}px;"><span class="bar-value">{stats.get('total', 0)}</span></div>
            <div class="month-name">{months[i-1]}</div>
        </div>'''
    
    # SVG 꺾은선 생성
    svg_line = ""
    if len(line_points) > 1:
        path_d = f"M {line_points[0][0]} {line_points[0][1]}"
        for x, y, _ in line_points[1:]:
            path_d += f" L {x} {y}"
        svg_line = f'<path d="{path_d}" stroke="#4A90D9" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        
        # 포인트 원 추가
        for x, y, _ in line_points:
            svg_line += f'<circle cx="{x}" cy="{y}" r="6" fill="#4A90D9"/>'
    
    avg_games = sum(m.get('total', 0) for m in monthly.values()) / len(monthly) if monthly else 0
    avg_wr = sum(m.get('winrate', 0) for m in monthly.values()) / len(monthly) if monthly else 0
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.chart-wrapper {{ position: relative; margin-top: 60px; }}
.chart {{ display: flex; justify-content: space-around; align-items: flex-end; height: 400px; position: relative; }}
.svg-overlay {{
    position: absolute;
    top: 70px;
    left: 0;
    width: 100%;
    height: 300px;
    pointer-events: none;
}}
.month-bar {{ text-align: center; position: relative; width: {100/12}%; }}
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
    z-index: 10;
}}
</style></head>
<body>
    <div class="section-title">월별 전적 추이</div>
    <div class="description">월 평균 {avg_games:.1f}회 게임 진행</div>
    <div class="description">승률 평균 {avg_wr:.2f}%</div>
    <div class="chart-wrapper">
        <svg class="svg-overlay" viewBox="0 0 {chart_width} {chart_height}" preserveAspectRatio="none">
            {svg_line}
        </svg>
        <div class="chart">{bars_html}</div>
    </div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_vs_race(data, member_name):
    """상대 종족별 전적"""
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
            <div class="race-info"><span class="race-games">{stats.get('total', 0)}</span><span class="race-name">{race}</span></div>
            <div class="race-wr">{stats.get('winrate', 0)}%</div>
        </div>'''
    
    opp_rows = ""
    for opp in top_opps[:6]:
        wr = opp.get('winrate', 0)
        color = '#4A90D9' if wr >= 55 else '#e74c3c' if wr < 50 else '#fff'
        opp_rows += f'''<div class="opp-row"><span class="opp-name">{opp.get('name', '')} ({opp.get('race', '')})</span><span class="opp-games">{opp.get('total', 0)}전</span><span class="opp-wr" style="color: {color};">{wr}%</span></div>'''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.content {{ display: flex; gap: 60px; margin-top: 60px; }}
.card {{ flex: 1; background: rgba(255,255,255,0.03); border: 1px solid #333; border-radius: 15px; padding: 40px; }}
.card-title {{ font-size: 24px; font-weight: 700; margin-bottom: 30px; }}
.race-bar {{ display: flex; justify-content: space-between; align-items: center; padding: 20px; border-bottom: 1px solid #333; }}
.race-info {{ display: flex; align-items: center; gap: 20px; }}
.race-games {{ font-size: 32px; font-weight: 700; }}
.race-name {{ font-size: 18px; color: #888; }}
.race-wr {{ font-size: 28px; font-weight: 700; color: #4A90D9; }}
.opp-row {{ display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px solid #333; font-size: 18px; }}
.opp-name {{ flex: 2; }}
.opp-games {{ flex: 1; text-align: center; color: #888; }}
.opp-wr {{ flex: 1; text-align: right; font-weight: 700; }}
</style></head>
<body>
    <div class="section-title">상대 종족별 비교</div>
    <div class="content">
        <div class="card"><div class="card-title">종족별 전적 비교</div>{race_bars}</div>
        <div class="card"><div class="card-title">주요 상대별 전적</div>{opp_rows}</div>
    </div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_by_map(data, member_name):
    """맵별 전적"""
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
            <div class="map-stats"><span class="map-games">{stats.get('total', 0)}전</span><span class="map-wr">{wr}%</span></div>
            <div class="map-bar-bg"><div class="map-bar-fill" style="width: {wr}%;"></div></div>
        </div>'''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.map-list {{ margin-top: 60px; }}
.map-bar {{ display: flex; align-items: center; gap: 30px; padding: 25px 0; border-bottom: 1px solid #333; }}
.map-name {{ width: 150px; font-size: 22px; font-weight: 600; }}
.map-stats {{ width: 150px; text-align: right; }}
.map-games {{ font-size: 18px; color: #888; margin-right: 20px; }}
.map-wr {{ font-size: 22px; font-weight: 700; color: #4A90D9; }}
.map-bar-bg {{ flex: 1; height: 20px; background: #333; border-radius: 10px; overflow: hidden; }}
.map-bar-fill {{ height: 100%; background: linear-gradient(90deg, #4A90D9 0%, #2a5a8a 100%); border-radius: 10px; }}
</style></head>
<body>
    <div class="section-title">주요 맵별 비교</div>
    <div class="map-list">{bars_html}</div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_vs_tier(data, member_name):
    """상대 티어별 전적"""
    member = data['member_details'][member_name]
    vs_tier = member['vs_tier']
    member_tier = member['tier_end']
    
    tier_order = ['1티어', '2티어', '3티어', '4티어', '5티어', '6티어', '7티어', '8티어', '베이비']
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
.tier-card {{ flex: 1; background: rgba(255,255,255,0.03); border: 1px solid #333; border-radius: 15px; padding: 40px; text-align: center; }}
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


async def regenerate_all():
    """모든 멤버 페이지 재생성"""
    data = load_data()
    sorted_members = get_sorted_members()
    
    print("=== 멤버 순서 (최종 티어/달성일 기준) ===")
    for i, m in enumerate(sorted_members, 1):
        print(f"{i:2d}. {m['name']} ({m['final_tier']})")
    
    # 기존 03-XX 파일 삭제
    print("\n기존 멤버 페이지 삭제 중...")
    for old_file in OUTPUT_DIR.glob("03-*"):
        old_file.unlink()
    
    pages = []
    
    for idx, member_info in enumerate(sorted_members, 1):
        member_name = member_info['name']
        
        # 프로필
        pages.append((f"03-{idx:02d}_00_{member_name}_profile", gen_profile(data, member_name, idx, member_info)))
        
        # 월별
        html = gen_monthly(data, member_name)
        if html:
            pages.append((f"03-{idx:02d}-1_{member_name}_monthly", html))
        
        # 종족별
        html = gen_vs_race(data, member_name)
        if html:
            pages.append((f"03-{idx:02d}-2_{member_name}_vs_race", html))
        
        # 맵별
        html = gen_by_map(data, member_name)
        if html:
            pages.append((f"03-{idx:02d}-3_{member_name}_by_map", html))
        
        # 티어별
        html = gen_vs_tier(data, member_name)
        if html:
            pages.append((f"03-{idx:02d}-4_{member_name}_vs_tier", html))
    
    print(f"\n총 {len(pages)}개 페이지 생성 중...")
    
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
    
    print("\n멤버 페이지 재생성 완료!")


def main():
    asyncio.run(regenerate_all())


if __name__ == "__main__":
    main()
