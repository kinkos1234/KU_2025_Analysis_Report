# -*- coding: utf-8 -*-
"""
팀 전체 분석 모듈
- 전체 통계
- 월별/분기별 추이
- 종족별 분석
- 티어별 분석
- 경기 유형별 분석
- 맵별 분석
"""

import pandas as pd
import json
from pathlib import Path
import sys

# config 모듈 임포트
sys.path.append(str(Path(__file__).parent))
from config import *

class TeamAnalyzer:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.results = {
            "overall": {},
            "monthly": {},
            "quarterly": {},
            "by_race": {},
            "by_tier": {},
            "by_game_type": {},
            "by_map": {},
            "matchups": {}
        }
    
    def load_data(self):
        """검증된 데이터 로드"""
        print("검증된 데이터 로드 중...")
        self.df = pd.read_csv(self.data_path, encoding='utf-8-sig')
        self.df[COL_DATE] = pd.to_datetime(self.df[COL_DATE])
        self.df['month'] = self.df[COL_DATE].dt.month
        self.df['quarter'] = self.df[COL_DATE].dt.quarter
        print(f"[OK] 데이터 로드 완료: {len(self.df)}건")
        return self.df
    
    def analyze_overall(self):
        """전체 통계"""
        print("\n전체 통계 분석 중...")
        
        total = len(self.df)
        wins = len(self.df[self.df[COL_RESULT] == RESULT_WIN])
        losses = len(self.df[self.df[COL_RESULT] == RESULT_LOSE])
        win_rate = (wins / total * 100) if total > 0 else 0
        
        self.results["overall"] = {
            "total_games": total,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "date_start": self.df[COL_DATE].min().strftime("%Y-%m-%d"),
            "date_end": self.df[COL_DATE].max().strftime("%Y-%m-%d")
        }
        
        print(f"[OK] 전체 {total}경기, 승률 {win_rate:.2f}%")
    
    def analyze_monthly(self):
        """월별 분석"""
        print("\n월별 추이 분석 중...")
        
        monthly_data = {}
        for month in range(1, 13):
            month_df = self.df[self.df['month'] == month]
            if len(month_df) == 0:
                continue
            
            total = len(month_df)
            wins = len(month_df[month_df[COL_RESULT] == RESULT_WIN])
            win_rate = (wins / total * 100) if total > 0 else 0
            
            monthly_data[f"{month}월"] = {
                "month": month,
                "total_games": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": round(win_rate, 2)
            }
        
        self.results["monthly"] = monthly_data
        print(f"[OK] {len(monthly_data)}개월 데이터 분석 완료")
    
    def analyze_quarterly(self):
        """분기별 분석"""
        print("\n분기별 분석 중...")
        
        quarterly_data = {}
        for q in range(1, 5):
            q_df = self.df[self.df['quarter'] == q]
            if len(q_df) == 0:
                continue
            
            total = len(q_df)
            wins = len(q_df[q_df[COL_RESULT] == RESULT_WIN])
            win_rate = (wins / total * 100) if total > 0 else 0
            
            quarterly_data[f"Q{q}"] = {
                "quarter": q,
                "total_games": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": round(win_rate, 2)
            }
        
        self.results["quarterly"] = quarterly_data
        print(f"[OK] {len(quarterly_data)}개 분기 분석 완료")
    
    def analyze_by_race(self):
        """종족별 분석"""
        print("\n종족별 분석 중...")
        
        race_data = {}
        for race in RACES:
            race_df = self.df[self.df[COL_MEMBER_RACE] == race]
            if len(race_df) == 0:
                continue
            
            total = len(race_df)
            wins = len(race_df[race_df[COL_RESULT] == RESULT_WIN])
            win_rate = (wins / total * 100) if total > 0 else 0
            
            race_data[race] = {
                "total_games": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": round(win_rate, 2)
            }
        
        self.results["by_race"] = race_data
        print(f"[OK] 종족별 분석 완료: {list(race_data.keys())}")
    
    def analyze_by_tier(self):
        """티어별 분석"""
        print("\n티어별 분석 중...")
        
        tier_data = {}
        for tier in TIER_ORDER:
            tier_df = self.df[self.df[COL_MEMBER_TIER] == tier]
            if len(tier_df) == 0:
                continue
            
            total = len(tier_df)
            wins = len(tier_df[tier_df[COL_RESULT] == RESULT_WIN])
            win_rate = (wins / total * 100) if total > 0 else 0
            
            tier_data[tier] = {
                "total_games": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": round(win_rate, 2)
            }
        
        self.results["by_tier"] = tier_data
        print(f"[OK] 티어별 분석 완료: {len(tier_data)}개 티어")
    
    def analyze_by_game_type(self):
        """경기 유형별 분석"""
        print("\n경기 유형별 분석 중...")
        
        type_data = {}
        for game_type in ANALYSIS_GAME_TYPES:
            type_df = self.df[self.df[COL_TYPE] == game_type]
            if len(type_df) == 0:
                continue
            
            total = len(type_df)
            wins = len(type_df[type_df[COL_RESULT] == RESULT_WIN])
            win_rate = (wins / total * 100) if total > 0 else 0
            
            type_data[game_type] = {
                "total_games": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": round(win_rate, 2)
            }
        
        self.results["by_game_type"] = type_data
        print(f"[OK] 경기 유형별 분석 완료")
    
    def analyze_by_map(self):
        """맵별 분석 (경기 수 상위 20개)"""
        print("\n맵별 분석 중...")
        
        # 맵별 경기 수 계산
        map_counts = self.df[COL_MAP].value_counts()
        top_maps = map_counts.head(20).index.tolist()
        
        map_data = {}
        for map_name in top_maps:
            map_df = self.df[self.df[COL_MAP] == map_name]
            
            total = len(map_df)
            wins = len(map_df[map_df[COL_RESULT] == RESULT_WIN])
            win_rate = (wins / total * 100) if total > 0 else 0
            
            map_data[map_name] = {
                "total_games": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": round(win_rate, 2)
            }
        
        self.results["by_map"] = map_data
        print(f"[OK] 맵별 분석 완료: 상위 {len(map_data)}개 맵")
    
    def analyze_matchups(self):
        """종족 상성 분석 (아군 종족 vs 상대 종족)"""
        print("\n종족 상성 분석 중...")
        
        matchup_data = {}
        for our_race in RACES:
            matchup_data[our_race] = {}
            
            for opp_race in RACES:
                matchup_df = self.df[
                    (self.df[COL_MEMBER_RACE] == our_race) &
                    (self.df[COL_OPPONENT_RACE] == opp_race)
                ]
                
                if len(matchup_df) == 0:
                    matchup_data[our_race][opp_race] = {
                        "total_games": 0,
                        "wins": 0,
                        "losses": 0,
                        "win_rate": 0
                    }
                    continue
                
                total = len(matchup_df)
                wins = len(matchup_df[matchup_df[COL_RESULT] == RESULT_WIN])
                win_rate = (wins / total * 100) if total > 0 else 0
                
                matchup_data[our_race][opp_race] = {
                    "total_games": total,
                    "wins": wins,
                    "losses": total - wins,
                    "win_rate": round(win_rate, 2)
                }
        
        self.results["matchups"] = matchup_data
        print("[OK] 종족 상성 매트릭스 생성 완료")
    
    def run_analysis(self):
        """전체 분석 실행"""
        print("=" * 80)
        print("팀 분석 시작")
        print("=" * 80)
        
        self.load_data()
        self.analyze_overall()
        self.analyze_monthly()
        self.analyze_quarterly()
        self.analyze_by_race()
        self.analyze_by_tier()
        self.analyze_by_game_type()
        self.analyze_by_map()
        self.analyze_matchups()
        
        print("\n" + "=" * 80)
        print("[SUCCESS] 팀 분석 완료")
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
        print("팀 분석 결과 요약")
        print("=" * 80)
        
        # 전체 통계
        overall = self.results["overall"]
        print(f"\n[전체 통계]")
        print(f"  기간: {overall['date_start']} ~ {overall['date_end']}")
        print(f"  총 경기: {overall['total_games']}경기")
        print(f"  승률: {overall['win_rate']}% ({overall['wins']}승 {overall['losses']}패)")
        
        # 경기 유형별
        print(f"\n[경기 유형별]")
        for game_type, data in self.results["by_game_type"].items():
            print(f"  {game_type}: {data['win_rate']}% ({data['wins']}승/{data['total_games']}경기)")
        
        # 종족별
        print(f"\n[종족별]")
        for race, data in self.results["by_race"].items():
            print(f"  {race}: {data['win_rate']}% ({data['wins']}승/{data['total_games']}경기)")
        
        # 월별 (최근 3개월)
        print(f"\n[최근 활동량]")
        monthly = self.results["monthly"]
        months_sorted = sorted(monthly.items(), key=lambda x: x[1]['month'], reverse=True)
        for month_name, data in months_sorted[:3]:
            print(f"  {month_name}: {data['total_games']}경기 (승률 {data['win_rate']}%)")


if __name__ == "__main__":
    # 분석 실행
    validated_csv = get_output_path("validated_data.csv")
    analyzer = TeamAnalyzer(validated_csv)
    results = analyzer.run_analysis()
    
    # 결과 저장
    output_file = get_output_path("team_analysis.json")
    analyzer.save_results(output_file)
    
    # 요약 출력
    analyzer.print_summary()
    
    print("\n[SUCCESS] 팀 분석 완료")

