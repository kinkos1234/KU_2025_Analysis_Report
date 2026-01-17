#!/usr/bin/env python3
"""
K UNIVERSITY 2025 연간 보고서 이미지 생성기
- HTML 템플릿을 PNG 이미지로 변환
"""

import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# 경로 설정
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "report_data.json"
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"

TEMPLATE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# 디자인 상수
WIDTH = 1920
HEIGHT = 1080


def load_data():
    """JSON 데이터 로드"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_cover_html(data):
    """00. 표지 HTML 생성"""
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
            flex-direction: column;
            justify-content: center;
            padding: 80px 120px;
        }}
        .title {{
            font-size: 120px;
            font-weight: 900;
            letter-spacing: -2px;
            line-height: 1.1;
        }}
        .subtitle {{
            font-size: 42px;
            font-weight: 400;
            margin-top: 30px;
            color: #ccc;
        }}
        .period {{
            font-size: 32px;
            color: #888;
            margin-top: 10px;
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
    <div class="title">K UNIVERSITY</div>
    <div class="subtitle">2025년 전적 분석 보고서</div>
    <div class="period">_ JAN. ~ DEC.</div>
    <div class="footer">HMD</div>
</body>
</html>'''


def generate_summary_html(data):
    """01. 요약 페이지 HTML 생성"""
    headline = data['report_text']['headline'].replace('\n', '<br>')
    points = data['report_text']['summary_points']
    
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
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a3a 100%);
            font-family: 'Pretendard', sans-serif;
            color: #fff;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 80px 120px;
        }}
        .headline {{
            font-size: 72px;
            font-weight: 900;
            line-height: 1.2;
            margin-bottom: 60px;
            background: linear-gradient(90deg, #fff 0%, #4A90D9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .points {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .point {{
            font-size: 28px;
            font-weight: 400;
            color: #ccc;
            padding-left: 30px;
            position: relative;
        }}
        .point::before {{
            content: "•";
            position: absolute;
            left: 0;
            color: #4A90D9;
        }}
        .point strong {{
            color: #fff;
            font-weight: 600;
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
    <div class="headline">{headline}</div>
    <div class="points">
        {''.join(f'<div class="point">{p}</div>' for p in points)}
    </div>
    <div class="footer">HMD</div>
</body>
</html>'''


def generate_overall_stats_html(data):
    """02-01. 전체 전적 HTML 생성"""
    overall = data['summary']['overall']
    spon = data['summary']['by_type'].get('스폰', {'total': 0, 'winrate': 0})
    tour = data['summary']['by_type'].get('대회', {'total': 0, 'winrate': 0})
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            width: {WIDTH}px;
            height: {HEIGHT}px;
            background: #1a1a1a;
            font-family: 'Pretendard', sans-serif;
            color: #fff;
            padding: 80px 120px;
        }}
        .section-label {{
            font-size: 20px;
            color: #888;
            margin-bottom: 10px;
        }}
        .section-title {{
            font-size: 64px;
            font-weight: 900;
            margin-bottom: 30px;
        }}
        .description {{
            font-size: 24px;
            color: #aaa;
            margin-bottom: 60px;
        }}
        .stats-container {{
            display: flex;
            justify-content: space-around;
            margin-top: 40px;
        }}
        .stat-card {{
            text-align: center;
        }}
        .stat-circle {{
            width: 220px;
            height: 220px;
            border-radius: 50%;
            border: 8px solid #333;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: 0 auto 20px;
            position: relative;
        }}
        .stat-circle::before {{
            content: "";
            position: absolute;
            top: -8px;
            left: -8px;
            right: -8px;
            bottom: -8px;
            border-radius: 50%;
            border: 8px solid transparent;
            border-top-color: #4A90D9;
            transform: rotate(-45deg);
        }}
        .stat-value {{
            font-family: 'Montserrat', sans-serif;
            font-size: 48px;
            font-weight: 700;
        }}
        .stat-label {{
            font-size: 20px;
            color: #888;
            margin-top: 10px;
        }}
        .stat-detail {{
            font-size: 16px;
            color: #666;
            margin-top: 5px;
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
    <div class="section-label">전체 전적 정리</div>
    <div class="section-title">케이대 전체 전적</div>
    <div class="description">
        케이대 학생들은 2025년 1월부터 12월까지 총 {overall['total']:,}번의 경기를 진행하였으며, 이는 월 평균 {overall['total']//12:,}회 입니다.
    </div>
    
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-circle">
                <div class="stat-value">{overall['winrate']}%</div>
            </div>
            <div class="stat-label">전체 전적 승률</div>
            <div class="stat-detail">전체 {overall['total']:,}전 {overall['wins']:,}승 {overall['losses']:,}패</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-circle">
                <div class="stat-value">{spon['winrate']}%</div>
            </div>
            <div class="stat-label">전체 스폰 승률</div>
            <div class="stat-detail">전체 스폰 {spon['total']:,}전 {spon['wins']:,}승 {spon['losses']:,}패</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-circle">
                <div class="stat-value">{tour['winrate']}%</div>
            </div>
            <div class="stat-label">전체 대회 및 CK 승률</div>
            <div class="stat-detail">전체 대회 및 CK {tour['total']:,}전 {tour['wins']:,}승 {tour['losses']:,}패</div>
        </div>
    </div>
    
    <div class="footer">HMD</div>
</body>
</html>'''


def generate_monthly_chart_html(data):
    """02-02. 월별 전적 추이 HTML 생성"""
    monthly = data['monthly']
    
    # 최대값 계산
    max_games = max(m['total'] for m in monthly.values())
    
    # SVG 차트 생성
    chart_width = 1600
    chart_height = 400
    bar_width = 80
    gap = 50
    start_x = 80
    
    bars_svg = ""
    line_points = []
    
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    
    for i, (month_num, stats) in enumerate(sorted(monthly.items(), key=lambda x: int(x[0]))):
        x = start_x + i * (bar_width + gap)
        bar_height = (stats['total'] / max_games) * 300 if max_games > 0 else 0
        y = chart_height - bar_height - 50
        
        # 막대 그래프
        bars_svg += f'''
        <rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" 
              fill="url(#barGradient)" rx="4"/>
        <text x="{x + bar_width/2}" y="{y - 15}" text-anchor="middle" 
              fill="#fff" font-size="16" font-weight="bold">{stats['total']}</text>
        <text x="{x + bar_width/2}" y="{chart_height - 20}" text-anchor="middle" 
              fill="#888" font-size="14">{months[i]}</text>
        '''
        
        # 승률 라인
        wr_y = chart_height - 50 - (stats['winrate'] / 100) * 300
        line_points.append(f"{x + bar_width/2},{wr_y}")
        bars_svg += f'''
        <circle cx="{x + bar_width/2}" cy="{wr_y}" r="8" fill="#4A90D9" stroke="#fff" stroke-width="2"/>
        <text x="{x + bar_width/2}" y="{wr_y - 15}" text-anchor="middle" 
              fill="#4A90D9" font-size="14">{stats['winrate']}%</text>
        '''
    
    line_path = f'<polyline points="{" ".join(line_points)}" fill="none" stroke="#4A90D9" stroke-width="2"/>'
    
    avg_games = sum(m['total'] for m in monthly.values()) // 12
    max_month = max(monthly.items(), key=lambda x: x[1]['total'])
    min_month = min(monthly.items(), key=lambda x: x[1]['total'])
    avg_wr = sum(m['winrate'] for m in monthly.values()) / 12
    max_wr = max(monthly.items(), key=lambda x: x[1]['winrate'])
    min_wr = min(monthly.items(), key=lambda x: x[1]['winrate'])
    
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
            padding: 80px 120px;
        }}
        .section-title {{
            font-size: 64px;
            font-weight: 900;
            margin-bottom: 20px;
        }}
        .description {{
            font-size: 22px;
            color: #aaa;
            margin-bottom: 10px;
        }}
        .chart-container {{
            margin-top: 40px;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #888;
        }}
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
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
        .y-axis {{
            position: absolute;
            right: 100px;
            top: 200px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 300px;
            color: #4A90D9;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="section-title">월별 전체 전적 추이</div>
    <div class="description">월 평균 {avg_games}회 게임 진행 (최대 {max_month[1]['total']}회, 최소 {min_month[1]['total']}회)</div>
    <div class="description">승률 평균 {avg_wr:.2f}% (최고 {max_wr[1]['winrate']}%, 최저 {min_wr[1]['winrate']}%)</div>
    
    <div class="chart-container">
        <svg width="{chart_width}" height="{chart_height + 50}">
            <defs>
                <linearGradient id="barGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#555"/>
                    <stop offset="100%" style="stop-color:#333"/>
                </linearGradient>
            </defs>
            {line_path}
            {bars_svg}
        </svg>
    </div>
    
    <div class="legend">
        <div class="legend-item">
            <div class="legend-dot" style="background: #444;"></div>
            <span>경기 수 추이</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background: #4A90D9;"></div>
            <span>승률 추이</span>
        </div>
    </div>
    
    <div class="y-axis">
        <span>100%</span>
        <span>75%</span>
        <span>50%</span>
        <span>25%</span>
        <span>0%</span>
    </div>
    
    <div class="footer">HMD</div>
</body>
</html>'''


def generate_member_profile_html(data, member_name):
    """멤버 프로필 페이지 HTML 생성"""
    member = data['member_details'][member_name]
    overall = member['overall']
    spon = member['by_type'].get('스폰', {'total': 0, 'wins': 0, 'losses': 0, 'winrate': 0})
    tour = member['by_type'].get('대회', {'total': 0, 'wins': 0, 'losses': 0, 'winrate': 0})
    
    tier_display = member['tier_end']
    if member['tier_start'] != member['tier_end']:
        tier_display = f"{member['tier_start']} → {member['tier_end']}"
    
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
            padding: 80px 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .profile-container {{
            display: flex;
            align-items: center;
            gap: 100px;
        }}
        .profile-image {{
            width: 400px;
            height: 500px;
            background: linear-gradient(135deg, #333 0%, #222 100%);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 120px;
            color: #555;
        }}
        .profile-info {{
            flex: 1;
        }}
        .member-name {{
            font-size: 80px;
            font-weight: 900;
            margin-bottom: 10px;
        }}
        .member-meta {{
            font-size: 32px;
            color: #888;
            margin-bottom: 50px;
        }}
        .stats-box {{
            background: rgba(255,255,255,0.05);
            border: 1px solid #333;
            border-radius: 10px;
            padding: 30px 40px;
        }}
        .stats-title {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 20px;
        }}
        .stats-row {{
            font-size: 22px;
            color: #ccc;
            margin-bottom: 12px;
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
    <div class="profile-container">
        <div class="profile-image">👤</div>
        <div class="profile-info">
            <div class="member-name">{member_name}</div>
            <div class="member-meta">{tier_display} {member['race']}</div>
            
            <div class="stats-box">
                <div class="stats-title">전적 요약</div>
                <div class="stats-row">전체 {overall['total']}전 {overall['wins']}승 {overall['losses']}패 {overall['winrate']}%</div>
                <div class="stats-row">스폰 {spon['total']}전 {spon['wins']}승 {spon['losses']}패 {spon['winrate']}%</div>
                <div class="stats-row">대회 및 CK {tour['total']}전 {tour['wins']}승 {tour['losses']}패 {tour['winrate']}%</div>
            </div>
        </div>
    </div>
    <div class="footer">HMD</div>
</body>
</html>'''


def generate_rankings_html(data):
    """07-02. 우수 학생 평가 점수표 HTML 생성"""
    rankings = data['rankings']
    
    rows_html = ""
    for r in rankings:
        highlight = 'style="color: #4A90D9; font-weight: 700;"' if r['rank'] == 1 else ''
        rows_html += f'''
        <tr {highlight}>
            <td>{r['name']}</td>
            <td>{r['monthly_avg']}</td>
            <td>{r['overall_winrate']}</td>
            <td>{r['top_tier_games']}</td>
            <td>{r['same_tier_winrate']}</td>
            <td>{r['tournament_winrate']}</td>
            <td>{r['growth']}</td>
            <td>{r['total_score']}</td>
            <td>{r['rank']}</td>
        </tr>
        '''
    
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
            padding: 60px 100px;
        }}
        .section-title {{
            font-size: 56px;
            font-weight: 900;
            margin-bottom: 40px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #2a2a2a;
            padding: 16px 12px;
            text-align: center;
            font-size: 16px;
            font-weight: 600;
            border-bottom: 2px solid #4A90D9;
        }}
        td {{
            padding: 14px 12px;
            text-align: center;
            font-size: 15px;
            border-bottom: 1px solid #333;
        }}
        tr:hover {{
            background: rgba(74, 144, 217, 0.1);
        }}
        .footer {{
            position: absolute;
            bottom: 40px;
            right: 100px;
            left: 100px;
            border-top: 1px solid #444;
            padding-top: 15px;
            text-align: right;
            font-size: 20px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="section-title">우수 학생 평가 점수</div>
    
    <table>
        <thead>
            <tr>
                <th>닉네임</th>
                <th>월평균 경기수</th>
                <th>전체 승률</th>
                <th>상위 경기수</th>
                <th>동일 승률</th>
                <th>대회 승률</th>
                <th>성장폭</th>
                <th>총점</th>
                <th>순위</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    
    <div class="footer">HMD</div>
</body>
</html>'''


def generate_ending_html():
    """09. E.O.D 엔딩 HTML 생성"""
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
            background: linear-gradient(180deg, #0a1628 0%, #1a2a3a 100%);
            font-family: 'Pretendard', sans-serif;
            color: #fff;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        .logo {{
            font-size: 200px;
            font-weight: 900;
            letter-spacing: 20px;
            background: linear-gradient(180deg, #fff 0%, #88a8c8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 60px rgba(136, 168, 200, 0.3);
        }}
        .star {{
            font-size: 40px;
            margin-bottom: 20px;
            color: #4A90D9;
        }}
        .eod {{
            position: absolute;
            bottom: 100px;
            right: 150px;
            font-size: 36px;
            font-weight: 700;
            color: #fff;
        }}
    </style>
</head>
<body>
    <div class="star">★</div>
    <div class="logo">KU</div>
    <div class="eod">E.O.D</div>
</body>
</html>'''


async def render_html_to_png(html_content, output_path):
    """HTML을 PNG로 렌더링"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': WIDTH, 'height': HEIGHT})
        await page.set_content(html_content)
        await page.screenshot(path=str(output_path), type='png')
        await browser.close()


