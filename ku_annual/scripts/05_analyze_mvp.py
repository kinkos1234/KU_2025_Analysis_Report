# -*- coding: utf-8 -*-
"""
MVP(Most Valuable Player) 선정 분석 모듈 (고도화 버전)
E-Sports 분석 전문가 관점의 7가지 평가 지표

1. 활동량 & 일관성 (15%) - 얼마나 꾸준히 노력했는가
2. 성장률 (20%) - 얼마나 개선되었는가
3. 동티어 경쟁력 (15%) - 같은 수준에서 얼마나 강한가
4. 상위 도전 정신 (15%) - 상위티어 도전 & 승률
5. 하위 방어율 (10%) - 하위티어 상대 압도력
6. 맵 적응력 (15%) - 맵별 승률 개선 & 다양성
7. 대회 성과 (10%) - 중요한 경기에서의 성과
"""

import pandas as pd
import json
import numpy as np
from pathlib import Path
import sys

# config 모듈 임포트
sys.path.append(str(Path(__file__).parent))
from config import *

class EnhancedMVPAnalyzer:
    def __init__(self, data_path, member_data_path):
        self.data_path = data_path
        self.member_data_path = member_data_path
        self.df = None
        self.member_data = None
        self.mvp_scores = {}
        self.mvp_ranking = []
        
        # 티어 레벨 매핑 (높은 숫자가 상위 티어)
        self.tier_levels = {tier: len(TIER_ORDER) - i for i, tier in enumerate(TIER_ORDER)}
        
    def load_data(self):
        """데이터 로드"""
        print("데이터 로드 중...")
        self.df = pd.read_csv(self.data_path, encoding='utf-8-sig')
        self.df[COL_DATE] = pd.to_datetime(self.df[COL_DATE])
        self.df['month'] = self.df[COL_DATE].dt.month
        
        with open(self.member_data_path, 'r', encoding='utf-8') as f:
            self.member_data = json.load(f)
        
        print(f"[OK] 데이터 로드 완료: {len(self.df)}건, {len(self.member_data)}명")
    
    def calculate_activity_consistency(self, member_name):
        """1. 활동량 & 일관성 점수 (0-100)"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        if len(member_df) == 0:
            return 0, {}
        
        total_games = len(member_df)
        active_months = member_df['month'].nunique()
        avg_games_per_month = total_games / active_months if active_months > 0 else 0
        
        # 월별 경기 수
        monthly_games = member_df.groupby('month').size()
        
        # 일관성: 변동계수(CV)의 역수 (낮을수록 일관적)
        if len(monthly_games) > 1:
            cv = monthly_games.std() / monthly_games.mean()
            consistency = 1 / (1 + cv)  # 0~1 사이 값
        else:
            consistency = 1.0
        
        # 활동 범위: 활동한 개월 수 / 전체 개월 수
        total_months = 11  # 1월~11월
        coverage = active_months / total_months
        
        # 점수 계산
        # 경기 수: 800경기를 만점 기준 (상위권 평균)
        games_score = min(total_games / 800 * 100, 100)
        # 일관성: 0~100점
        consistency_score = consistency * 100
        # 커버리지: 0~100점
        coverage_score = coverage * 100
        
        # 가중 평균 (경기수 40%, 일관성 40%, 커버리지 20%)
        final_score = games_score * 0.4 + consistency_score * 0.4 + coverage_score * 0.2
        
        details = {
            "total_games": total_games,
            "active_months": active_months,
            "avg_per_month": round(avg_games_per_month, 1),
            "consistency": round(consistency, 3),
            "coverage": round(coverage, 3),
            "games_score": round(games_score, 2),
            "consistency_score": round(consistency_score, 2),
            "coverage_score": round(coverage_score, 2),
            "final_score": round(final_score, 2)
        }
        
        return final_score, details
    
    def calculate_growth_rate(self, member_name):
        """2. 성장률 점수 (0-100)"""
        if member_name not in self.member_data:
            return 0, {}
        
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        growth_data = self.member_data[member_name].get('growth')
        
        if not growth_data or len(member_df) < 50:
            return 0, {"reason": "데이터 부족"}
        
        # 전반기 vs 후반기 성장
        overall_growth = growth_data['growth']
        
        # 월별 승률 추세선 기울기 (선형 회귀)
        monthly_wr = []
        months = []
        for month in range(1, 12):
            month_df = member_df[member_df['month'] == month]
            if len(month_df) >= 5:  # 최소 5경기
                wr = len(month_df[month_df[COL_RESULT] == RESULT_WIN]) / len(month_df) * 100
                monthly_wr.append(wr)
                months.append(month)
        
        trend_slope = 0
        if len(monthly_wr) >= 3:
            # 간단한 선형 회귀
            x = np.array(months)
            y = np.array(monthly_wr)
            trend_slope = np.polyfit(x, y, 1)[0]  # 기울기
        
        # 최근 3개월 vs 초기 3개월 비교
        early_3m = member_df[member_df['month'] <= 3]
        recent_3m = member_df[member_df['month'] >= 9]
        
        recent_improvement = 0
        if len(early_3m) >= 10 and len(recent_3m) >= 10:
            early_wr = len(early_3m[early_3m[COL_RESULT] == RESULT_WIN]) / len(early_3m) * 100
            recent_wr = len(recent_3m[recent_3m[COL_RESULT] == RESULT_WIN]) / len(recent_3m) * 100
            recent_improvement = recent_wr - early_wr
        
        # 점수 계산
        # 전반기 vs 후반기: -20%p ~ +30%p를 0~100점으로 환산
        growth_score = min(max((overall_growth + 20) / 50 * 100, 0), 100)
        
        # 월별 트렌드: -2%p/월 ~ +3%p/월을 0~100점으로
        trend_score = min(max((trend_slope + 2) / 5 * 100, 0), 100)
        
        # 최근 개선: -20%p ~ +30%p를 0~100점으로
        recent_score = min(max((recent_improvement + 20) / 50 * 100, 0), 100)
        
        # 가중 평균 (전반기 vs 후반기 50%, 트렌드 30%, 최근 20%)
        final_score = growth_score * 0.5 + trend_score * 0.3 + recent_score * 0.2
        
        details = {
            "overall_growth": round(overall_growth, 2),
            "trend_slope": round(trend_slope, 3),
            "recent_improvement": round(recent_improvement, 2),
            "growth_score": round(growth_score, 2),
            "trend_score": round(trend_score, 2),
            "recent_score": round(recent_score, 2),
            "final_score": round(final_score, 2)
        }
        
        return final_score, details
    
    def calculate_same_tier_dominance(self, member_name):
        """3. 동티어 경쟁력 점수 (0-100)"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        if len(member_df) == 0:
            return 0, {}
        
        main_tier = member_df[COL_MEMBER_TIER].mode()[0] if len(member_df) > 0 else None
        if not main_tier:
            return 0, {"reason": "티어 정보 없음"}
        
        # 동티어 경기
        same_tier_df = member_df[member_df[COL_OPPONENT_TIER] == main_tier]
        
        if len(same_tier_df) < 10:
            return 0, {"reason": "동티어 경기 부족", "games": len(same_tier_df)}
        
        same_tier_wins = len(same_tier_df[same_tier_df[COL_RESULT] == RESULT_WIN])
        same_tier_wr = (same_tier_wins / len(same_tier_df) * 100)
        
        # 동티어 내 연승 기록
        same_tier_df_sorted = same_tier_df.sort_values(COL_DATE)
        max_streak = 0
        current_streak = 0
        for result in same_tier_df_sorted[COL_RESULT]:
            if result == RESULT_WIN:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        # 점수 계산
        # 승률: 40%를 0점, 70%를 100점 기준
        wr_score = min(max((same_tier_wr - 40) / 30 * 100, 0), 100)
        
        # 연승: 5연승을 100점 기준
        streak_score = min(max_streak / 5 * 100, 100)
        
        # 경기 수 신뢰도 (50경기 이상이면 100%)
        reliability = min(len(same_tier_df) / 50, 1.0)
        
        # 가중 평균 (승률 70%, 연승 30%)
        base_score = wr_score * 0.7 + streak_score * 0.3
        final_score = base_score * reliability
        
        details = {
            "main_tier": main_tier,
            "same_tier_games": len(same_tier_df),
            "same_tier_wr": round(same_tier_wr, 2),
            "max_streak": max_streak,
            "wr_score": round(wr_score, 2),
            "streak_score": round(streak_score, 2),
            "reliability": round(reliability, 3),
            "final_score": round(final_score, 2)
        }
        
        return final_score, details
    
    def calculate_upward_challenge(self, member_name):
        """4. 상위 도전 정신 점수 (0-100)"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        if len(member_df) == 0:
            return 0, {}
        
        main_tier = member_df[COL_MEMBER_TIER].mode()[0] if len(member_df) > 0 else None
        if not main_tier or main_tier not in self.tier_levels:
            return 0, {"reason": "티어 정보 없음"}
        
        main_tier_level = self.tier_levels[main_tier]
        
        # 상위티어 도전 경기 (멤버 티어 < 상대 티어)
        upward_df = member_df[
            member_df[COL_OPPONENT_TIER].apply(
                lambda x: self.tier_levels.get(x, 0) > main_tier_level
            )
        ]
        
        if len(upward_df) == 0:
            return 0, {"reason": "상위티어 도전 없음"}
        
        upward_wins = len(upward_df[upward_df[COL_RESULT] == RESULT_WIN])
        upward_wr = (upward_wins / len(upward_df) * 100) if len(upward_df) > 0 else 0
        
        # 도전 빈도 (전체 경기 대비)
        challenge_rate = len(upward_df) / len(member_df)
        
        # 티어 격차별 승률
        tier_gap_wins = {}
        for gap in [1, 2, 3]:  # 1티어 차이, 2티어 차이, 3티어 이상
            gap_df = upward_df[
                upward_df[COL_OPPONENT_TIER].apply(
                    lambda x: main_tier_level < self.tier_levels.get(x, 0) <= main_tier_level + gap
                )
            ]
            if len(gap_df) > 0:
                gap_wr = len(gap_df[gap_df[COL_RESULT] == RESULT_WIN]) / len(gap_df) * 100
                tier_gap_wins[f"{gap}tier_gap"] = round(gap_wr, 2)
        
        # 점수 계산
        # 상위티어 승률: 30%를 50점, 50%를 100점 기준
        wr_score = min(max((upward_wr - 20) / 30 * 100, 0), 100)
        
        # 도전 빈도: 20%를 100점 기준
        frequency_score = min(challenge_rate / 0.2 * 100, 100)
        
        # 경기 수 신뢰도 (20경기 이상이면 100%)
        reliability = min(len(upward_df) / 20, 1.0)
        
        # 가중 평균 (승률 60%, 도전 빈도 40%)
        base_score = wr_score * 0.6 + frequency_score * 0.4
        final_score = base_score * reliability
        
        details = {
            "upward_games": len(upward_df),
            "upward_wr": round(upward_wr, 2),
            "challenge_rate": round(challenge_rate * 100, 2),
            "tier_gap_performance": tier_gap_wins,
            "wr_score": round(wr_score, 2),
            "frequency_score": round(frequency_score, 2),
            "reliability": round(reliability, 3),
            "final_score": round(final_score, 2)
        }
        
        return final_score, details
    
    def calculate_downward_defense(self, member_name):
        """5. 하위 방어율 점수 (0-100)"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        if len(member_df) == 0:
            return 0, {}
        
        main_tier = member_df[COL_MEMBER_TIER].mode()[0] if len(member_df) > 0 else None
        if not main_tier or main_tier not in self.tier_levels:
            return 0, {"reason": "티어 정보 없음"}
        
        main_tier_level = self.tier_levels[main_tier]
        
        # 하위티어 경기 (멤버 티어 > 상대 티어)
        downward_df = member_df[
            member_df[COL_OPPONENT_TIER].apply(
                lambda x: self.tier_levels.get(x, 0) < main_tier_level
            )
        ]
        
        if len(downward_df) < 5:
            return 0, {"reason": "하위티어 경기 부족"}
        
        downward_wins = len(downward_df[downward_df[COL_RESULT] == RESULT_WIN])
        downward_wr = (downward_wins / len(downward_df) * 100)
        
        # 완벽한 방어 (하위티어 상대 연속 승리)
        downward_df_sorted = downward_df.sort_values(COL_DATE)
        max_defense_streak = 0
        current_streak = 0
        for result in downward_df_sorted[COL_RESULT]:
            if result == RESULT_WIN:
                current_streak += 1
                max_defense_streak = max(max_defense_streak, current_streak)
            else:
                current_streak = 0
        
        # 점수 계산
        # 하위티어 승률: 60%를 0점, 85%를 100점 기준 (하위티어는 이겨야 함)
        wr_score = min(max((downward_wr - 60) / 25 * 100, 0), 100)
        
        # 연속 방어: 10연승을 100점 기준
        defense_score = min(max_defense_streak / 10 * 100, 100)
        
        # 가중 평균 (승률 80%, 연속 방어 20%)
        final_score = wr_score * 0.8 + defense_score * 0.2
        
        details = {
            "downward_games": len(downward_df),
            "downward_wr": round(downward_wr, 2),
            "max_defense_streak": max_defense_streak,
            "wr_score": round(wr_score, 2),
            "defense_score": round(defense_score, 2),
            "final_score": round(final_score, 2)
        }
        
        return final_score, details
    
    def calculate_map_adaptability(self, member_name):
        """6. 맵 적응력 점수 (0-100)"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        if len(member_df) < 30:
            return 0, {"reason": "경기 수 부족"}
        
        # 맵별 경기 수 (5경기 이상만)
        map_stats = {}
        for map_name in member_df[COL_MAP].unique():
            map_df = member_df[member_df[COL_MAP] == map_name]
            if len(map_df) >= 5:
                wins = len(map_df[map_df[COL_RESULT] == RESULT_WIN])
                wr = (wins / len(map_df) * 100)
                map_stats[map_name] = {
                    "games": len(map_df),
                    "wr": wr
                }
        
        if len(map_stats) < 3:
            return 0, {"reason": "플레이한 맵 다양성 부족"}
        
        # 맵 다양성 (서로 다른 맵 개수)
        map_diversity = len(map_stats)
        
        # 맵별 승률 표준편차 (낮을수록 모든 맵에서 고르게 강함)
        map_wrs = [stat['wr'] for stat in map_stats.values()]
        wr_std = np.std(map_wrs)
        wr_consistency = 1 / (1 + wr_std / 20)  # 표준편차 20을 기준으로 정규화
        
        # 평균 맵 승률
        avg_map_wr = np.mean(map_wrs)
        
        # 최고/최저 맵 승률 차이 (작을수록 적응력이 높음)
        wr_range = max(map_wrs) - min(map_wrs) if len(map_wrs) > 0 else 0
        
        # 점수 계산
        # 다양성: 10개 맵을 100점 기준
        diversity_score = min(map_diversity / 10 * 100, 100)
        
        # 일관성: 0~100점 (표준편차가 낮을수록 높은 점수)
        consistency_score = wr_consistency * 100
        
        # 평균 승률: 40%를 0점, 65%를 100점 기준
        avg_wr_score = min(max((avg_map_wr - 40) / 25 * 100, 0), 100)
        
        # 가중 평균 (다양성 30%, 일관성 40%, 평균 승률 30%)
        final_score = diversity_score * 0.3 + consistency_score * 0.4 + avg_wr_score * 0.3
        
        details = {
            "map_diversity": map_diversity,
            "avg_map_wr": round(avg_map_wr, 2),
            "wr_std": round(wr_std, 2),
            "wr_range": round(wr_range, 2),
            "best_map": max(map_stats.items(), key=lambda x: x[1]['wr'])[0] if map_stats else None,
            "worst_map": min(map_stats.items(), key=lambda x: x[1]['wr'])[0] if map_stats else None,
            "diversity_score": round(diversity_score, 2),
            "consistency_score": round(consistency_score, 2),
            "avg_wr_score": round(avg_wr_score, 2),
            "final_score": round(final_score, 2)
        }
        
        return final_score, details
    
    def calculate_tournament_performance(self, member_name):
        """7. 대회 성과 점수 (0-100)"""
        member_df = self.df[self.df[COL_MEMBER_NAME] == member_name]
        
        # 대회 경기
        tournament_df = member_df[member_df[COL_TYPE] == GAME_TYPE_TOURNAMENT]
        # 스폰 경기
        spon_df = member_df[member_df[COL_TYPE] == GAME_TYPE_SPON]
        
        if len(tournament_df) < 5:
            return 0, {"reason": "대회 참가 부족"}
        
        tournament_wins = len(tournament_df[tournament_df[COL_RESULT] == RESULT_WIN])
        tournament_wr = (tournament_wins / len(tournament_df) * 100)
        
        # 스폰 승률 대비 대회 승률 차이
        spon_wr = 0
        if len(spon_df) > 0:
            spon_wins = len(spon_df[spon_df[COL_RESULT] == RESULT_WIN])
            spon_wr = (spon_wins / len(spon_df) * 100)
        
        clutch_factor = tournament_wr - spon_wr  # 중요한 순간에 더 강한지
        
        # 대회 참가 적극성 (전체 경기 대비)
        tournament_rate = len(tournament_df) / len(member_df) if len(member_df) > 0 else 0
        
        # 점수 계산
        # 대회 승률: 40%를 0점, 70%를 100점 기준
        wr_score = min(max((tournament_wr - 40) / 30 * 100, 0), 100)
        
        # 클러치: -10%p를 0점, +10%p를 100점 기준
        clutch_score = min(max((clutch_factor + 10) / 20 * 100, 0), 100)
        
        # 참가율: 10%를 100점 기준
        participation_score = min(tournament_rate / 0.1 * 100, 100)
        
        # 가중 평균 (승률 50%, 클러치 30%, 참가율 20%)
        final_score = wr_score * 0.5 + clutch_score * 0.3 + participation_score * 0.2
        
        details = {
            "tournament_games": len(tournament_df),
            "tournament_wr": round(tournament_wr, 2),
            "spon_wr": round(spon_wr, 2),
            "clutch_factor": round(clutch_factor, 2),
            "tournament_rate": round(tournament_rate * 100, 2),
            "wr_score": round(wr_score, 2),
            "clutch_score": round(clutch_score, 2),
            "participation_score": round(participation_score, 2),
            "final_score": round(final_score, 2)
        }
        
        return final_score, details
    
    def calculate_total_mvp_score(self, member_name):
        """종합 MVP 점수 계산 (7가지 지표 가중 평균)"""
        print(f"\n[{member_name}] MVP 점수 계산 중...")
        
        # 7가지 점수 계산
        activity, activity_det = self.calculate_activity_consistency(member_name)
        growth, growth_det = self.calculate_growth_rate(member_name)
        same_tier, same_tier_det = self.calculate_same_tier_dominance(member_name)
        upward, upward_det = self.calculate_upward_challenge(member_name)
        downward, downward_det = self.calculate_downward_defense(member_name)
        map_adapt, map_det = self.calculate_map_adaptability(member_name)
        tournament, tournament_det = self.calculate_tournament_performance(member_name)
        
        # 가중치 (총 100%)
        weights = {
            "activity": 0.15,      # 15%
            "growth": 0.20,        # 20%
            "same_tier": 0.15,     # 15%
            "upward": 0.15,        # 15%
            "downward": 0.10,      # 10%
            "map_adapt": 0.15,     # 15%
            "tournament": 0.10     # 10%
        }
        
        # 종합 점수
        total_score = (
            activity * weights["activity"] +
            growth * weights["growth"] +
            same_tier * weights["same_tier"] +
            upward * weights["upward"] +
            downward * weights["downward"] +
            map_adapt * weights["map_adapt"] +
            tournament * weights["tournament"]
        )
        
        result = {
            "member_name": member_name,
            "total_score": round(total_score, 2),
            "scores": {
                "activity_consistency": {"score": round(activity, 2), "weight": weights["activity"], "details": activity_det},
                "growth_rate": {"score": round(growth, 2), "weight": weights["growth"], "details": growth_det},
                "same_tier_dominance": {"score": round(same_tier, 2), "weight": weights["same_tier"], "details": same_tier_det},
                "upward_challenge": {"score": round(upward, 2), "weight": weights["upward"], "details": upward_det},
                "downward_defense": {"score": round(downward, 2), "weight": weights["downward"], "details": downward_det},
                "map_adaptability": {"score": round(map_adapt, 2), "weight": weights["map_adapt"], "details": map_det},
                "tournament_performance": {"score": round(tournament, 2), "weight": weights["tournament"], "details": tournament_det}
            }
        }
        
        print(f"  활동 {activity:.0f} | 성장 {growth:.0f} | 동티어 {same_tier:.0f} | "
              f"상위도전 {upward:.0f} | 하위방어 {downward:.0f} | 맵적응 {map_adapt:.0f} | "
              f"대회 {tournament:.0f} → 종합 {total_score:.1f}점")
        
        return result
    
    def analyze_all_members(self):
        """모든 멤버 MVP 점수 계산"""
        print("\n" + "=" * 80)
        print("MVP 분석 시작 (7가지 고급 지표)")
        print("=" * 80)
        
        for member_name in self.member_data.keys():
            result = self.calculate_total_mvp_score(member_name)
            self.mvp_scores[member_name] = result
        
        # 점수 순으로 정렬
        self.mvp_ranking = sorted(
            self.mvp_scores.values(),
            key=lambda x: x['total_score'],
            reverse=True
        )
        
        print("\n" + "=" * 80)
        print(f"[SUCCESS] MVP 분석 완료: {len(self.mvp_scores)}명")
        print("=" * 80)
    
    def print_mvp_ranking(self, top_n=10):
        """MVP 순위 출력"""
        print("\n" + "=" * 80)
        print(f"2025년 MVP 최종 순위 (TOP {top_n})")
        print("=" * 80)
        print(f"\n{'순위':<5} {'이름':<10} {'종합':<8} {'활동':<6} {'성장':<6} "
              f"{'동티어':<7} {'상위':<6} {'하위':<6} {'맵':<6} {'대회':<6}")
        print("-" * 80)
        
        for i, candidate in enumerate(self.mvp_ranking[:top_n], 1):
            name = candidate['member_name']
            total = candidate['total_score']
            scores = candidate['scores']
            
            print(f"{i:<5} {name:<10} {total:<8.1f} "
                  f"{scores['activity_consistency']['score']:<6.0f} "
                  f"{scores['growth_rate']['score']:<6.0f} "
                  f"{scores['same_tier_dominance']['score']:<7.0f} "
                  f"{scores['upward_challenge']['score']:<6.0f} "
                  f"{scores['downward_defense']['score']:<6.0f} "
                  f"{scores['map_adaptability']['score']:<6.0f} "
                  f"{scores['tournament_performance']['score']:<6.0f}")
        
        # TOP 3 상세 정보
        print("\n" + "=" * 80)
        print("MVP 후보 상세 분석 (TOP 3)")
        print("=" * 80)
        
        for i, candidate in enumerate(self.mvp_ranking[:3], 1):
            print(f"\n{'='*80}")
            print(f"{i}위. {candidate['member_name']} - 종합 {candidate['total_score']:.1f}점")
            print(f"{'='*80}")
            
            scores = candidate['scores']
            
            # 각 지표별 상세 정보
            for key, data in scores.items():
                title = {
                    "activity_consistency": "활동량 & 일관성",
                    "growth_rate": "성장률",
                    "same_tier_dominance": "동티어 경쟁력",
                    "upward_challenge": "상위 도전 정신",
                    "downward_defense": "하위 방어율",
                    "map_adaptability": "맵 적응력",
                    "tournament_performance": "대회 성과"
                }[key]
                
                print(f"\n[{title}: {data['score']:.1f}점 (가중치 {data['weight']*100:.0f}%)]")
                
                details = data['details']
                if 'reason' not in details:
                    for k, v in list(details.items())[:5]:  # 주요 지표만 표시
                        if isinstance(v, (int, float)):
                            print(f"  - {k}: {v:.2f}" if isinstance(v, float) else f"  - {k}: {v}")
                        else:
                            print(f"  - {k}: {v}")
                else:
                    print(f"  - {details['reason']}")
    
    def save_results(self, output_path):
        """결과 저장"""
        ensure_dirs()
        
        output = {
            "mvp_ranking": self.mvp_ranking,
            "all_scores": self.mvp_scores,
            "evaluation_criteria": {
                "activity_consistency": "활동량 & 일관성 (15%)",
                "growth_rate": "성장률 (20%)",
                "same_tier_dominance": "동티어 경쟁력 (15%)",
                "upward_challenge": "상위 도전 정신 (15%)",
                "downward_defense": "하위 방어율 (10%)",
                "map_adaptability": "맵 적응력 (15%)",
                "tournament_performance": "대회 성과 (10%)"
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\nMVP 분석 결과 저장: {output_path}")
    
    def run_analysis(self):
        """전체 분석 실행"""
        self.load_data()
        self.analyze_all_members()
        return {
            "ranking": self.mvp_ranking,
            "scores": self.mvp_scores
        }


if __name__ == "__main__":
    validated_csv = get_output_path("validated_data.csv")
    member_json = get_output_path("member_analysis.json")
    
    analyzer = EnhancedMVPAnalyzer(validated_csv, member_json)
    results = analyzer.run_analysis()
    
    # 결과 저장
    output_file = get_output_path("mvp_analysis.json")
    analyzer.save_results(output_file)
    
    # 순위 출력
    analyzer.print_mvp_ranking(top_n=15)
    
    print("\n[SUCCESS] MVP 분석 완료")
