#!/usr/bin/env python3
"""
K UNIVERSITY 2025 연간 보고서 - POTY & 타임라인 섹션 생성
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
.section-title { font-size: 64px; font-weight: 900; margin-bottom: 30px; }
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


def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================
# 07. PLAYER OF THE YEAR
# ============================================================

def gen_07_intro(data):
    """07. POTY 인트로"""
    mvp = data['summary']['highlights']['mvp']
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    width: {WIDTH}px;
    height: {HEIGHT}px;
    background: linear-gradient(135deg, #1a1a1a 0%, #0a1628 100%);
    font-family: 'Pretendard', sans-serif;
    color: #fff;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px 120px;
}}
.title {{
    font-size: 48px;
    font-weight: 300;
    margin-bottom: 20px;
}}
.subtitle {{
    font-size: 96px;
    font-weight: 900;
    line-height: 1.1;
}}
.highlight {{ color: #4A90D9; }}
.info {{
    margin-top: 60px;
    font-size: 28px;
    color: #888;
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
    <div class="title">PLAYER</div>
    <div class="subtitle">OF THE<br><span class="highlight">YEAR</span></div>
    <div class="info">2025년을 빛낸 최고의 학생들</div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_07_01_criteria(data):
    """07-01. 평가 기준 설명"""
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.criteria-list {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 30px;
    margin-top: 50px;
}}
.criteria-card {{
    background: rgba(255,255,255,0.03);
    border: 1px solid #333;
    border-radius: 15px;
    padding: 35px;
}}
.criteria-name {{
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 15px;
    color: #4A90D9;
}}
.criteria-desc {{
    font-size: 16px;
    color: #aaa;
    line-height: 1.6;
}}
.criteria-weight {{
    font-size: 14px;
    color: #666;
    margin-top: 15px;
}}
</style></head>
<body>
    <div class="section-title">우수 학생 평가 기준</div>
    <div class="description">2025년 연간 성적을 기반으로 종합 평가 점수를 산출합니다.</div>
    
    <div class="criteria-list">
        <div class="criteria-card">
            <div class="criteria-name">월평균 경기수</div>
            <div class="criteria-desc">한 해 동안 얼마나 꾸준히 활동했는지 평가합니다. 활발한 참여도를 중요시합니다.</div>
            <div class="criteria-weight">가중치: ×1.0</div>
        </div>
        <div class="criteria-card">
            <div class="criteria-name">전체 승률</div>
            <div class="criteria-desc">전체 경기의 승률입니다. 기본적인 실력 지표로 활용됩니다.</div>
            <div class="criteria-weight">가중치: ×1.5</div>
        </div>
        <div class="criteria-card">
            <div class="criteria-name">상위 티어 경기수</div>
            <div class="criteria-desc">1~4티어 상대와의 경기 횟수입니다. 강자와의 대전 경험을 평가합니다.</div>
            <div class="criteria-weight">가중치: ×0.1</div>
        </div>
        <div class="criteria-card">
            <div class="criteria-name">동일 티어 승률</div>
            <div class="criteria-desc">같은 티어 상대와의 승률입니다. 동등한 상대와의 경쟁력을 평가합니다.</div>
            <div class="criteria-weight">가중치: ×1.0</div>
        </div>
        <div class="criteria-card">
            <div class="criteria-name">대회 승률</div>
            <div class="criteria-desc">대회 및 CK에서의 승률입니다. 중요한 경기에서의 멘탈과 실력을 평가합니다.</div>
            <div class="criteria-weight">가중치: ×1.5</div>
        </div>
        <div class="criteria-card">
            <div class="criteria-name">성장폭</div>
            <div class="criteria-desc">티어 상승 단계 수입니다. 한 해 동안의 성장을 높이 평가합니다.</div>
            <div class="criteria-weight">가중치: ×50</div>
        </div>
    </div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_07_03_mvp(data):
    """07-03. MVP 선정"""
    mvp_name = data['summary']['highlights']['mvp']['name']
    member = data['member_details'][mvp_name]
    overall = member['overall']
    ranking = next((r for r in data['rankings'] if r['name'] == mvp_name), {})
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
body {{
    background: linear-gradient(135deg, #1a1a1a 0%, #1a2a3a 100%);
    display: flex;
    padding: 0;
}}
.left {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px;
}}
.right {{
    flex: 1;
    background: rgba(74, 144, 217, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
}}
.award {{ font-size: 28px; color: #4A90D9; margin-bottom: 20px; }}
.name {{ font-size: 80px; font-weight: 900; margin-bottom: 10px; }}
.meta {{ font-size: 28px; color: #888; margin-bottom: 40px; }}
.stats {{ margin-top: 30px; }}
.stat-row {{
    display: flex;
    justify-content: space-between;
    padding: 15px 0;
    border-bottom: 1px solid #333;
    font-size: 20px;
}}
.stat-label {{ color: #888; }}
.stat-value {{ font-weight: 700; color: #4A90D9; }}
.profile-placeholder {{
    width: 400px;
    height: 500px;
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 150px;
    color: #4A90D9;
}}
</style></head>
<body>
    <div class="left">
        <div class="award">🏆 MVP - Most Valuable Player</div>
        <div class="name">{mvp_name}</div>
        <div class="meta">{member['tier_end']} {member['race']}</div>
        
        <div class="stats">
            <div class="stat-row">
                <span class="stat-label">전체 전적</span>
                <span class="stat-value">{overall['total']}전 {overall['wins']}승 {overall['losses']}패</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">전체 승률</span>
                <span class="stat-value">{overall['winrate']}%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">대회 승률</span>
                <span class="stat-value">{ranking.get('tournament_winrate', 0)}%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">동일 티어 승률</span>
                <span class="stat-value">{ranking.get('same_tier_winrate', 0)}%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">종합 순위</span>
                <span class="stat-value">{ranking.get('rank', 0)}위 (총점 {ranking.get('total_score', 0)})</span>
            </div>
        </div>
    </div>
    <div class="right">
        <div class="profile-placeholder">👑</div>
    </div>
</body></html>'''


def gen_07_04_mip(data):
    """07-04. MIP 선정"""
    if 'mip' not in data['summary']['highlights']:
        return None
    
    mip_info = data['summary']['highlights']['mip']
    mip_name = mip_info['name']
    member = data['member_details'][mip_name]
    overall = member['overall']
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
body {{
    background: linear-gradient(135deg, #1a1a1a 0%, #2a1a2a 100%);
    display: flex;
    padding: 0;
}}
.left {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px;
}}
.right {{
    flex: 1;
    background: rgba(147, 112, 219, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
}}
.award {{ font-size: 28px; color: #9370DB; margin-bottom: 20px; }}
.name {{ font-size: 80px; font-weight: 900; margin-bottom: 10px; }}
.meta {{ font-size: 28px; color: #888; margin-bottom: 40px; }}
.growth-box {{
    background: rgba(147, 112, 219, 0.2);
    border-radius: 15px;
    padding: 30px;
    margin-top: 30px;
}}
.growth-title {{ font-size: 20px; color: #9370DB; margin-bottom: 15px; }}
.growth-content {{
    display: flex;
    align-items: center;
    gap: 30px;
    font-size: 36px;
    font-weight: 700;
}}
.growth-arrow {{ color: #9370DB; font-size: 48px; }}
.stats {{ margin-top: 30px; }}
.stat-row {{
    display: flex;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #333;
    font-size: 18px;
}}
.stat-label {{ color: #888; }}
.stat-value {{ font-weight: 700; color: #9370DB; }}
.profile-placeholder {{
    width: 400px;
    height: 500px;
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 150px;
    color: #9370DB;
}}
</style></head>
<body>
    <div class="left">
        <div class="award">📈 MIP - Most Improved Player</div>
        <div class="name">{mip_name}</div>
        <div class="meta">{member['tier_end']} {member['race']}</div>
        
        <div class="growth-box">
            <div class="growth-title">연간 성장</div>
            <div class="growth-content">
                <span>{mip_info['tier_start']}</span>
                <span class="growth-arrow">→</span>
                <span>{mip_info['tier_end']}</span>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-row">
                <span class="stat-label">전체 전적</span>
                <span class="stat-value">{overall['total']}전 {overall['wins']}승 {overall['losses']}패</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">전체 승률</span>
                <span class="stat-value">{overall['winrate']}%</span>
            </div>
        </div>
    </div>
    <div class="right">
        <div class="profile-placeholder">🚀</div>
    </div>
</body></html>'''


def gen_07_05_ironman(data):
    """07-05. 철인상 선정"""
    iron = data['summary']['highlights']['most_games']
    iron_name = iron['name']
    member = data['member_details'][iron_name]
    overall = member['overall']
    ranking = next((r for r in data['rankings'] if r['name'] == iron_name), {})
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
body {{
    background: linear-gradient(135deg, #1a1a1a 0%, #1a2a1a 100%);
    display: flex;
    padding: 0;
}}
.left {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px;
}}
.right {{
    flex: 1;
    background: rgba(46, 204, 113, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
}}
.award {{ font-size: 28px; color: #2ecc71; margin-bottom: 20px; }}
.name {{ font-size: 80px; font-weight: 900; margin-bottom: 10px; }}
.meta {{ font-size: 28px; color: #888; margin-bottom: 40px; }}
.games-box {{
    background: rgba(46, 204, 113, 0.2);
    border-radius: 15px;
    padding: 30px;
    text-align: center;
    margin-top: 30px;
}}
.games-number {{
    font-size: 72px;
    font-weight: 900;
    color: #2ecc71;
}}
.games-label {{ font-size: 20px; color: #888; }}
.stats {{ margin-top: 30px; }}
.stat-row {{
    display: flex;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #333;
    font-size: 18px;
}}
.stat-label {{ color: #888; }}
.stat-value {{ font-weight: 700; color: #2ecc71; }}
.profile-placeholder {{
    width: 400px;
    height: 500px;
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 150px;
    color: #2ecc71;
}}
</style></head>
<body>
    <div class="left">
        <div class="award">🏃 철인상 - Ironman Award</div>
        <div class="name">{iron_name}</div>
        <div class="meta">{member['tier_end']} {member['race']}</div>
        
        <div class="games-box">
            <div class="games-number">{iron['total']}</div>
            <div class="games-label">총 경기 수 (최다 출전)</div>
        </div>
        
        <div class="stats">
            <div class="stat-row">
                <span class="stat-label">월평균 경기수</span>
                <span class="stat-value">{ranking.get('monthly_avg', 0)}회</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">전체 승률</span>
                <span class="stat-value">{overall['winrate']}%</span>
            </div>
        </div>
    </div>
    <div class="right">
        <div class="profile-placeholder">💪</div>
    </div>
</body></html>'''


# ============================================================
# 08. 타임라인
# ============================================================

def gen_08_01_monthly_events(data):
    """08-01. 월별 주요 이벤트"""
    monthly = data['monthly']
    
    timeline_html = ""
    months_kr = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
    
    for i in range(1, 13):
        stats = monthly.get(i, monthly.get(str(i), {}))
        if not stats:
            continue
        
        wr = stats.get('winrate', 0)
        color = '#4A90D9' if wr >= 55 else '#e74c3c' if wr < 50 else '#888'
        
        timeline_html += f'''
        <div class="month-item">
            <div class="month-name">{months_kr[i-1]}</div>
            <div class="month-dot" style="background: {color};"></div>
            <div class="month-stats">
                <span class="games">{stats.get('total', 0)}경기</span>
                <span class="wr" style="color: {color};">{wr}%</span>
            </div>
        </div>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.timeline {{
    display: flex;
    justify-content: space-between;
    margin-top: 80px;
    position: relative;
}}
.timeline::before {{
    content: "";
    position: absolute;
    top: 35px;
    left: 0;
    right: 0;
    height: 4px;
    background: #333;
}}
.month-item {{
    text-align: center;
    position: relative;
    z-index: 1;
}}
.month-name {{
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 15px;
}}
.month-dot {{
    width: 20px;
    height: 20px;
    border-radius: 50%;
    margin: 0 auto 15px;
    border: 4px solid #1a1a1a;
}}
.month-stats {{
    display: flex;
    flex-direction: column;
    gap: 5px;
}}
.games {{ font-size: 14px; color: #888; }}
.wr {{ font-size: 16px; font-weight: 700; }}
</style></head>
<body>
    <div class="section-title">월별 성적 타임라인</div>
    <div class="description">2025년 1월부터 12월까지 월별 성적 추이</div>
    
    <div class="timeline">{timeline_html}</div>
    <div class="footer">HMD</div>
</body></html>'''


def gen_08_02_tier_changes(data):
    """08-02. 멤버 티어 변동 연표"""
    members = data['member_details']
    
    changes = []
    for name, info in members.items():
        if info['tier_start'] != info['tier_end']:
            changes.append({
                'name': name,
                'race': info['race'],
                'start': info['tier_start'],
                'end': info['tier_end']
            })
    
    rows_html = ""
    for c in changes:
        rows_html += f'''
        <div class="change-row">
            <div class="member-info">
                <span class="member-name">{c['name']}</span>
                <span class="member-race">{c['race']}</span>
            </div>
            <div class="tier-change">
                <span class="tier-start">{c['start']}</span>
                <span class="arrow">→</span>
                <span class="tier-end">{c['end']}</span>
            </div>
        </div>
        '''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
{COMMON_STYLE}
.changes-list {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-top: 50px;
}}
.change-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 25px 30px;
    background: rgba(255,255,255,0.03);
    border: 1px solid #333;
    border-radius: 12px;
}}
.member-info {{ display: flex; flex-direction: column; gap: 5px; }}
.member-name {{ font-size: 22px; font-weight: 700; }}
.member-race {{ font-size: 16px; color: #888; }}
.tier-change {{
    display: flex;
    align-items: center;
    gap: 15px;
    font-size: 20px;
}}
.tier-start {{ color: #888; }}
.arrow {{ color: #4A90D9; font-size: 24px; }}
.tier-end {{ color: #4A90D9; font-weight: 700; }}
</style></head>
<body>
    <div class="section-title">멤버 티어 변동 연표</div>
    <div class="description">2025년 한 해 동안 티어가 변동된 멤버들</div>
    
    <div class="changes-list">{rows_html}</div>
    <div class="footer">HMD</div>
</body></html>'''


async def generate_final(data):
    """POTY & 타임라인 페이지 생성"""
    pages = [
        ("07_poty_intro", gen_07_intro(data)),
        ("07-01_criteria", gen_07_01_criteria(data)),
        ("07-03_mvp", gen_07_03_mvp(data)),
        ("07-04_mip", gen_07_04_mip(data)),
        ("07-05_ironman", gen_07_05_ironman(data)),
        ("08-01_monthly_timeline", gen_08_01_monthly_events(data)),
        ("08-02_tier_changes", gen_08_02_tier_changes(data)),
    ]
    
    # None 제거
    pages = [(n, h) for n, h in pages if h is not None]
    
    print(f"\n총 {len(pages)}개 페이지 렌더링...")
    
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
    
    print(f"\n완료! 출력: {OUTPUT_DIR}")


def main():
    print("POTY & 타임라인 섹션 생성...")
    data = load_data()
    asyncio.run(generate_final(data))


if __name__ == "__main__":
    main()
