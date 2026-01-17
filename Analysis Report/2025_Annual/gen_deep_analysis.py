#!/usr/bin/env python3
"""
심층 분석 페이지 생성
- 티어별 비교: 경기 시점 기준으로 수정
- 40% 미만 승률 항목에 대한 원인 분석
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
.section-title { font-size: 48px; font-weight: 900; margin-bottom: 15px; }
.description { font-size: 20px; color: #aaa; margin-bottom: 8px; }
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
.warning { color: #e74c3c; font-weight: 700; }
'''


def get_member_deep_analysis(member_name):
    """멤버별 심층 분석 데이터 수집"""
    df = pd.read_excel(EXCEL_PATH)
    df_2025 = df[(df['날짜'] >= '2025-01-01') & (df['날짜'] <= '2025-12-31')].copy()
    m_df = df_2025[df_2025['멤버 이름'] == member_name]
    
    analysis = {
        'name': member_name,
        'weak_points': [],  # 40% 미만 항목들
        'deep_analysis': {}  # 심층 분석 결과
    }
    
    # 종족별 전적 (경기수 10 이상, 40% 미만)
    for race in ['테란', '저그', '프로토스']:
        race_df = m_df[m_df['상대 종족'] == race]
        if len(race_df) >= 10:
            wins = len(race_df[race_df['결과'] == '승'])
            wr = round(wins / len(race_df) * 100, 2)
            if wr < 40:
                analysis['weak_points'].append({
                    'type': 'race',
                    'target': race,
                    'total': len(race_df),
                    'winrate': wr
                })
                # 해당 종족전 상대별 전적
                opp_stats = {}
                for _, row in race_df.iterrows():
                    opp = row['상대']
                    result = 1 if row['결과'] == '승' else 0
                    if opp not in opp_stats:
                        opp_stats[opp] = {'wins': 0, 'losses': 0}
                    if result:
                        opp_stats[opp]['wins'] += 1
                    else:
                        opp_stats[opp]['losses'] += 1
                
                for opp in opp_stats:
                    s = opp_stats[opp]
                    s['total'] = s['wins'] + s['losses']
                    s['winrate'] = round(s['wins'] / s['total'] * 100, 2) if s['total'] > 0 else 0
                
                analysis['deep_analysis'][f'vs_{race}'] = {
                    'opponents': sorted(opp_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:10],
                    'by_map': {}
                }
                
                # 해당 종족전 맵별 전적
                for map_name in race_df['맵'].unique():
                    map_race_df = race_df[race_df['맵'] == map_name]
                    if len(map_race_df) >= 3:
                        map_wins = len(map_race_df[map_race_df['결과'] == '승'])
                        analysis['deep_analysis'][f'vs_{race}']['by_map'][map_name] = {
                            'total': len(map_race_df),
                            'wins': map_wins,
                            'winrate': round(map_wins / len(map_race_df) * 100, 2)
                        }
    
    # 맵별 전적 (경기수 10 이상, 40% 미만)
    for map_name in m_df['맵'].unique():
        map_df = m_df[m_df['맵'] == map_name]
        if len(map_df) >= 10:
            wins = len(map_df[map_df['결과'] == '승'])
            wr = round(wins / len(map_df) * 100, 2)
            if wr < 40:
                analysis['weak_points'].append({
                    'type': 'map',
                    'target': map_name,
                    'total': len(map_df),
                    'winrate': wr
                })
                
                # 해당 맵 종족별 전적
                race_stats = {}
                for race in ['테란', '저그', '프로토스']:
                    race_map_df = map_df[map_df['상대 종족'] == race]
                    if len(race_map_df) >= 1:
                        race_wins = len(race_map_df[race_map_df['결과'] == '승'])
                        race_stats[race] = {
                            'total': len(race_map_df),
                            'wins': race_wins,
                            'winrate': round(race_wins / len(race_map_df) * 100, 2) if len(race_map_df) > 0 else 0
                        }
                
                # 해당 맵 상대별 전적
                opp_stats = {}
                for _, row in map_df.iterrows():
                    opp = row['상대']
                    opp_race = row['상대 종족']
                    result = 1 if row['결과'] == '승' else 0
                    if opp not in opp_stats:
                        opp_stats[opp] = {'race': opp_race, 'wins': 0, 'losses': 0}
                    if result:
                        opp_stats[opp]['wins'] += 1
                    else:
                        opp_stats[opp]['losses'] += 1
                
                for opp in opp_stats:
                    s = opp_stats[opp]
                    s['total'] = s['wins'] + s['losses']
                    s['winrate'] = round(s['wins'] / s['total'] * 100, 2) if s['total'] > 0 else 0
                
                analysis['deep_analysis'][f'map_{map_name}'] = {
                    'by_race': race_stats,
                    'opponents': sorted(opp_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:8]
                }
    
    # 티어별 전적 (경기 시점 기준으로 재계산)
    tier_order = {'1티어': 1, '2티어': 2, '3티어': 3, '4티어': 4, '5티어': 5, 
                  '6티어': 6, '7티어': 7, '8티어': 8, '베이비': 9}
    
    # 경기 시점 기준 티어 비교
    tier_comparison = {'상위': {'wins': 0, 'total': 0}, '동일': {'wins': 0, 'total': 0}, '하위': {'wins': 0, 'total': 0}}
    
    for _, row in m_df.iterrows():
        my_tier = tier_order.get(row['멤버 티어'], 9)
        opp_tier = tier_order.get(row['상대 티어'], 9)
        result = 1 if row['결과'] == '승' else 0
        
        if opp_tier < my_tier:  # 상대가 상위 티어
            tier_comparison['상위']['total'] += 1
            tier_comparison['상위']['wins'] += result
        elif opp_tier == my_tier:  # 동일 티어
            tier_comparison['동일']['total'] += 1
            tier_comparison['동일']['wins'] += result
        else:  # 상대가 하위 티어
            tier_comparison['하위']['total'] += 1
            tier_comparison['하위']['wins'] += result
    
    for key in tier_comparison:
        t = tier_comparison[key]
        t['winrate'] = round(t['wins'] / t['total'] * 100, 2) if t['total'] > 0 else 0
    
    analysis['tier_comparison'] = tier_comparison
    
    return analysis


def gen_tier_comparison_page(member_name, analysis, idx):
    """티어별 비교 페이지 (경기 시점 기준)"""
    tc = analysis['tier_comparison']
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.tier-cards {{ display: flex; gap: 40px; margin-top: 50px; }}
.tier-card {{ flex: 1; background: rgba(255,255,255,0.03); border: 1px solid #333; border-radius: 15px; padding: 40px; text-align: center; }}
.tier-label {{ font-size: 20px; color: #888; margin-bottom: 20px; }}
.tier-games {{ font-size: 48px; font-weight: 900; margin-bottom: 10px; }}
.tier-wr {{ font-size: 32px; font-weight: 700; }}
.tier-detail {{ font-size: 16px; color: #666; margin-top: 10px; }}
.note {{ margin-top: 40px; padding: 20px 30px; background: rgba(74, 144, 217, 0.1); border-left: 4px solid #4A90D9; font-size: 16px; color: #aaa; }}
</style></head>
<body>
    <div class="section-title">상대 티어별 비교</div>
    <div class="description">※ 경기 시점 기준 멤버 티어 대비 상대 티어 비교</div>
    
    <div class="tier-cards">
        <div class="tier-card">
            <div class="tier-label">상위 티어 상대</div>
            <div class="tier-games">{tc['상위']['total']}</div>
            <div class="tier-wr" style="color: {'#4A90D9' if tc['상위']['winrate'] >= 50 else '#e74c3c'};">{tc['상위']['winrate']}%</div>
            <div class="tier-detail">{tc['상위']['wins']}승 {tc['상위']['total'] - tc['상위']['wins']}패</div>
        </div>
        <div class="tier-card">
            <div class="tier-label">동일 티어 상대</div>
            <div class="tier-games">{tc['동일']['total']}</div>
            <div class="tier-wr" style="color: {'#4A90D9' if tc['동일']['winrate'] >= 50 else '#e74c3c'};">{tc['동일']['winrate']}%</div>
            <div class="tier-detail">{tc['동일']['wins']}승 {tc['동일']['total'] - tc['동일']['wins']}패</div>
        </div>
        <div class="tier-card">
            <div class="tier-label">하위 티어 상대</div>
            <div class="tier-games">{tc['하위']['total']}</div>
            <div class="tier-wr" style="color: {'#4A90D9' if tc['하위']['winrate'] >= 50 else '#e74c3c'};">{tc['하위']['winrate']}%</div>
            <div class="tier-detail">{tc['하위']['wins']}승 {tc['하위']['total'] - tc['하위']['wins']}패</div>
        </div>
    </div>
    
    <div class="note">
        ※ 각 경기 시점에서의 멤버 티어와 상대 티어를 비교하여 산출<br>
        예: 5티어 시절 4티어 상대와의 경기 → 상위 티어 상대로 분류
    </div>
    
    <div class="footer">HMD</div>
</body></html>'''


def gen_weakness_analysis_page(member_name, weakness, deep_data, idx):
    """약점 심층 분석 페이지"""
    w_type = weakness['type']
    target = weakness['target']
    total = weakness['total']
    winrate = weakness['winrate']
    
    if w_type == 'race':
        # 종족전 약점 분석
        key = f'vs_{target}'
        if key not in deep_data:
            return None
        
        data = deep_data[key]
        opponents = data['opponents']
        by_map = data['by_map']
        
        # 상대별 전적 테이블
        opp_rows = ""
        for opp, stats in opponents[:8]:
            wr_color = '#4A90D9' if stats['winrate'] >= 50 else '#e74c3c' if stats['winrate'] < 40 else '#fff'
            opp_rows += f'''
            <tr>
                <td>{opp}</td>
                <td>{stats['total']}</td>
                <td>{stats['wins']}</td>
                <td>{stats['total'] - stats['wins']}</td>
                <td style="color: {wr_color}; font-weight: 700;">{stats['winrate']}%</td>
            </tr>
            '''
        
        # 맵별 전적
        map_rows = ""
        sorted_maps = sorted(by_map.items(), key=lambda x: x[1]['total'], reverse=True)
        for map_name, stats in sorted_maps[:6]:
            wr_color = '#4A90D9' if stats['winrate'] >= 50 else '#e74c3c' if stats['winrate'] < 40 else '#fff'
            map_rows += f'''
            <div class="map-item">
                <span class="map-name">{map_name}</span>
                <span class="map-stats">{stats['total']}전 <span style="color: {wr_color};">{stats['winrate']}%</span></span>
            </div>
            '''
        
        # 시사점 도출
        worst_opp = min(opponents, key=lambda x: x[1]['winrate'] if x[1]['total'] >= 3 else 100) if opponents else None
        worst_map = min(by_map.items(), key=lambda x: x[1]['winrate'] if x[1]['total'] >= 3 else 100) if by_map else None
        
        insights = []
        if worst_opp and worst_opp[1]['winrate'] < 30:
            insights.append(f"특히 {worst_opp[0]} 상대 {worst_opp[1]['total']}전 {worst_opp[1]['winrate']}%로 극심한 열세")
        if worst_map and worst_map[1]['winrate'] < 30:
            insights.append(f"{worst_map[0]} 맵에서 {target}전 {worst_map[1]['total']}전 {worst_map[1]['winrate']}%로 고전")
        if not insights:
            insights.append(f"전반적으로 {target} 상대 승률 개선 필요")
        
        return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.content {{ display: flex; gap: 40px; margin-top: 30px; }}
.main-section {{ flex: 2; }}
.side-section {{ flex: 1; }}
table {{ width: 100%; border-collapse: collapse; }}
th {{ background: #2a2a2a; padding: 12px; text-align: center; font-size: 14px; border-bottom: 2px solid #e74c3c; }}
td {{ padding: 10px; text-align: center; font-size: 14px; border-bottom: 1px solid #333; }}
.card {{ background: rgba(255,255,255,0.03); border: 1px solid #333; border-radius: 10px; padding: 20px; margin-bottom: 20px; }}
.card-title {{ font-size: 18px; font-weight: 700; margin-bottom: 15px; color: #e74c3c; }}
.map-item {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #333; font-size: 14px; }}
.insight {{ margin-top: 30px; padding: 20px; background: rgba(231, 76, 60, 0.1); border-left: 4px solid #e74c3c; }}
.insight-title {{ font-size: 16px; font-weight: 700; color: #e74c3c; margin-bottom: 10px; }}
.insight-item {{ font-size: 14px; color: #aaa; margin: 5px 0; }}
</style></head>
<body>
    <div class="section-title">⚠️ vs {target} 심층 분석</div>
    <div class="description">{total}전 {winrate}% - 약점 항목 상세 분석</div>
    
    <div class="content">
        <div class="main-section">
            <div class="card">
                <div class="card-title">{target} 상대별 전적</div>
                <table>
                    <thead><tr><th>상대</th><th>경기</th><th>승</th><th>패</th><th>승률</th></tr></thead>
                    <tbody>{opp_rows}</tbody>
                </table>
            </div>
        </div>
        <div class="side-section">
            <div class="card">
                <div class="card-title">{target}전 맵별 전적</div>
                {map_rows if map_rows else '<div style="color: #666;">데이터 없음</div>'}
            </div>
            <div class="insight">
                <div class="insight-title">💡 시사점</div>
                {''.join(f'<div class="insight-item">• {i}</div>' for i in insights)}
            </div>
        </div>
    </div>
    
    <div class="footer">HMD</div>
</body></html>'''
    
    elif w_type == 'map':
        # 맵 약점 분석
        key = f'map_{target}'
        if key not in deep_data:
            return None
        
        data = deep_data[key]
        by_race = data['by_race']
        opponents = data['opponents']
        
        # 종족별 전적
        race_rows = ""
        for race in ['테란', '저그', '프로토스']:
            if race in by_race:
                stats = by_race[race]
                wr_color = '#4A90D9' if stats['winrate'] >= 50 else '#e74c3c' if stats['winrate'] < 40 else '#fff'
                race_rows += f'''
                <div class="race-item">
                    <span class="race-name">vs {race}</span>
                    <span class="race-stats">{stats['total']}전 <span style="color: {wr_color}; font-weight: 700;">{stats['winrate']}%</span></span>
                </div>
                '''
        
        # 상대별 전적
        opp_rows = ""
        for opp, stats in opponents[:8]:
            wr_color = '#4A90D9' if stats['winrate'] >= 50 else '#e74c3c' if stats['winrate'] < 40 else '#fff'
            opp_rows += f'''
            <tr>
                <td>{opp}</td>
                <td>{stats.get('race', '')}</td>
                <td>{stats['total']}</td>
                <td style="color: {wr_color}; font-weight: 700;">{stats['winrate']}%</td>
            </tr>
            '''
        
        # 시사점 도출
        insights = []
        worst_race = min(by_race.items(), key=lambda x: x[1]['winrate'] if x[1]['total'] >= 3 else 100) if by_race else None
        if worst_race and worst_race[1]['winrate'] < 40:
            insights.append(f"{target}에서 {worst_race[0]} 상대 {worst_race[1]['total']}전 {worst_race[1]['winrate']}%로 특히 고전")
        
        frequent_losses = [(o, s) for o, s in opponents if s['winrate'] < 30 and s['total'] >= 2]
        if frequent_losses:
            names = ', '.join([f[0] for f in frequent_losses[:3]])
            insights.append(f"주요 패배 상대: {names}")
        
        if not insights:
            insights.append(f"{target} 맵 전반적 전략 재검토 필요")
        
        return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.content {{ display: flex; gap: 40px; margin-top: 30px; }}
.main-section {{ flex: 1; }}
.side-section {{ flex: 1; }}
table {{ width: 100%; border-collapse: collapse; }}
th {{ background: #2a2a2a; padding: 12px; text-align: center; font-size: 14px; border-bottom: 2px solid #e74c3c; }}
td {{ padding: 10px; text-align: center; font-size: 14px; border-bottom: 1px solid #333; }}
.card {{ background: rgba(255,255,255,0.03); border: 1px solid #333; border-radius: 10px; padding: 20px; margin-bottom: 20px; }}
.card-title {{ font-size: 18px; font-weight: 700; margin-bottom: 15px; color: #e74c3c; }}
.race-item {{ display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px solid #333; font-size: 16px; }}
.insight {{ margin-top: 30px; padding: 20px; background: rgba(231, 76, 60, 0.1); border-left: 4px solid #e74c3c; }}
.insight-title {{ font-size: 16px; font-weight: 700; color: #e74c3c; margin-bottom: 10px; }}
.insight-item {{ font-size: 14px; color: #aaa; margin: 5px 0; }}
</style></head>
<body>
    <div class="section-title">⚠️ {target} 맵 심층 분석</div>
    <div class="description">{total}전 {winrate}% - 약점 항목 상세 분석</div>
    
    <div class="content">
        <div class="main-section">
            <div class="card">
                <div class="card-title">{target} 종족별 전적</div>
                {race_rows if race_rows else '<div style="color: #666;">데이터 없음</div>'}
            </div>
            <div class="insight">
                <div class="insight-title">💡 시사점</div>
                {''.join(f'<div class="insight-item">• {i}</div>' for i in insights)}
            </div>
        </div>
        <div class="side-section">
            <div class="card">
                <div class="card-title">{target} 상대별 전적</div>
                <table>
                    <thead><tr><th>상대</th><th>종족</th><th>경기</th><th>승률</th></tr></thead>
                    <tbody>{opp_rows}</tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="footer">HMD</div>
</body></html>'''
    
    return None


async def main():
    data = load_data()
    sorted_members = get_sorted_members()
    
    pages = []
    
    print("=== 심층 분석 페이지 생성 ===")
    
    for idx, m_info in enumerate(sorted_members, 1):
        member_name = m_info['name']
        analysis = get_member_deep_analysis(member_name)
        
        # 1. 티어별 비교 페이지 (경기 시점 기준) 재생성
        tier_html = gen_tier_comparison_page(member_name, analysis, idx)
        pages.append((f"03-{idx:02d}-4_{member_name}_vs_tier", tier_html))
        
        # 2. 40% 미만 약점 분석 페이지들
        weak_count = 0
        for weakness in analysis['weak_points']:
            # 가장 심각한 약점 2개만 페이지 생성
            if weak_count >= 2:
                break
            
            weak_html = gen_weakness_analysis_page(
                member_name, weakness, analysis['deep_analysis'], idx
            )
            if weak_html:
                pages.append((f"03-{idx:02d}-6_{member_name}_weakness_{weak_count+1}", weak_html))
                weak_count += 1
                print(f"  {member_name}: {weakness['type']}_{weakness['target']} ({weakness['winrate']}%) 분석 페이지 생성")
    
    print(f"\n총 {len(pages)}개 페이지 생성 중...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        for name, html in pages:
            output_path = OUTPUT_DIR / f"{name}.png"
            page = await browser.new_page(viewport={'width': WIDTH, 'height': HEIGHT})
            await page.set_content(html)
            await page.screenshot(path=str(output_path), type='png')
            await page.close()
        
        await browser.close()
    
    print("✓ 심층 분석 페이지 생성 완료!")


if __name__ == "__main__":
    asyncio.run(main())
