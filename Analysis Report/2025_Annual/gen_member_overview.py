#!/usr/bin/env python3
"""
03-00 멤버 전체 비교 페이지 생성
- 모든 멤버의 연간 경기수와 승률 비교 그래프
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
            'tier_achieved_date': tier_first_date
        })
    
    return sorted(member_tier_info, key=lambda x: (x['tier_order'], x['tier_achieved_date']))


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


def gen_03_00_member_overview(data):
    """03-00. 멤버별 경기수/승률 비교 그래프"""
    sorted_members = get_sorted_members()
    
    # 멤버별 데이터 수집
    members_data = []
    max_games = 0
    
    for m_info in sorted_members:
        name = m_info['name']
        member = data['member_details'][name]
        overall = member['overall']
        
        members_data.append({
            'name': name,
            'tier': m_info['final_tier'],
            'total': overall['total'],
            'winrate': overall['winrate'],
            'race': member['race']
        })
        
        if overall['total'] > max_games:
            max_games = overall['total']
    
    # 종족별 색상
    race_colors = {
        '테란': '#4A90D9',
        '저그': '#9B59B6',
        '프로토스': '#F1C40F'
    }
    
    # 막대 그래프 HTML
    bars_html = ""
    bar_width = 100
    bar_gap = 20
    chart_height = 400
    
    for i, m in enumerate(members_data):
        # 경기수 막대 높이 (최대 400px)
        games_height = (m['total'] / max_games) * chart_height if max_games > 0 else 0
        
        # 승률 포인트 위치 (0-100% -> 0-400px)
        wr_position = m['winrate'] * 4
        
        race_color = race_colors.get(m['race'], '#4A90D9')
        
        bars_html += f'''
        <div class="member-bar" style="left: {i * (bar_width + bar_gap)}px;">
            <div class="wr-point" style="bottom: {wr_position}px;">
                <span class="wr-value">{m['winrate']}%</span>
            </div>
            <div class="games-bar" style="height: {games_height}px; background: linear-gradient(180deg, {race_color} 0%, {race_color}66 100%);">
                <span class="games-value">{m['total']}</span>
            </div>
            <div class="member-name">{m['name']}</div>
            <div class="member-tier">{m['tier']}</div>
        </div>
        '''
    
    # 승률 연결선 SVG
    chart_width = len(members_data) * (bar_width + bar_gap)
    svg_points = []
    for i, m in enumerate(members_data):
        x = i * (bar_width + bar_gap) + bar_width / 2
        y = chart_height - (m['winrate'] * 4)
        svg_points.append((x, y))
    
    svg_path = ""
    if len(svg_points) > 1:
        path_d = f"M {svg_points[0][0]} {svg_points[0][1]}"
        for x, y in svg_points[1:]:
            path_d += f" L {x} {y}"
        svg_path = f'<path d="{path_d}" stroke="#fff" stroke-width="2" fill="none" stroke-dasharray="5,5" opacity="0.5"/>'
    
    # 평균값 계산
    avg_games = sum(m['total'] for m in members_data) / len(members_data)
    avg_wr = sum(m['winrate'] for m in members_data) / len(members_data)
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.chart-container {{
    position: relative;
    margin-top: 50px;
    height: 550px;
}}
.chart-area {{
    position: relative;
    height: {chart_height}px;
    margin-bottom: 80px;
}}
.member-bar {{
    position: absolute;
    bottom: 80px;
    width: {bar_width}px;
    text-align: center;
}}
.games-bar {{
    width: 60px;
    margin: 0 auto;
    border-radius: 6px 6px 0 0;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 10px;
    min-height: 30px;
}}
.games-value {{
    font-size: 14px;
    font-weight: 700;
    color: #fff;
}}
.member-name {{
    margin-top: 10px;
    font-size: 16px;
    font-weight: 600;
}}
.member-tier {{
    font-size: 12px;
    color: #888;
    margin-top: 2px;
}}
.wr-point {{
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
}}
.wr-value {{
    background: rgba(255, 255, 255, 0.9);
    color: #1a1a1a;
    padding: 4px 8px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 700;
    white-space: nowrap;
}}
.svg-overlay {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: {chart_height}px;
    pointer-events: none;
}}
.legend {{
    display: flex;
    gap: 40px;
    margin-top: 20px;
}}
.legend-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 16px;
    color: #888;
}}
.legend-bar {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
}}
.legend-line {{
    width: 30px;
    height: 2px;
    background: #fff;
    border-style: dashed;
}}
.stats-summary {{
    display: flex;
    gap: 60px;
    margin-top: 30px;
    padding: 20px 40px;
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    width: fit-content;
}}
.stat-item {{ text-align: center; }}
.stat-value {{ font-size: 28px; font-weight: 700; color: #4A90D9; }}
.stat-label {{ font-size: 14px; color: #888; margin-top: 5px; }}
</style></head>
<body>
    <div class="section-title">멤버별 전적 비교</div>
    <div class="description">2025년 연간 경기수 및 승률 비교 (티어 순 정렬)</div>
    
    <div class="stats-summary">
        <div class="stat-item">
            <div class="stat-value">{len(members_data)}</div>
            <div class="stat-label">총 멤버</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{avg_games:.0f}</div>
            <div class="stat-label">평균 경기수</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{avg_wr:.1f}%</div>
            <div class="stat-label">평균 승률</div>
        </div>
    </div>
    
    <div class="chart-container">
        <svg class="svg-overlay" viewBox="0 0 {chart_width} {chart_height}" preserveAspectRatio="xMinYMin meet">
            {svg_path}
        </svg>
        <div class="chart-area">
            {bars_html}
        </div>
    </div>
    
    <div class="legend">
        <div class="legend-item">
            <div class="legend-bar" style="background: #4A90D9;"></div>
            <span>테란</span>
        </div>
        <div class="legend-item">
            <div class="legend-bar" style="background: #9B59B6;"></div>
            <span>저그</span>
        </div>
        <div class="legend-item">
            <div class="legend-bar" style="background: #F1C40F;"></div>
            <span>프로토스</span>
        </div>
        <div class="legend-item">
            <span style="color: #666;">막대: 경기수 / 점선: 승률</span>
        </div>
    </div>
    
    <div class="footer">HMD</div>
</body></html>'''


async def main():
    data = load_data()
    
    html = gen_03_00_member_overview(data)
    output_path = OUTPUT_DIR / "03-00_member_overview.png"
    
    print("03-00 멤버 전체 비교 페이지 생성 중...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': WIDTH, 'height': HEIGHT})
        await page.set_content(html)
        await page.screenshot(path=str(output_path), type='png')
        await page.close()
        await browser.close()
    
    print(f"✓ {output_path.name} 생성 완료!")


if __name__ == "__main__":
    asyncio.run(main())
