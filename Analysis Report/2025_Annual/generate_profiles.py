#!/usr/bin/env python3
"""
멤버 프로필 페이지 생성 (14명 전원)
"""

import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "report_data.json"
OUTPUT_DIR = BASE_DIR / "output"

WIDTH = 1920
HEIGHT = 1080


def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def gen_member_profile(data, member_name, rank):
    """멤버 프로필 페이지 HTML 생성"""
    member = data['member_details'][member_name]
    overall = member['overall']
    spon = member['by_type'].get('스폰', {'total': 0, 'wins': 0, 'losses': 0, 'winrate': 0})
    tour = member['by_type'].get('대회', {'total': 0, 'wins': 0, 'losses': 0, 'winrate': 0})
    
    tier_display = member['tier_end']
    if member['tier_start'] != member['tier_end']:
        tier_display = f"{member['tier_start']} → {member['tier_end']}"
    
    # 종족별 색상
    race_colors = {
        '테란': '#4A90D9',
        '저그': '#9B59B6',
        '프로토스': '#F1C40F'
    }
    race_color = race_colors.get(member['race'], '#4A90D9')
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            width: {WIDTH}px;
            height: {HEIGHT}px;
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
            width: 350px;
            height: 450px;
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
        .member-name {{
            font-size: 48px;
            font-weight: 900;
            margin-bottom: 10px;
        }}
        .member-meta {{
            font-size: 24px;
            color: {race_color};
        }}
        .right {{
            flex: 1;
            padding: 80px 80px 80px 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .section-label {{
            font-size: 18px;
            color: #888;
            margin-bottom: 10px;
        }}
        .stats-box {{
            background: rgba(255,255,255,0.03);
            border: 1px solid #333;
            border-radius: 15px;
            padding: 35px 45px;
            margin-bottom: 30px;
        }}
        .stats-title {{
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 25px;
            color: {race_color};
        }}
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
    </style>
</head>
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
            {''.join(f"""
            <div class="stats-row">
                <span class="stats-label">vs {race}</span>
                <span class="stats-value">{member['vs_race'].get(race, {}).get('total', 0)}전 {member['vs_race'].get(race, {}).get('winrate', 0)}%</span>
            </div>
            """ for race in ['테란', '저그', '프로토스'] if member['vs_race'].get(race))}
        </div>
    </div>
    
    <div class="footer">HMD</div>
</body>
</html>'''


async def generate_all_profiles(data):
    """모든 멤버 프로필 생성"""
    # 경기수 순으로 정렬
    members_sorted = sorted(
        data['member_details'].items(),
        key=lambda x: x[1]['overall']['total'],
        reverse=True
    )
    
    print(f"총 {len(members_sorted)}명 멤버 프로필 생성...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        for idx, (member_name, _) in enumerate(members_sorted, 1):
            html = gen_member_profile(data, member_name, idx)
            output_path = OUTPUT_DIR / f"03-{idx:02d}_00_{member_name}_profile.png"
            
            page = await browser.new_page(viewport={'width': WIDTH, 'height': HEIGHT})
            await page.set_content(html)
            await page.screenshot(path=str(output_path), type='png')
            await page.close()
            print(f"  ✓ 03-{idx:02d}_00_{member_name}_profile.png")
        
        await browser.close()
    
    print("\n프로필 생성 완료!")


def main():
    data = load_data()
    asyncio.run(generate_all_profiles(data))


if __name__ == "__main__":
    main()
