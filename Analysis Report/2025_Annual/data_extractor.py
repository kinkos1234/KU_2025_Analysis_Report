#!/usr/bin/env python3
"""
K UNIVERSITY 2025 연간 보고서 데이터 추출 스크립트
- 2025-01-01 ~ 2025-12-31 데이터 분석
- JSON 형식으로 모든 분석 데이터 추출
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
EXCEL_PATH = BASE_DIR / "ku_records.xlsx"
OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data():
    """2025년 데이터 로드 및 필터링"""
    df = pd.read_excel(EXCEL_PATH)
    df_2025 = df[(df['날짜'] >= '2025-01-01') & (df['날짜'] <= '2025-12-31')].copy()
    df_2025['월'] = df_2025['날짜'].dt.month
    df_2025['분기'] = df_2025['날짜'].dt.quarter
    df_2025['요일'] = df_2025['날짜'].dt.dayofweek
    return df_2025


def calc_winrate(data):
    """승률 계산"""
    if len(data) == 0:
        return {"total": 0, "wins": 0, "losses": 0, "winrate": 0.0}
    wins = (data['결과'] == '승').sum()
    total = len(data)
    losses = total - wins
    winrate = round(wins / total * 100, 2)
    return {"total": int(total), "wins": int(wins), "losses": int(losses), "winrate": float(winrate)}


def extract_summary(df):
    """요약 데이터 추출"""
    summary = {
        "period": {
            "start": "2025-01-01",
            "end": "2025-12-31",
            "months": 12
        },
        "overall": calc_winrate(df),
        "by_type": {},
        "members": {
            "total": df['멤버 이름'].nunique(),
            "list": df['멤버 이름'].unique().tolist()
        },
        "highlights": {}
    }
    
    # 구분별 전적
    for cat in df['구분2'].unique():
        cat_data = df[df['구분2'] == cat]
        summary["by_type"][cat] = calc_winrate(cat_data)
    
    # 하이라이트 계산
    member_stats = []
    for member in df['멤버 이름'].unique():
        m_data = df[df['멤버 이름'] == member]
        stats = calc_winrate(m_data)
        stats['name'] = member
        stats['race'] = m_data['멤버 종족'].iloc[0]
        stats['tier_start'] = m_data.iloc[0]['멤버 티어']
        stats['tier_end'] = m_data.iloc[-1]['멤버 티어']
        member_stats.append(stats)
    
    # MVP (최고 승률, 100경기 이상)
    qualified = [m for m in member_stats if m['total'] >= 100]
    mvp = max(qualified, key=lambda x: x['winrate'])
    summary["highlights"]["mvp"] = {
        "name": mvp['name'],
        "winrate": mvp['winrate'],
        "total": mvp['total']
    }
    
    # 최다 출전
    most_games = max(member_stats, key=lambda x: x['total'])
    summary["highlights"]["most_games"] = {
        "name": most_games['name'],
        "total": most_games['total']
    }
    
    # MIP (Most Improved - 티어 상승)
    tier_order = {'1티어': 1, '2티어': 2, '3티어': 3, '4티어': 4, '5티어': 5, 
                  '6티어': 6, '7티어': 7, '8티어': 8, '베이비': 9}
    improved = []
    for m in member_stats:
        start = tier_order.get(m['tier_start'], 10)
        end = tier_order.get(m['tier_end'], 10)
        improvement = start - end  # 숫자가 작을수록 높은 티어
        if improvement > 0:
            improved.append({**m, 'improvement': improvement})
    
    if improved:
        mip = max(improved, key=lambda x: x['improvement'])
        summary["highlights"]["mip"] = {
            "name": mip['name'],
            "tier_start": mip['tier_start'],
            "tier_end": mip['tier_end'],
            "improvement": mip['improvement']
        }
    
    return summary


def extract_monthly(df):
    """월별 전적 추출"""
    monthly = {}
    for month in range(1, 13):
        m_data = df[df['월'] == month]
        monthly[month] = calc_winrate(m_data)
    return monthly


def extract_quarterly(df):
    """분기별 전적 추출"""
    quarterly = {}
    for q in range(1, 5):
        q_data = df[df['분기'] == q]
        quarterly[f"Q{q}"] = calc_winrate(q_data)
    return quarterly


def extract_race_stats(df):
    """종족별 전적 추출"""
    race_stats = {
        "member_race": {},
        "opponent_race": {},
        "matchups": {}
    }
    
    # 멤버 종족별
    for race in ['테란', '저그', '프로토스']:
        race_data = df[df['멤버 종족'] == race]
        race_stats["member_race"][race] = calc_winrate(race_data)
    
    # 상대 종족별
    for race in ['테란', '저그', '프로토스']:
        race_data = df[df['상대 종족'] == race]
        race_stats["opponent_race"][race] = calc_winrate(race_data)
    
    # 매치업별
    for my_race in ['테란', '저그', '프로토스']:
        for opp_race in ['테란', '저그', '프로토스']:
            matchup_data = df[(df['멤버 종족'] == my_race) & (df['상대 종족'] == opp_race)]
            key = f"{my_race[0]}v{opp_race[0]}"
            race_stats["matchups"][key] = {
                **calc_winrate(matchup_data),
                "member_race": my_race,
                "opponent_race": opp_race
            }
    
    return race_stats


def extract_map_stats(df):
    """맵별 전적 추출"""
    map_stats = {}
    for map_name in df['맵'].value_counts().index:
        map_data = df[df['맵'] == map_name]
        stats = calc_winrate(map_data)
        
        # 맵-종족 교차
        by_race = {}
        for race in ['테란', '저그', '프로토스']:
            race_data = map_data[map_data['멤버 종족'] == race]
            if len(race_data) > 0:
                by_race[race] = calc_winrate(race_data)
        
        map_stats[map_name] = {
            **stats,
            "by_member_race": by_race
        }
    
    return map_stats


def extract_opponent_stats(df):
    """상대별 전적 추출"""
    opponent_stats = {
        "by_tier": {},
        "top_opponents": []
    }
    
    # 티어별
    tier_order = ['1티어', '2티어', '3티어', '4티어', '5티어', '6티어', '7티어', '8티어', '베이비']
    for tier in tier_order:
        tier_data = df[df['상대 티어'] == tier]
        if len(tier_data) > 0:
            opponent_stats["by_tier"][tier] = calc_winrate(tier_data)
    
    # 상위 상대 (30경기 이상)
    opp_counts = df['상대'].value_counts()
    for opp in opp_counts[opp_counts >= 30].index:
        opp_data = df[df['상대'] == opp]
        stats = calc_winrate(opp_data)
        stats['name'] = opp
        stats['race'] = opp_data['상대 종족'].iloc[0]
        stats['tier'] = opp_data['상대 티어'].iloc[-1]
        opponent_stats["top_opponents"].append(stats)
    
    # 승률순 정렬
    opponent_stats["top_opponents"].sort(key=lambda x: x['total'], reverse=True)
    
    return opponent_stats


def extract_tournament_stats(df):
    """대회별 전적 추출"""
    tour_data = df[df['구분2'] == '대회']
    tournament_stats = {
        "overall": calc_winrate(tour_data),
        "by_tournament": {},
        "by_member": []
    }
    
    # 대회별
    for tour in tour_data['구분'].value_counts().index:
        t_data = tour_data[tour_data['구분'] == tour]
        tournament_stats["by_tournament"][tour] = calc_winrate(t_data)
    
    # 멤버별 대회 성적
    for member in df['멤버 이름'].unique():
        m_tour = tour_data[tour_data['멤버 이름'] == member]
        if len(m_tour) > 0:
            stats = calc_winrate(m_tour)
            stats['name'] = member
            tournament_stats["by_member"].append(stats)
    
    tournament_stats["by_member"].sort(key=lambda x: x['total'], reverse=True)
    
    return tournament_stats


def extract_member_details(df):
    """멤버별 상세 데이터 추출"""
    members = {}
    
    for member in df['멤버 이름'].unique():
        m_data = df[df['멤버 이름'] == member]
        
        member_info = {
            "name": member,
            "race": m_data['멤버 종족'].iloc[0],
            "tier_start": m_data.iloc[0]['멤버 티어'],
            "tier_end": m_data.iloc[-1]['멤버 티어'],
            "overall": calc_winrate(m_data),
            "by_type": {},
            "monthly": {},
            "quarterly": {},
            "vs_race": {},
            "by_map": {},
            "vs_tier": {},
            "top_opponents": []
        }
        
        # 타입별
        for cat in ['스폰', '대회']:
            cat_data = m_data[m_data['구분2'] == cat]
            if len(cat_data) > 0:
                member_info["by_type"][cat] = calc_winrate(cat_data)
        
        # 월별
        for month in range(1, 13):
            month_data = m_data[m_data['월'] == month]
            if len(month_data) > 0:
                member_info["monthly"][month] = calc_winrate(month_data)
        
        # 분기별
        for q in range(1, 5):
            q_data = m_data[m_data['분기'] == q]
            if len(q_data) > 0:
                member_info["quarterly"][f"Q{q}"] = calc_winrate(q_data)
        
        # 상대 종족별
        for race in ['테란', '저그', '프로토스']:
            race_data = m_data[m_data['상대 종족'] == race]
            if len(race_data) > 0:
                member_info["vs_race"][race] = calc_winrate(race_data)
        
        # 맵별
        for map_name in m_data['맵'].value_counts().head(10).index:
            map_data = m_data[m_data['맵'] == map_name]
            member_info["by_map"][map_name] = calc_winrate(map_data)
        
        # 상대 티어별
        tier_order = ['1티어', '2티어', '3티어', '4티어', '5티어', '6티어', '7티어', '8티어', '베이비']
        for tier in tier_order:
            tier_data = m_data[m_data['상대 티어'] == tier]
            if len(tier_data) > 0:
                member_info["vs_tier"][tier] = calc_winrate(tier_data)
        
        # 주요 상대 (10경기 이상)
        opp_counts = m_data['상대'].value_counts()
        for opp in opp_counts[opp_counts >= 10].index:
            opp_data = m_data[m_data['상대'] == opp]
            stats = calc_winrate(opp_data)
            stats['name'] = opp
            stats['race'] = opp_data['상대 종족'].iloc[0]
            stats['tier'] = opp_data['상대 티어'].iloc[-1]
            member_info["top_opponents"].append(stats)
        
        member_info["top_opponents"].sort(key=lambda x: x['total'], reverse=True)
        members[member] = member_info
    
    return members


def extract_player_rankings(df):
    """우수 학생 평가 점수 계산"""
    rankings = []
    
    for member in df['멤버 이름'].unique():
        m_data = df[df['멤버 이름'] == member]
        
        # 기본 지표
        monthly_avg = len(m_data) / 12  # 월평균 경기수
        overall = calc_winrate(m_data)
        
        # 상위 티어 경기 (1~4티어 상대)
        top_tier = m_data[m_data['상대 티어'].isin(['1티어', '2티어', '3티어', '4티어'])]
        top_tier_stats = calc_winrate(top_tier)
        
        # 동일 티어 경기
        member_tier = m_data.iloc[-1]['멤버 티어']
        same_tier = m_data[m_data['상대 티어'] == member_tier]
        same_tier_stats = calc_winrate(same_tier)
        
        # 대회 성적
        tour_data = m_data[m_data['구분2'] == '대회']
        tour_stats = calc_winrate(tour_data)
        
        # 성장폭 계산
        tier_order = {'1티어': 1, '2티어': 2, '3티어': 3, '4티어': 4, '5티어': 5, 
                      '6티어': 6, '7티어': 7, '8티어': 8, '베이비': 9}
        tier_start = m_data.iloc[0]['멤버 티어']
        tier_end = m_data.iloc[-1]['멤버 티어']
        growth = tier_order.get(tier_start, 10) - tier_order.get(tier_end, 10)
        
        # 점수 계산 (가중치 적용)
        score = (
            monthly_avg * 1.0 +                    # 월평균 경기수
            overall['winrate'] * 1.5 +             # 전체 승률
            top_tier_stats['total'] * 0.1 +        # 상위 경기수
            same_tier_stats['winrate'] * 1.0 +     # 동일 티어 승률
            tour_stats['winrate'] * 1.5 +          # 대회 승률
            growth * 50                             # 성장폭
        )
        
        rankings.append({
            "name": member,
            "race": m_data['멤버 종족'].iloc[0],
            "tier": tier_end,
            "monthly_avg": round(monthly_avg, 1),
            "overall_winrate": overall['winrate'],
            "top_tier_games": top_tier_stats['total'],
            "top_tier_winrate": top_tier_stats['winrate'],
            "same_tier_games": same_tier_stats['total'],
            "same_tier_winrate": same_tier_stats['winrate'],
            "tournament_games": tour_stats['total'],
            "tournament_winrate": tour_stats['winrate'],
            "growth": growth,
            "tier_start": tier_start,
            "tier_end": tier_end,
            "total_score": round(score, 1)
        })
    
    rankings.sort(key=lambda x: x['total_score'], reverse=True)
    for i, r in enumerate(rankings):
        r['rank'] = i + 1
    
    return rankings


def generate_report_text(summary, monthly, quarterly):
    """보고서 요약 문장 생성"""
    overall = summary['overall']
    mvp = summary['highlights']['mvp']
    most_games = summary['highlights']['most_games']
    
    # 최고/최저 월 찾기
    best_month = max(monthly.items(), key=lambda x: x[1]['winrate'] if x[1]['total'] > 0 else 0)
    worst_month = min(monthly.items(), key=lambda x: x[1]['winrate'] if x[1]['total'] > 50 else 100)
    
    # 최고/최저 분기
    best_quarter = max(quarterly.items(), key=lambda x: x[1]['winrate'])
    
    texts = {
        "headline": f"대회 승률 {summary['by_type'].get('대회', {}).get('winrate', 0)}%\n우리의 2025년을 돌아보다",
        "summary_points": [
            f"2025년 한 해 동안 케이대 학생들은 총 {overall['total']:,}경기를 치렀습니다.",
            f"전체 승률 {overall['winrate']}%, {overall['wins']:,}승 {overall['losses']:,}패를 기록했습니다.",
            f"{best_quarter[0]} 시즌에 {best_quarter[1]['winrate']}%로 가장 높은 승률을 달성했습니다.",
            f"{best_month[0]}월에는 {best_month[1]['winrate']}%로 연중 최고 승률을 기록했습니다.",
            f"MVP {mvp['name']}은 {mvp['winrate']}%의 압도적인 승률을 보여주었습니다.",
            f"철인 {most_games['name']}은 {most_games['total']:,}경기로 최다 출전했습니다."
        ]
    }
    
    if 'mip' in summary['highlights']:
        mip = summary['highlights']['mip']
        texts["summary_points"].append(
            f"MIP {mip['name']}은 {mip['tier_start']}에서 {mip['tier_end']}까지 성장했습니다."
        )
    
    return texts


def main():
    print("K UNIVERSITY 2025 연간 보고서 데이터 추출 시작...")
    
    # 데이터 로드
    df = load_data()
    print(f"총 {len(df):,}개 경기 데이터 로드 완료")
    
    # 각 섹션별 데이터 추출
    print("요약 데이터 추출 중...")
    summary = extract_summary(df)
    
    print("월별/분기별 데이터 추출 중...")
    monthly = extract_monthly(df)
    quarterly = extract_quarterly(df)
    
    print("종족 데이터 추출 중...")
    race_stats = extract_race_stats(df)
    
    print("맵 데이터 추출 중...")
    map_stats = extract_map_stats(df)
    
    print("상대 데이터 추출 중...")
    opponent_stats = extract_opponent_stats(df)
    
    print("대회 데이터 추출 중...")
    tournament_stats = extract_tournament_stats(df)
    
    print("멤버별 상세 데이터 추출 중...")
    member_details = extract_member_details(df)
    
    print("평가 점수 계산 중...")
    rankings = extract_player_rankings(df)
    
    print("보고서 텍스트 생성 중...")
    report_text = generate_report_text(summary, monthly, quarterly)
    
    # 전체 데이터 통합
    all_data = {
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
        "monthly": monthly,
        "quarterly": quarterly,
        "race_stats": race_stats,
        "map_stats": map_stats,
        "opponent_stats": opponent_stats,
        "tournament_stats": tournament_stats,
        "member_details": member_details,
        "rankings": rankings,
        "report_text": report_text
    }
    
    # JSON 파일로 저장
    output_file = OUTPUT_DIR / "report_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n데이터 추출 완료: {output_file}")
    
    # 요약 출력
    print("\n" + "="*50)
    print("2025년 연간 보고서 데이터 요약")
    print("="*50)
    print(f"총 경기 수: {summary['overall']['total']:,}전")
    print(f"전체 승률: {summary['overall']['winrate']}%")
    print(f"멤버 수: {summary['members']['total']}명")
    print(f"MVP: {summary['highlights']['mvp']['name']} ({summary['highlights']['mvp']['winrate']}%)")
    print(f"철인상: {summary['highlights']['most_games']['name']} ({summary['highlights']['most_games']['total']}경기)")
    if 'mip' in summary['highlights']:
        print(f"MIP: {summary['highlights']['mip']['name']} ({summary['highlights']['mip']['tier_start']}→{summary['highlights']['mip']['tier_end']})")
    
    return all_data


if __name__ == "__main__":
    main()