async def generate_all_pages(data):
    """모든 페이지 생성"""
    pages = []
    
    # 00. 표지
    pages.append(("00_cover", generate_cover_html(data)))
    
    # 01. 요약
    pages.append(("01_summary", generate_summary_html(data)))
    
    # 02-01. 전체 전적
    pages.append(("02-01_overall", generate_overall_stats_html(data)))
    
    # 02-02. 월별 추이
    pages.append(("02-02_monthly", generate_monthly_chart_html(data)))
    
    # 07-02. 평가 점수표
    pages.append(("07-02_rankings", generate_rankings_html(data)))
    
    # 멤버별 프로필 (상위 5명만 우선 생성)
    top_members = ['규리야', '정서린', '냥수디', '내가먼지', '슬돌이']
    for i, member in enumerate(top_members):
        if member in data['member_details']:
            pages.append((f"03-{i+1:02d}_{member}_profile", generate_member_profile_html(data, member)))
    
    # 09. E.O.D
    pages.append(("09_eod", generate_ending_html()))
    
    # 렌더링
    print(f"\n총 {len(pages)}개 페이지 렌더링 시작...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        for name, html in pages:
            output_path = OUTPUT_DIR / f"{name}.png"
            page = await browser.new_page(viewport={'width': WIDTH, 'height': HEIGHT})
            await page.set_content(html)
            await page.screenshot(path=str(output_path), type='png')
            await page.close()
            print(f"  ✓ {name}.png 생성 완료")
        
        await browser.close()
    
    print(f"\n모든 페이지 생성 완료! 출력 폴더: {OUTPUT_DIR}")


def main():
    print("K UNIVERSITY 2025 연간 보고서 생성 시작...")
    data = load_data()
    asyncio.run(generate_all_pages(data))


if __name__ == "__main__":
    main()
