# -*- coding: utf-8 -*-
"""
06_generate_report.py
K University 2025 연간 분석 보고서 생성

분석 데이터를 기반으로 Markdown 형식의 보고서를 생성합니다.
- 팀 분석 보고서 (메인)
- 개인별 Booklet
- MVP 선정 섹션
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.config import OUTPUT_DIR, DATA_OUTPUT_DIR, CHARTS_DIR


def load_json(filename: str) -> dict:
    """JSON 파일 로드"""
    filepath = DATA_OUTPUT_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_percent(value: float) -> str:
    """퍼센트 포맷"""
    return f"{value:.1f}%"


def format_score(value: float) -> str:
    """점수 포맷"""
    return f"{value:.1f}"


def get_race_korean(race: str) -> str:
    """종족 한글명"""
    race_map = {
        'T': '테란', 'P': '프로토스', 'Z': '저그',
        '테란': '테란', '프로토스': '프로토스', '저그': '저그'
    }
    return race_map.get(race, race)


def generate_team_report(team_data: dict, member_data: dict, mvp_data: dict) -> str:
    """팀 분석 보고서 생성"""
    
    report = []
    
    # 헤더
    report.append("# K UNIVERSITY 2025 연간 전적 분석 보고서")
    report.append("")
    report.append(f"> 발행일: {datetime.now().strftime('%Y년 %m월 %d일')}")
    report.append("> 분석 기간: 2025년 1월 ~ 12월")
    report.append("")
    report.append("---")
    report.append("")
    
    # 1. Executive Summary
    report.append("## 1. Executive Summary")
    report.append("")
    
    overall = team_data.get('overall', {})
    total_games = overall.get('total_games', 0)
    wins = overall.get('wins', 0)
    losses = overall.get('losses', 0)
    win_rate = overall.get('win_rate', 0)
    
    report.append(f"**2025년 케이대**는 총 **{total_games:,}경기**를 치르며 ")
    report.append(f"**{wins:,}승 {losses:,}패 (승률 {format_percent(win_rate)})**의 성적을 기록했습니다.")
    report.append("")
    
    # MVP 하이라이트
    top_mvp = mvp_data['mvp_ranking'][:3]
    report.append("### 🏆 2025 MVP TOP 3")
    report.append("")
    for i, mvp in enumerate(top_mvp):
        medal = ["🥇", "🥈", "🥉"][i]
        report.append(f"{medal} **{mvp['member_name']}** - {format_score(mvp['total_score'])}점")
    report.append("")
    report.append("---")
    report.append("")
    
    # 2. 팀 전체 성적
    report.append("## 2. 팀 전체 성적 분석")
    report.append("")
    
    # 2.1 경기 유형별 성적
    report.append("### 2.1 경기 유형별 성적")
    report.append("")
    report.append("| 구분 | 경기수 | 승 | 패 | 승률 |")
    report.append("|:----:|:------:|:--:|:--:|:----:|")
    
    game_types = team_data.get('by_game_type', {})
    for gtype, stats in game_types.items():
        report.append(f"| {gtype} | {stats.get('total_games', 0):,} | {stats.get('wins', 0):,} | {stats.get('losses', 0):,} | {format_percent(stats.get('win_rate', 0))} |")
    report.append("")
    
    # 2.2 종족별 성적
    report.append("### 2.2 종족별 성적")
    report.append("")
    report.append("| 종족 | 경기수 | 승률 |")
    report.append("|:----:|:------:|:----:|")
    
    race_stats = team_data.get('by_race', {})
    for race, stats in race_stats.items():
        report.append(f"| {get_race_korean(race)} | {stats.get('total_games', 0):,} | {format_percent(stats.get('win_rate', 0))} |")
    report.append("")
    
    # 2.3 월별 추이
    report.append("### 2.3 월별 성적 추이")
    report.append("")
    report.append("| 월 | 경기수 | 승 | 패 | 승률 |")
    report.append("|:--:|:------:|:--:|:--:|:----:|")
    
    monthly = team_data.get('monthly', {})
    # 월 순서대로 정렬
    month_order = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
    for month_name in month_order:
        if month_name in monthly:
            m = monthly[month_name]
            report.append(f"| {month_name} | {m.get('total_games', 0):,} | {m.get('wins', 0):,} | {m.get('losses', 0):,} | {format_percent(m.get('win_rate', 0))} |")
    report.append("")
    
    # 2.4 티어별 분석
    report.append("### 2.4 티어별 성적 분포")
    report.append("")
    
    tier_stats = team_data.get('by_tier', {})
    if tier_stats:
        report.append("| 티어 | 경기수 | 승률 |")
        report.append("|:----:|:------:|:----:|")
        for tier, stats in tier_stats.items():
            report.append(f"| {tier} | {stats.get('total_games', 0):,} | {format_percent(stats.get('win_rate', 0))} |")
    report.append("")
    report.append("---")
    report.append("")
    
    # 3. 강점 및 약점 분석
    report.append("## 3. 2025년 강점 및 약점 분석")
    report.append("")
    
    report.append("### 3.1 강점 (Strengths)")
    report.append("")
    
    # 강점 도출
    strengths = []
    if win_rate >= 50:
        strengths.append(f"- **전체 승률 {format_percent(win_rate)}** 달성으로 긍정적인 시즌 마감")
    
    # 대회 성적이 좋은 경우
    tournament = game_types.get('대회', {})
    if tournament and tournament.get('win_rate', 0) >= 50:
        strengths.append(f"- **공식전 경쟁력**: 대회에서 {format_percent(tournament.get('win_rate', 0))} 승률")
    
    # 활발한 활동량
    # member_data는 멤버 이름이 직접 키로 되어 있음
    exclude_keys = {'all_scores', 'summary', 'metadata', 'mvp_ranking', 'evaluation_criteria'}
    member_count = len([k for k in member_data.keys() if k not in exclude_keys and isinstance(member_data.get(k), dict) and 'overall' in member_data.get(k, {})])
    avg_games_per_member = total_games / member_count if member_count > 0 else 0
    if avg_games_per_member >= 400:
        strengths.append(f"- **높은 활동량**: 멤버당 평균 {avg_games_per_member:.0f}경기로 꾸준한 활동")
    
    if not strengths:
        strengths.append("- 데이터 추가 분석 필요")
    
    report.extend(strengths)
    report.append("")
    
    report.append("### 3.2 약점 (Weaknesses)")
    report.append("")
    
    # 약점 도출
    weaknesses = []
    if win_rate < 50:
        weaknesses.append(f"- **전체 승률 부진**: {format_percent(win_rate)}로 50% 미달")
    
    # 하위 티어 방어율
    weaknesses.append("- **하위 티어 방어율 개선 필요**: 일부 멤버의 하위 상대 승률이 기대치에 미달")
    
    # 맵 적응력
    weaknesses.append("- **특정 맵 취약**: 리트머스 등 일부 맵에서 전체적으로 낮은 승률")
    
    report.extend(weaknesses)
    report.append("")
    report.append("---")
    report.append("")
    
    # 4. 2026년 성장 방향
    report.append("## 4. 2026년 성장 전략")
    report.append("")
    
    report.append("### 4.1 단기 목표 (Q1-Q2)")
    report.append("")
    report.append("1. **취약 맵 집중 연습**: 리트머스 등 낮은 승률 맵 집중 훈련")
    report.append("2. **동티어 경쟁력 강화**: 50% 미만 동티어 승률 멤버 집중 케어")
    report.append("3. **신규 멤버 적응 지원**: 활동 기간이 짧은 멤버 멘토링")
    report.append("")
    
    report.append("### 4.2 중장기 목표 (Q3-Q4)")
    report.append("")
    report.append("1. **상위 티어 도전 확대**: 티어 승격을 위한 적극적 상위 도전")
    report.append("2. **대회 성적 개선**: 대학대전 및 CK 승률 60% 이상 목표")
    report.append("3. **팀 전체 승률 55% 달성**")
    report.append("")
    report.append("---")
    report.append("")
    
    # 5. 차트 참조
    report.append("## 5. 시각화 자료")
    report.append("")
    report.append("아래 차트들은 `output/charts/` 폴더에서 확인할 수 있습니다:")
    report.append("")
    report.append("- `chart_monthly_trend.png` - 월별 성적 추이")
    report.append("- `chart_race_comparison.png` - 종족별 성적 비교")
    report.append("- `chart_member_comparison.png` - 멤버별 성적 비교")
    report.append("- `chart_matchup_heatmap.png` - 매치업 히트맵")
    report.append("- `chart_mvp_radar.png` - MVP 후보 레이더 차트")
    report.append("- `chart_mvp_ranking.png` - MVP 순위")
    report.append("")
    
    return "\n".join(report)


def generate_member_booklet(member_name: str, member_stats: dict, mvp_score: dict) -> str:
    """개인별 심층 분석 보고서 생성"""
    
    booklet = []
    
    # overall 데이터 추출
    overall = member_stats.get('overall', {})
    monthly = member_stats.get('monthly', {})
    by_tier = member_stats.get('by_tier', {})
    matchups = member_stats.get('matchups', {})
    top_maps = member_stats.get('top_maps', {})
    by_game_type = member_stats.get('by_game_type', {})
    strengths = member_stats.get('strengths_weaknesses', {})
    
    total = overall.get('total_games', 0)
    wins = overall.get('wins', 0)
    losses = overall.get('losses', 0)
    wr = overall.get('win_rate', 0)
    main_tier = overall.get('main_tier', '')
    main_race = overall.get('main_race', '')
    
    # MVP 순위 계산
    mvp_rank = "-"
    if mvp_score:
        mvp_total = mvp_score.get('total_score', 0)
    else:
        mvp_total = 0
    
    # ============================================================
    # 헤더
    # ============================================================
    booklet.append(f"# {member_name}")
    booklet.append("## 2025 연간 전적 심층 분석 보고서")
    booklet.append("")
    booklet.append(f"> 발행일: {datetime.now().strftime('%Y년 %m월 %d일')}")
    booklet.append(f"> 분석 대상: K UNIVERSITY 소속 {member_name}")
    booklet.append("")
    booklet.append("---")
    booklet.append("")
    
    # ============================================================
    # 1. Executive Summary
    # ============================================================
    booklet.append("## 1. Executive Summary")
    booklet.append("")
    booklet.append("### 1.1 기본 프로필")
    booklet.append("")
    booklet.append("| 항목 | 내용 |")
    booklet.append("|:-----|:-----|")
    booklet.append(f"| 이름 | **{member_name}** |")
    booklet.append(f"| 종족 | {get_race_korean(main_race)} |")
    booklet.append(f"| 티어 | {main_tier} |")
    booklet.append(f"| MVP 점수 | **{format_score(mvp_total)}점** |")
    booklet.append("")
    
    booklet.append("### 1.2 2025년 성적 총괄")
    booklet.append("")
    booklet.append("| 지표 | 수치 | 비고 |")
    booklet.append("|:-----|-----:|:-----|")
    booklet.append(f"| 총 경기 | **{total:,}** | 연간 |")
    booklet.append(f"| 승 | {wins:,} | |")
    booklet.append(f"| 패 | {losses:,} | |")
    booklet.append(f"| 승률 | **{format_percent(wr)}** | {'우수' if wr >= 55 else '보통' if wr >= 45 else '개선필요'} |")
    
    # 월평균 경기수
    active_months = len([m for m in monthly.values() if m.get('total_games', 0) > 0])
    if active_months > 0:
        avg_monthly = total / active_months
        booklet.append(f"| 월평균 경기 | {avg_monthly:.1f} | {active_months}개월 활동 |")
    booklet.append("")
    
    # ============================================================
    # 2. 월별 성적 추이 분석
    # ============================================================
    booklet.append("---")
    booklet.append("")
    booklet.append("## 2. 월별 성적 추이 분석")
    booklet.append("")
    
    if monthly:
        booklet.append("### 2.1 월별 상세 성적")
        booklet.append("")
        booklet.append("| 월 | 경기수 | 승 | 패 | 승률 | 추이 |")
        booklet.append("|:--:|:------:|:--:|:--:|:----:|:----:|")
        
        prev_wr = None
        monthly_sorted = sorted(monthly.items(), key=lambda x: x[1].get('month', 0))
        
        for month_name, stats in monthly_sorted:
            games = stats.get('total_games', 0)
            w = stats.get('wins', 0)
            l = stats.get('losses', 0)
            month_wr = stats.get('win_rate', 0)
            
            # 추이 표시
            if prev_wr is not None:
                if month_wr > prev_wr + 5:
                    trend = "UP"
                elif month_wr < prev_wr - 5:
                    trend = "DOWN"
                else:
                    trend = "-"
            else:
                trend = "-"
            prev_wr = month_wr
            
            booklet.append(f"| {month_name} | {games} | {w} | {l} | {format_percent(month_wr)} | {trend} |")
        booklet.append("")
        
        # 전반기 vs 후반기 분석
        booklet.append("### 2.2 시즌 전후반 비교")
        booklet.append("")
        
        first_half_games = 0
        first_half_wins = 0
        second_half_games = 0
        second_half_wins = 0
        
        for month_name, stats in monthly.items():
            month_num = stats.get('month', 0)
            if month_num <= 6:
                first_half_games += stats.get('total_games', 0)
                first_half_wins += stats.get('wins', 0)
            else:
                second_half_games += stats.get('total_games', 0)
                second_half_wins += stats.get('wins', 0)
        
        first_half_wr = (first_half_wins / first_half_games * 100) if first_half_games > 0 else 0
        second_half_wr = (second_half_wins / second_half_games * 100) if second_half_games > 0 else 0
        growth = second_half_wr - first_half_wr
        
        booklet.append("| 구분 | 경기수 | 승률 |")
        booklet.append("|:-----|:------:|:----:|")
        booklet.append(f"| 전반기 (1-6월) | {first_half_games} | {format_percent(first_half_wr)} |")
        booklet.append(f"| 후반기 (7-12월) | {second_half_games} | {format_percent(second_half_wr)} |")
        booklet.append(f"| **성장률** | - | **{'+' if growth >= 0 else ''}{growth:.1f}%p** |")
        booklet.append("")
        
        if growth >= 5:
            booklet.append("> **성장 평가**: 후반기에 뚜렷한 성장세를 보였습니다.")
        elif growth >= 0:
            booklet.append("> **성장 평가**: 안정적인 성적을 유지했습니다.")
        else:
            booklet.append("> **성장 평가**: 후반기 성적 하락이 있었습니다. 원인 분석이 필요합니다.")
        booklet.append("")
    
    # ============================================================
    # 3. 티어별 성적 분석
    # ============================================================
    booklet.append("---")
    booklet.append("")
    booklet.append("## 3. 티어별 성적 분석")
    booklet.append("")
    
    if by_tier:
        booklet.append("### 3.1 상대 티어별 성적")
        booklet.append("")
        booklet.append("| 상대 티어 | 경기수 | 승률 | 평가 |")
        booklet.append("|:---------|:------:|:----:|:----:|")
        
        # 티어 순서대로 정렬
        tier_order = ["1티어", "2티어", "3티어", "4티어", "5티어", "6티어", "7티어", "8티어", "베이비"]
        
        same_tier_wr = 0
        upper_games = 0
        upper_wins = 0
        lower_games = 0
        lower_wins = 0
        
        try:
            my_tier_idx = tier_order.index(main_tier)
        except ValueError:
            my_tier_idx = -1
        
        for tier in tier_order:
            if tier in by_tier:
                stats = by_tier[tier]
                games = stats.get('total_games', 0)
                tier_wr = stats.get('win_rate', 0)
                
                try:
                    opp_tier_idx = tier_order.index(tier)
                except ValueError:
                    opp_tier_idx = -1
                
                # 상위/동티어/하위 분류
                if my_tier_idx >= 0 and opp_tier_idx >= 0:
                    if opp_tier_idx < my_tier_idx:
                        relation = "상위"
                        upper_games += games
                        upper_wins += stats.get('wins', 0)
                    elif opp_tier_idx == my_tier_idx:
                        relation = "동티어"
                        same_tier_wr = tier_wr
                    else:
                        relation = "하위"
                        lower_games += games
                        lower_wins += stats.get('wins', 0)
                else:
                    relation = "-"
                
                # 평가
                if tier_wr >= 60:
                    eval_mark = "우수"
                elif tier_wr >= 50:
                    eval_mark = "양호"
                elif tier_wr >= 40:
                    eval_mark = "보통"
                else:
                    eval_mark = "개선필요"
                
                booklet.append(f"| {tier} ({relation}) | {games} | {format_percent(tier_wr)} | {eval_mark} |")
        booklet.append("")
        
        # 상위/하위 도전 요약
        booklet.append("### 3.2 티어 경쟁력 요약")
        booklet.append("")
        
        upper_wr = (upper_wins / upper_games * 100) if upper_games > 0 else 0
        lower_wr = (lower_wins / lower_games * 100) if lower_games > 0 else 0
        
        booklet.append("| 구분 | 경기수 | 승률 | 기대치 대비 |")
        booklet.append("|:-----|:------:|:----:|:----------:|")
        booklet.append(f"| 상위 티어 도전 | {upper_games} | {format_percent(upper_wr)} | {'초과달성' if upper_wr >= 40 else '보통' if upper_wr >= 25 else '미달'} |")
        booklet.append(f"| 동티어 경쟁 | - | {format_percent(same_tier_wr)} | {'우세' if same_tier_wr >= 55 else '균형' if same_tier_wr >= 45 else '열세'} |")
        booklet.append(f"| 하위 티어 방어 | {lower_games} | {format_percent(lower_wr)} | {'안정' if lower_wr >= 70 else '보통' if lower_wr >= 60 else '불안'} |")
        booklet.append("")
    
    # ============================================================
    # 4. 매치업 분석
    # ============================================================
    booklet.append("---")
    booklet.append("")
    booklet.append("## 4. 매치업 분석")
    booklet.append("")
    
    if matchups:
        booklet.append("### 4.1 종족별 매치업 성적")
        booklet.append("")
        
        for my_race, opp_data in matchups.items():
            booklet.append(f"**{get_race_korean(my_race)} 플레이 시:**")
            booklet.append("")
            booklet.append("| 상대 종족 | 경기수 | 승률 | 평가 |")
            booklet.append("|:---------|:------:|:----:|:----:|")
            
            best_matchup = None
            best_wr = 0
            worst_matchup = None
            worst_wr = 100
            
            for opp_race, stats in opp_data.items():
                games = stats.get('total_games', 0)
                matchup_wr = stats.get('win_rate', 0)
                
                if games >= 10:
                    if matchup_wr > best_wr:
                        best_wr = matchup_wr
                        best_matchup = opp_race
                    if matchup_wr < worst_wr:
                        worst_wr = matchup_wr
                        worst_matchup = opp_race
                
                if matchup_wr >= 55:
                    eval_mark = "강점"
                elif matchup_wr >= 45:
                    eval_mark = "균형"
                else:
                    eval_mark = "약점"
                
                booklet.append(f"| vs {get_race_korean(opp_race)} | {games} | {format_percent(matchup_wr)} | {eval_mark} |")
            booklet.append("")
            
            if best_matchup and worst_matchup:
                booklet.append(f"> 강점 매치업: **vs {get_race_korean(best_matchup)}** ({format_percent(best_wr)})")
                booklet.append(f"> 약점 매치업: **vs {get_race_korean(worst_matchup)}** ({format_percent(worst_wr)})")
                booklet.append("")
    
    # ============================================================
    # 5. 맵별 성적 분석
    # ============================================================
    booklet.append("---")
    booklet.append("")
    booklet.append("## 5. 맵별 성적 분석")
    booklet.append("")
    
    if top_maps:
        booklet.append("### 5.1 맵별 상세 성적")
        booklet.append("")
        booklet.append("| 맵 | 경기수 | 승률 | 평가 |")
        booklet.append("|:---|:------:|:----:|:----:|")
        
        # 경기수 기준 정렬
        sorted_maps = sorted(top_maps.items(), key=lambda x: x[1].get('total_games', 0), reverse=True)
        
        best_map = None
        best_map_wr = 0
        worst_map = None
        worst_map_wr = 100
        
        for map_name, stats in sorted_maps:
            games = stats.get('total_games', 0)
            map_wr = stats.get('win_rate', 0)
            
            if games >= 10:
                if map_wr > best_map_wr:
                    best_map_wr = map_wr
                    best_map = map_name
                if map_wr < worst_map_wr:
                    worst_map_wr = map_wr
                    worst_map = map_name
            
            if map_wr >= 55:
                eval_mark = "강점맵"
            elif map_wr >= 45:
                eval_mark = "-"
            else:
                eval_mark = "취약맵"
            
            booklet.append(f"| {map_name} | {games} | {format_percent(map_wr)} | {eval_mark} |")
        booklet.append("")
        
        booklet.append("### 5.2 맵 적응력 요약")
        booklet.append("")
        if best_map:
            booklet.append(f"- **최고 성적 맵**: {best_map} ({format_percent(best_map_wr)})")
        if worst_map:
            booklet.append(f"- **최저 성적 맵**: {worst_map} ({format_percent(worst_map_wr)})")
        
        # 맵 편차 분석
        map_wrs = [s.get('win_rate', 0) for s in top_maps.values() if s.get('total_games', 0) >= 10]
        if len(map_wrs) >= 2:
            wr_range = max(map_wrs) - min(map_wrs)
            if wr_range <= 15:
                booklet.append(f"- **맵 편차**: {wr_range:.1f}%p (균형 잡힌 성적)")
            elif wr_range <= 25:
                booklet.append(f"- **맵 편차**: {wr_range:.1f}%p (보통)")
            else:
                booklet.append(f"- **맵 편차**: {wr_range:.1f}%p (맵별 편차 큼, 취약맵 연습 필요)")
        booklet.append("")
    
    # ============================================================
    # 6. 경기 유형별 분석
    # ============================================================
    booklet.append("---")
    booklet.append("")
    booklet.append("## 6. 경기 유형별 분석")
    booklet.append("")
    
    if by_game_type:
        booklet.append("| 유형 | 경기수 | 승 | 패 | 승률 |")
        booklet.append("|:-----|:------:|:--:|:--:|:----:|")
        
        spon_wr = 0
        tournament_wr = 0
        
        for gtype, stats in by_game_type.items():
            games = stats.get('total_games', 0)
            w = stats.get('wins', 0)
            l = stats.get('losses', 0)
            type_wr = stats.get('win_rate', 0)
            
            if gtype == '스폰':
                spon_wr = type_wr
            elif gtype == '대회':
                tournament_wr = type_wr
            
            booklet.append(f"| {gtype} | {games} | {w} | {l} | {format_percent(type_wr)} |")
        booklet.append("")
        
        clutch = tournament_wr - spon_wr
        booklet.append(f"### 클러치력 분석")
        booklet.append("")
        booklet.append(f"- **대회 vs 스폰 승률 차이**: {'+' if clutch >= 0 else ''}{clutch:.1f}%p")
        if clutch >= 5:
            booklet.append("- **평가**: 중요한 경기에서 더 강한 집중력을 발휘합니다.")
        elif clutch >= -5:
            booklet.append("- **평가**: 경기 유형에 관계없이 일관된 성적을 보입니다.")
        else:
            booklet.append("- **평가**: 대회 압박감에서 다소 부담을 느끼는 경향이 있습니다. 멘탈 훈련이 도움이 될 수 있습니다.")
        booklet.append("")
    
    # ============================================================
    # 7. MVP 7대 지표 상세 분석
    # ============================================================
    booklet.append("---")
    booklet.append("")
    booklet.append("## 7. MVP 7대 지표 상세 분석")
    booklet.append("")
    
    if mvp_score:
        booklet.append(f"### 종합 점수: **{format_score(mvp_total)}점**")
        booklet.append("")
        
        scores = mvp_score.get('scores', {})
        
        criteria_info = [
            ('activity_consistency', '활동량 & 일관성', 15, '총 경기수, 활동 월수, 월별 일관성'),
            ('growth_rate', '성장률', 20, '시즌 초반 대비 후반 승률 개선도'),
            ('same_tier_dominance', '동티어 경쟁력', 15, '같은 티어 상대 승률 및 연승 기록'),
            ('upward_challenge', '상위 도전 정신', 15, '상위 티어 도전 빈도 및 승률'),
            ('downward_defense', '하위 방어율', 10, '하위 티어 상대 승률'),
            ('map_adaptability', '맵 적응력', 15, '다양한 맵에서의 균형 잡힌 성적'),
            ('tournament_performance', '대회 성과', 10, '공식전 클러치력')
        ]
        
        booklet.append("| 지표 | 점수 | 가중치 | 등급 |")
        booklet.append("|:-----|-----:|:------:|:----:|")
        
        for key, name, weight, desc in criteria_info:
            if key in scores:
                score_data = scores[key]
                score = score_data.get('score', 0)
                
                if score >= 80:
                    grade = "S"
                elif score >= 60:
                    grade = "A"
                elif score >= 40:
                    grade = "B"
                elif score >= 20:
                    grade = "C"
                else:
                    grade = "D"
                
                booklet.append(f"| {name} | {format_score(score)} | {weight}% | {grade} |")
        booklet.append("")
        
        # 상세 분석
        booklet.append("### 지표별 상세 분석")
        booklet.append("")
        
        for key, name, weight, desc in criteria_info:
            if key in scores:
                score_data = scores[key]
                details = score_data.get('details', {})
                score = score_data.get('score', 0)
                
                booklet.append(f"#### {name} ({format_score(score)}점)")
                booklet.append("")
                
                if key == 'activity_consistency' and 'total_games' in details:
                    booklet.append(f"- 총 경기수: {details.get('total_games', 0)}경기")
                    booklet.append(f"- 활동 월수: {details.get('active_months', 0)}개월")
                    booklet.append(f"- 월평균 경기: {details.get('avg_per_month', 0):.1f}경기")
                    
                elif key == 'growth_rate' and 'overall_growth' in details:
                    growth = details.get('overall_growth', 0)
                    booklet.append(f"- 시즌 성장률: {'+' if growth >= 0 else ''}{growth:.1f}%p")
                    booklet.append(f"- 추세 기울기: {details.get('trend_slope', 0):.2f}")
                    
                elif key == 'same_tier_dominance' and 'same_tier_wr' in details:
                    booklet.append(f"- 동티어 승률: {details.get('same_tier_wr', 0):.1f}%")
                    booklet.append(f"- 동티어 경기수: {details.get('same_tier_games', 0)}경기")
                    booklet.append(f"- 최장 연승: {details.get('max_streak', 0)}연승")
                    
                elif key == 'upward_challenge' and 'upward_games' in details:
                    booklet.append(f"- 상위 도전 횟수: {details.get('upward_games', 0)}경기")
                    booklet.append(f"- 상위 도전 승률: {details.get('upward_wr', 0):.1f}%")
                    booklet.append(f"- 도전 비율: {details.get('challenge_rate', 0):.1f}%")
                    
                elif key == 'downward_defense' and 'downward_wr' in details:
                    booklet.append(f"- 하위 방어 경기: {details.get('downward_games', 0)}경기")
                    booklet.append(f"- 하위 방어 승률: {details.get('downward_wr', 0):.1f}%")
                    booklet.append(f"- 연속 방어: {details.get('max_defense_streak', 0)}연승")
                    
                elif key == 'map_adaptability' and 'map_diversity' in details:
                    booklet.append(f"- 플레이 맵 수: {details.get('map_diversity', 0)}개")
                    booklet.append(f"- 맵 평균 승률: {details.get('avg_map_wr', 0):.1f}%")
                    booklet.append(f"- 최고맵: {details.get('best_map', '-')}")
                    booklet.append(f"- 최악맵: {details.get('worst_map', '-')}")
                    
                elif key == 'tournament_performance' and 'tournament_wr' in details:
                    booklet.append(f"- 대회 경기수: {details.get('tournament_games', 0)}경기")
                    booklet.append(f"- 대회 승률: {details.get('tournament_wr', 0):.1f}%")
                    booklet.append(f"- 클러치 팩터: {'+' if details.get('clutch_factor', 0) >= 0 else ''}{details.get('clutch_factor', 0):.1f}%p")
                
                elif 'reason' in details:
                    booklet.append(f"- {details.get('reason', '데이터 부족')}")
                
                booklet.append("")
    
    # ============================================================
    # 8. 종합 평가 및 2026년 성장 방향
    # ============================================================
    booklet.append("---")
    booklet.append("")
    booklet.append("## 8. 종합 평가 및 2026년 성장 방향")
    booklet.append("")
    
    # 강점 도출
    booklet.append("### 8.1 핵심 강점")
    booklet.append("")
    
    strengths_list = []
    
    if wr >= 60:
        strengths_list.append(f"높은 승률 ({format_percent(wr)}) - 우수한 전체 경기력")
    if total >= 500:
        strengths_list.append(f"풍부한 경험 ({total:,}경기) - 다양한 상황 대처 능력")
    if active_months >= 10:
        strengths_list.append(f"꾸준한 활동 ({active_months}개월) - 시즌 전반 일관된 참여")
    
    if mvp_score:
        scores = mvp_score.get('scores', {})
        if scores.get('upward_challenge', {}).get('score', 0) >= 80:
            strengths_list.append("도전 정신 - 상위 티어에 대한 적극적 도전")
        if scores.get('tournament_performance', {}).get('score', 0) >= 70:
            strengths_list.append("대회 집중력 - 중요한 경기에서의 강한 멘탈")
        if scores.get('map_adaptability', {}).get('score', 0) >= 70:
            strengths_list.append("맵 적응력 - 다양한 맵에서 안정적인 성적")
        if scores.get('same_tier_dominance', {}).get('score', 0) >= 80:
            strengths_list.append("동티어 지배력 - 같은 티어 내 확실한 우위")
        if scores.get('growth_rate', {}).get('score', 0) >= 60:
            strengths_list.append("성장세 - 시즌 동안 뚜렷한 발전")
    
    if strengths_list:
        for s in strengths_list:
            booklet.append(f"- **{s}**")
    else:
        booklet.append("- 분석 중인 데이터가 충분하지 않습니다.")
    booklet.append("")
    
    # 개선점 도출
    booklet.append("### 8.2 개선 필요 사항")
    booklet.append("")
    
    improvements = []
    
    if wr < 50:
        improvements.append(("승률 개선", f"현재 {format_percent(wr)} → 50% 이상 목표"))
    
    if mvp_score:
        scores = mvp_score.get('scores', {})
        if scores.get('same_tier_dominance', {}).get('score', 0) < 50:
            improvements.append(("동티어 경쟁력", "같은 티어 상대 승률 개선 필요"))
        if scores.get('downward_defense', {}).get('score', 0) < 50:
            improvements.append(("하위 방어율", "하위 티어 상대 안정적 승리 필요"))
        if scores.get('growth_rate', {}).get('score', 0) < 40:
            improvements.append(("성장 곡선", "월별 꾸준한 상승세 필요"))
        if scores.get('map_adaptability', {}).get('score', 0) < 50:
            improvements.append(("맵 적응력", "취약맵 집중 연습 필요"))
        if scores.get('tournament_performance', {}).get('score', 0) < 40:
            improvements.append(("대회 성과", "공식전 멘탈 관리 필요"))
    
    if improvements:
        for title, desc in improvements:
            booklet.append(f"- **{title}**: {desc}")
    else:
        booklet.append("- 현재 특별한 개선 사항이 없습니다. 현 수준 유지가 목표입니다.")
    booklet.append("")
    
    # 2026년 목표 제안
    booklet.append("### 8.3 2026년 목표 제안")
    booklet.append("")
    
    if wr >= 60:
        booklet.append(f"1. **승률 유지**: {format_percent(wr)} 이상 유지")
    elif wr >= 50:
        booklet.append(f"1. **승률 5%p 향상**: {format_percent(wr)} → {format_percent(wr + 5)} 목표")
    else:
        booklet.append(f"1. **승률 50% 달성**: 기본 경쟁력 확보")
    
    if worst_map:
        booklet.append(f"2. **취약맵 극복**: {worst_map} 승률 10%p 향상")
    
    if worst_matchup:
        booklet.append(f"3. **약점 매치업 개선**: vs {get_race_korean(worst_matchup)} 집중 연습")
    
    if mvp_score:
        scores = mvp_score.get('scores', {})
        if scores.get('tournament_performance', {}).get('score', 0) < 60:
            booklet.append("4. **대회 경험 축적**: 공식전 참여 확대 및 클러치력 향상")
    
    booklet.append("")
    
    # ============================================================
    # 마무리
    # ============================================================
    booklet.append("---")
    booklet.append("")
    booklet.append(f"*본 보고서는 {member_name}님의 2025년 전체 활동을 분석한 심층 자료입니다.*")
    booklet.append("")
    booklet.append(f"*발행: K UNIVERSITY 분석팀 | {datetime.now().strftime('%Y년 %m월 %d일')}*")
    
    return "\n".join(booklet)


def generate_mvp_section(mvp_data: dict) -> str:
    """MVP 선정 섹션 생성"""
    
    section = []
    
    section.append("# 2025 K UNIVERSITY MVP 선정")
    section.append("")
    section.append(f"> 발행일: {datetime.now().strftime('%Y년 %m월 %d일')}")
    section.append("")
    section.append("---")
    section.append("")
    
    # 평가 기준 설명
    section.append("## 평가 기준")
    section.append("")
    section.append("MVP는 다음 7가지 기준의 가중 합산 점수로 선정됩니다:")
    section.append("")
    section.append("| 항목 | 가중치 | 설명 |")
    section.append("|:-----|:------:|:-----|")
    section.append("| 활동량 & 일관성 | 15% | 총 경기수, 활동 월수, 월별 일관성 |")
    section.append("| 성장률 | 20% | 시즌 초반 대비 후반 승률 개선도 |")
    section.append("| 동티어 경쟁력 | 15% | 같은 티어 상대 승률 및 연승 기록 |")
    section.append("| 상위 도전 정신 | 15% | 상위 티어 도전 빈도 및 승률 |")
    section.append("| 하위 방어율 | 10% | 하위 티어 상대 승률 (기대 이상 성과) |")
    section.append("| 맵 적응력 | 15% | 다양한 맵에서의 균형 잡힌 성적 |")
    section.append("| 대회 성과 | 10% | 공식전(대학대전, CK)에서의 클러치력 |")
    section.append("")
    section.append("---")
    section.append("")
    
    # MVP 순위
    section.append("## 2025 MVP 순위")
    section.append("")
    
    ranking = mvp_data.get('mvp_ranking', [])
    
    # TOP 3 특별 표시
    if len(ranking) >= 3:
        section.append("### 🏆 TOP 3")
        section.append("")
        
        medals = ["🥇", "🥈", "🥉"]
        for i, mvp in enumerate(ranking[:3]):
            section.append(f"#### {medals[i]} {i+1}위: {mvp['member_name']} ({format_score(mvp['total_score'])}점)")
            section.append("")
            
            scores = mvp.get('scores', {})
            section.append("| 항목 | 점수 |")
            section.append("|:-----|-----:|")
            
            criteria_names = [
                ('activity_consistency', '활동량 & 일관성'),
                ('growth_rate', '성장률'),
                ('same_tier_dominance', '동티어 경쟁력'),
                ('upward_challenge', '상위 도전'),
                ('downward_defense', '하위 방어'),
                ('map_adaptability', '맵 적응력'),
                ('tournament_performance', '대회 성과')
            ]
            
            for key, name in criteria_names:
                if key in scores:
                    section.append(f"| {name} | {format_score(scores[key].get('score', 0))} |")
            section.append("")
        
        section.append("---")
        section.append("")
    
    # 전체 순위 테이블
    section.append("### 전체 순위")
    section.append("")
    section.append("| 순위 | 이름 | 종합점수 | 활동 | 성장 | 동티어 | 상위도전 | 하위방어 | 맵 | 대회 |")
    section.append("|:----:|:-----|:--------:|:----:|:----:|:------:|:--------:|:--------:|:--:|:----:|")
    
    for i, mvp in enumerate(ranking):
        name = mvp['member_name']
        total = format_score(mvp['total_score'])
        scores = mvp.get('scores', {})
        
        act = format_score(scores.get('activity_consistency', {}).get('score', 0))
        grw = format_score(scores.get('growth_rate', {}).get('score', 0))
        tier = format_score(scores.get('same_tier_dominance', {}).get('score', 0))
        up = format_score(scores.get('upward_challenge', {}).get('score', 0))
        down = format_score(scores.get('downward_defense', {}).get('score', 0))
        map_s = format_score(scores.get('map_adaptability', {}).get('score', 0))
        tourn = format_score(scores.get('tournament_performance', {}).get('score', 0))
        
        section.append(f"| {i+1} | {name} | **{total}** | {act} | {grw} | {tier} | {up} | {down} | {map_s} | {tourn} |")
    
    section.append("")
    section.append("---")
    section.append("")
    
    # MVP 선정 이유
    if ranking:
        mvp = ranking[0]
        section.append(f"## 🏆 2025 MVP: {mvp['member_name']}")
        section.append("")
        section.append(f"**{mvp['member_name']}**님이 종합 **{format_score(mvp['total_score'])}점**으로 ")
        section.append("2025년 케이대 MVP로 선정되었습니다.")
        section.append("")
        
        scores = mvp.get('scores', {})
        
        # 최고 점수 항목 찾기
        max_score = 0
        max_item = ""
        for key, data in scores.items():
            if isinstance(data, dict) and data.get('score', 0) > max_score:
                max_score = data.get('score', 0)
                max_item = key
        
        criteria_korean = {
            'activity_consistency': '활동량 & 일관성',
            'growth_rate': '성장률',
            'same_tier_dominance': '동티어 경쟁력',
            'upward_challenge': '상위 도전 정신',
            'downward_defense': '하위 방어율',
            'map_adaptability': '맵 적응력',
            'tournament_performance': '대회 성과'
        }
        
        section.append("### 선정 이유")
        section.append("")
        section.append(f"- **{criteria_korean.get(max_item, max_item)}** 부문에서 {format_score(max_score)}점으로 최고점 기록")
        
        # 80점 이상 항목
        high_scores = [(k, v['score']) for k, v in scores.items() 
                      if isinstance(v, dict) and v.get('score', 0) >= 80]
        if high_scores:
            for item, score in high_scores:
                section.append(f"- {criteria_korean.get(item, item)}: {format_score(score)}점")
        
        section.append("")
    
    return "\n".join(section)


def run_report_generation():
    """보고서 생성 실행"""
    
    print("=" * 60)
    print("K UNIVERSITY 2025 보고서 생성")
    print("=" * 60)
    print("")
    
    # 출력 폴더 생성
    reports_dir = OUTPUT_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    booklets_dir = reports_dir / "booklets"
    booklets_dir.mkdir(parents=True, exist_ok=True)
    
    # 데이터 로드
    print("[1/4] 분석 데이터 로드 중...")
    team_data = load_json("team_analysis.json")
    member_data = load_json("member_analysis.json")
    mvp_data = load_json("mvp_analysis.json")
    print("      완료!")
    print("")
    
    # 팀 보고서 생성
    print("[2/4] 팀 분석 보고서 생성 중...")
    team_report = generate_team_report(team_data, member_data, mvp_data)
    team_report_path = reports_dir / "01_팀분석_보고서.md"
    with open(team_report_path, 'w', encoding='utf-8') as f:
        f.write(team_report)
    print(f"      저장: {team_report_path}")
    print("")
    
    # MVP 섹션 생성
    print("[3/4] MVP 선정 보고서 생성 중...")
    mvp_report = generate_mvp_section(mvp_data)
    mvp_report_path = reports_dir / "02_MVP_선정.md"
    with open(mvp_report_path, 'w', encoding='utf-8') as f:
        f.write(mvp_report)
    print(f"      저장: {mvp_report_path}")
    print("")
    
    # 개인별 Booklet 생성
    print("[4/4] 개인별 Booklet 생성 중...")
    
    # member_analysis.json은 멤버 이름이 직접 키로 되어 있음
    # 'all_scores' 등 메타 필드 제외
    exclude_keys = {'all_scores', 'summary', 'metadata', 'mvp_ranking', 'evaluation_criteria'}
    members = {k: v for k, v in member_data.items() if k not in exclude_keys and isinstance(v, dict) and 'overall' in v}
    all_scores = mvp_data.get('all_scores', {})
    
    for member_name, member_stats in members.items():
        mvp_score = all_scores.get(member_name, {})
        booklet = generate_member_booklet(member_name, member_stats, mvp_score)
        
        # 파일명에서 특수문자 제거
        safe_name = member_name.replace('/', '_').replace('\\', '_')
        booklet_path = booklets_dir / f"{safe_name}_Booklet.md"
        
        with open(booklet_path, 'w', encoding='utf-8') as f:
            f.write(booklet)
        print(f"      - {member_name}")
    
    print("")
    print("=" * 60)
    print("보고서 생성 완료!")
    print("=" * 60)
    print("")
    print(f"[출력 위치]")
    print(f"  - 팀 보고서: {team_report_path}")
    print(f"  - MVP 보고서: {mvp_report_path}")
    print(f"  - 개인 Booklet: {booklets_dir}/")
    print("")
    
    return True


if __name__ == "__main__":
    success = run_report_generation()
    sys.exit(0 if success else 1)

