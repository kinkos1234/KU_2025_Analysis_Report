# -*- coding: utf-8 -*-
"""
멤버별 세부 분석 모듈
- 15명 전원의 개별 전적 분석
- 종족별/티어별/맵별/월별 세부 분석
- 강점/약점 파악
- 성장 곡선 분석
"""

import pandas as pd
import json
from pathlib import Path
import sys

# config 모듈 임포트
sys.path.append(str(Path(__file__).parent))
from config import *

class MemberAnalyzer:
    def __init__(self, data_path, members_path):
        self.data_path = data_path
        self.members_path = members_path
        self.df = None
        self.members = []
        self.results = {}
    
    def load_data(self):
        """데이터 및 멤버 목록 로드"""
        print("데이터 로드 중...")
        self.df = pd.read_csv(self.data_path, encoding='utf-8-sig')
        self.df[COL_DATE] = pd.to_datetime(self.df[COL_DATE])
        self.df['month'] = self.df[COL_DATE].dt.month
        
        # 멤버 목록 로드 (오타 방지)
        with open(self.members_path, 'r', encoding='utf-8') as f:
            members_data = json.load(f)
            self.members = members_data['members']
        
        print(f"[OK] 데이터 로드: {len(self.df)}건")
        print(f"[OK] 멤버 목록: {len(self.members)}명")
        print(f"  -> {', '.join(self.members)}")
        
        return self.df
    
    def analyze_member_overall(self, member_name):
        """멤버 전체 통계"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        if len(member_df) == 0:
            return None
        
        total = len(member_df)
        wins = len(member_df[member_df[COL_RESULT] == RESULT_WIN])
        win_rate = (wins / total * 100) if total > 0 else 0
        
        # 주 종족 (가장 많이 플레이한 종족)
        main_race = member_df[COL_MEMBER_RACE].mode()[0] if len(member_df) > 0 else "N/A"
        
        # 주 티어 (가장 많이 플레이한 티어)
        main_tier = member_df[COL_MEMBER_TIER].mode()[0] if len(member_df) > 0 else "N/A"
        
        return {
            "name": member_name,
            "main_race": main_race,
            "main_tier": main_tier,
            "total_games": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": round(win_rate, 2)
        }
    
    def analyze_member_by_race(self, member_name):
        """멤버 종족별 분석"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        race_stats = {}
        for race in RACES:
            race_df = member_df[member_df[COL_MEMBER_RACE] == race]
            if len(race_df) == 0:
                continue
            
            total = len(race_df)
            wins = len(race_df[race_df[COL_RESULT] == RESULT_WIN])
            win_rate = (wins / total * 100) if total > 0 else 0
            
            race_stats[race] = {
                "total_games": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": round(win_rate, 2)
            }
        
        return race_stats
    
    def analyze_member_by_tier(self, member_name):
        """멤버 티어별 분석"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        tier_stats = {}
        for tier in TIER_ORDER:
            tier_df = member_df[member_df[COL_MEMBER_TIER] == tier]
            if len(tier_df) == 0:
                continue
            
            total = len(tier_df)
            wins = len(tier_df[tier_df[COL_RESULT] == RESULT_WIN])
            win_rate = (wins / total * 100) if total > 0 else 0
            
            tier_stats[tier] = {
                "total_games": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": round(win_rate, 2)
            }
        
        return tier_stats
    
    def analyze_member_by_game_type(self, member_name):
        """멤버 경기 유형별 분석"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        type_stats = {}
        for game_type in ANALYSIS_GAME_TYPES:
            type_df = member_df[member_df[COL_TYPE] == game_type]
            if len(type_df) == 0:
                continue
            
            total = len(type_df)
            wins = len(type_df[type_df[COL_RESULT] == RESULT_WIN])
            win_rate = (wins / total * 100) if total > 0 else 0
            
            type_stats[game_type] = {
                "total_games": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": round(win_rate, 2)
            }
        
        return type_stats
    
    def analyze_member_monthly(self, member_name):
        """멤버 월별 추이"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        monthly_stats = {}
        for month in range(1, 13):
            month_df = member_df[member_df['month'] == month]
            if len(month_df) == 0:
                continue
            
            total = len(month_df)
            wins = len(month_df[month_df[COL_RESULT] == RESULT_WIN])
            win_rate = (wins / total * 100) if total > 0 else 0
            
            monthly_stats[f"{month}월"] = {
                "month": month,
                "total_games": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": round(win_rate, 2)
            }
        
        return monthly_stats
    
    def analyze_member_matchups(self, member_name):
        """멤버 종족 상성 분석 (아군 종족 vs 상대 종족)"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        matchup_stats = {}
        for our_race in RACES:
            our_race_df = member_df[member_df[COL_MEMBER_RACE] == our_race]
            if len(our_race_df) == 0:
                continue
            
            matchup_stats[our_race] = {}
            
            for opp_race in RACES:
                matchup_df = our_race_df[our_race_df[COL_OPPONENT_RACE] == opp_race]
                
                if len(matchup_df) == 0:
                    continue
                
                total = len(matchup_df)
                wins = len(matchup_df[matchup_df[COL_RESULT] == RESULT_WIN])
                win_rate = (wins / total * 100) if total > 0 else 0
                
                matchup_stats[our_race][opp_race] = {
                    "total_games": total,
                    "wins": wins,
                    "losses": total - wins,
                    "win_rate": round(win_rate, 2)
                }
        
        return matchup_stats
    
    def analyze_member_maps(self, member_name, top_n=10):
        """멤버 맵별 분석 (상위 N개)"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        # 맵별 경기 수 계산
        map_counts = member_df[COL_MAP].value_counts()
        top_maps = map_counts.head(top_n).index.tolist()
        
        map_stats = {}
        for map_name in top_maps:
            map_df = member_df[member_df[COL_MAP] == map_name]
            
            total = len(map_df)
            wins = len(map_df[map_df[COL_RESULT] == RESULT_WIN])
            win_rate = (wins / total * 100) if total > 0 else 0
            
            map_stats[map_name] = {
                "total_games": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": round(win_rate, 2)
            }
        
        return map_stats
    
    def analyze_member_strengths_weaknesses(self, member_name):
        """멤버 강점/약점 분석"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        if len(member_df) < 10:  # 경기 수가 너무 적으면 분석 불가
            return None
        
        # 종족별 승률
        race_stats = self.analyze_member_by_race(member_name)
        best_race = max(race_stats.items(), key=lambda x: x[1]['win_rate']) if race_stats else None
        worst_race = min(race_stats.items(), key=lambda x: x[1]['win_rate']) if race_stats else None
        
        # 맵별 승률 (경기 수 5개 이상)
        all_maps = {}
        for map_name in member_df[COL_MAP].unique():
            map_df = member_df[member_df[COL_MAP] == map_name]
            if len(map_df) >= 5:
                total = len(map_df)
                wins = len(map_df[map_df[COL_RESULT] == RESULT_WIN])
                win_rate = (wins / total * 100) if total > 0 else 0
                all_maps[map_name] = {
                    "total_games": total,
                    "win_rate": round(win_rate, 2)
                }
        
        best_map = max(all_maps.items(), key=lambda x: x[1]['win_rate']) if all_maps else None
        worst_map = min(all_maps.items(), key=lambda x: x[1]['win_rate']) if all_maps else None
        
        return {
            "best_race": {
                "race": best_race[0],
                "win_rate": best_race[1]['win_rate'],
                "games": best_race[1]['total_games']
            } if best_race else None,
            "worst_race": {
                "race": worst_race[0],
                "win_rate": worst_race[1]['win_rate'],
                "games": worst_race[1]['total_games']
            } if worst_race else None,
            "best_map": {
                "map": best_map[0],
                "win_rate": best_map[1]['win_rate'],
                "games": best_map[1]['total_games']
            } if best_map else None,
            "worst_map": {
                "map": worst_map[0],
                "win_rate": worst_map[1]['win_rate'],
                "games": worst_map[1]['total_games']
            } if worst_map else None
        }
    
    def analyze_member_growth(self, member_name):
        """멤버 성장 분석 (전반기 vs 후반기)"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        if len(member_df) < 20:
            return None
        
        # 전반기 (Q1-Q2: 1~6월)
        first_half = member_df[member_df['month'] <= 6]
        # 후반기 (Q3-Q4: 7~12월)
        second_half = member_df[member_df['month'] >= 7]
        
        if len(first_half) == 0 or len(second_half) == 0:
            return None
        
        first_wr = (len(first_half[first_half[COL_RESULT] == RESULT_WIN]) / len(first_half) * 100)
        second_wr = (len(second_half[second_half[COL_RESULT] == RESULT_WIN]) / len(second_half) * 100)
        
        growth = second_wr - first_wr
        
        return {
            "first_half": {
                "games": len(first_half),
                "win_rate": round(first_wr, 2)
            },
            "second_half": {
                "games": len(second_half),
                "win_rate": round(second_wr, 2)
            },
            "growth": round(growth, 2),
            "trend": "상승" if growth > 0 else "하락" if growth < 0 else "유지"
        }
    
    def analyze_member(self, member_name):
        """멤버 종합 분석"""
        print(f"\n[{member_name}] 분석 중...")
        
        overall = self.analyze_member_overall(member_name)
        if overall is None:
            print(f"  경고: {member_name} 데이터 없음")
            return None
        
        by_race = self.analyze_member_by_race(member_name)
        by_tier = self.analyze_member_by_tier(member_name)
        by_game_type = self.analyze_member_by_game_type(member_name)
        monthly = self.analyze_member_monthly(member_name)
        matchups = self.analyze_member_matchups(member_name)
        maps = self.analyze_member_maps(member_name, top_n=10)
        strengths = self.analyze_member_strengths_weaknesses(member_name)
        growth = self.analyze_member_growth(member_name)
        
        print(f"  [OK] {overall['total_games']}경기, 승률 {overall['win_rate']}%")
        
        return {
            "overall": overall,
            "by_race": by_race,
            "by_tier": by_tier,
            "by_game_type": by_game_type,
            "monthly": monthly,
            "matchups": matchups,
            "top_maps": maps,
            "strengths_weaknesses": strengths,
            "growth": growth
        }
    
    def run_analysis(self):
        """전체 멤버 분석 실행"""
        print("=" * 80)
        print("멤버별 분석 시작")
        print("=" * 80)
        
        self.load_data()
        
        for member in self.members:
            member_result = self.analyze_member(member)
            if member_result:
                self.results[member] = member_result
        
        print("\n" + "=" * 80)
        print(f"[SUCCESS] 멤버별 분석 완료: {len(self.results)}명")
        print("=" * 80)
        
        return self.results
    
    def save_results(self, output_path):
        """분석 결과 저장"""
        ensure_dirs()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n분석 결과 저장: {output_path}")
    
    def print_summary(self):
        """분석 결과 요약 출력"""
        print("\n" + "=" * 80)
        print("멤버별 분석 결과 요약")
        print("=" * 80)
        
        # 승률 순 정렬
        sorted_members = sorted(
            self.results.items(),
            key=lambda x: x[1]['overall']['win_rate'],
            reverse=True
        )
        
        print("\n[승률 순위 (경기 수 50경기 이상)]")
        rank = 1
        for member_name, data in sorted_members:
            if data['overall']['total_games'] >= 50:
                overall = data['overall']
                print(f"  {rank}. {member_name}: {overall['win_rate']}% "
                      f"({overall['wins']}승 {overall['losses']}패, {overall['total_games']}경기)")
                rank += 1
        
        # 경기 수 순
        print("\n[경기 수 순위]")
        sorted_by_games = sorted(
            self.results.items(),
            key=lambda x: x[1]['overall']['total_games'],
            reverse=True
        )
        for i, (member_name, data) in enumerate(sorted_by_games[:10], 1):
            print(f"  {i}. {member_name}: {data['overall']['total_games']}경기")
        
        # 가장 성장한 멤버
        print("\n[성장률 상위 (전반기 → 후반기)]")
        growth_members = [
            (name, data) for name, data in self.results.items()
            if data.get('growth') is not None and data['growth']['growth'] > 0
        ]
        sorted_growth = sorted(
            growth_members,
            key=lambda x: x[1]['growth']['growth'],
            reverse=True
        )
        for i, (member_name, data) in enumerate(sorted_growth[:5], 1):
            growth = data['growth']
            print(f"  {i}. {member_name}: {growth['first_half']['win_rate']}% → "
                  f"{growth['second_half']['win_rate']}% (+{growth['growth']}%p)")


if __name__ == "__main__":
    # 분석 실행
    validated_csv = get_output_path("validated_data.csv")
    members_json = get_output_path("member_names.json")
    
    analyzer = MemberAnalyzer(validated_csv, members_json)
    results = analyzer.run_analysis()
    
    # 결과 저장
    output_file = get_output_path("member_analysis.json")
    analyzer.save_results(output_file)
    
    # 요약 출력
    analyzer.print_summary()
    
    print("\n[SUCCESS] 멤버별 분석 완료")

