# -*- coding: utf-8 -*-
"""
시각화 차트 생성 모듈
- 기존 보고서 스타일 계승 (어두운 배경)
- 팀 분석 차트
- 멤버별 차트
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# config 모듈 임포트
sys.path.append(str(Path(__file__).parent))
from config import *

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class ChartGenerator:
    def __init__(self, team_data_path, member_data_path, mvp_data_path=None):
        self.team_data_path = team_data_path
        self.member_data_path = member_data_path
        self.mvp_data_path = mvp_data_path
        self.team_data = None
        self.member_data = None
        self.mvp_data = None
        
        # 스타일 적용
        self.apply_style()
    
    def apply_style(self):
        """기존 보고서 스타일 적용"""
        for key, value in CHART_STYLE.items():
            plt.rcParams[key] = value
    
    def load_data(self):
        """분석 결과 데이터 로드"""
        print("분석 데이터 로드 중...")
        
        with open(self.team_data_path, 'r', encoding='utf-8') as f:
            self.team_data = json.load(f)
        
        with open(self.member_data_path, 'r', encoding='utf-8') as f:
            self.member_data = json.load(f)
        
        print(f"[OK] 팀 데이터 로드 완료")
        print(f"[OK] 멤버 데이터 로드 완료: {len(self.member_data)}명")
        
        # MVP 데이터 로드 (선택적)
        if self.mvp_data_path and Path(self.mvp_data_path).exists():
            with open(self.mvp_data_path, 'r', encoding='utf-8') as f:
                self.mvp_data = json.load(f)
            print(f"[OK] MVP 데이터 로드 완료")
    
    def create_member_comparison_chart(self):
        """멤버별 전적 비교 차트 (기존 02-01 스타일)"""
        print("\n멤버별 전적 비교 차트 생성 중...")
        
        # 데이터 준비
        members = []
        games = []
        win_rates = []
        
        for member_name, data in self.member_data.items():
            members.append(member_name)
            games.append(data['overall']['total_games'])
            win_rates.append(data['overall']['win_rate'])
        
        # 경기 수 순으로 정렬
        sorted_indices = sorted(range(len(games)), key=lambda i: games[i], reverse=True)
        members = [members[i] for i in sorted_indices]
        games = [games[i] for i in sorted_indices]
        win_rates = [win_rates[i] for i in sorted_indices]
        
        # 차트 생성
        fig, ax = plt.subplots(figsize=(16, 9))
        
        x = np.arange(len(members))
        width = 0.6
        
        # 막대 그래프 (경기 수)
        bars = ax.bar(x, games, width, color=COLOR_PRIMARY, alpha=0.7, label='경기 수')
        
        # 승률 라인 그래프
        ax2 = ax.twinx()
        line = ax2.plot(x, win_rates, color=COLOR_SECONDARY, marker='o', 
                        linewidth=2.5, markersize=8, label='승률', linestyle='--')
        
        # 승률 값 표시
        for i, (rate, game) in enumerate(zip(win_rates, games)):
            ax2.text(i, rate + 1.5, f'{rate}%', ha='center', va='bottom', 
                    color=COLOR_SECONDARY, fontsize=9, fontweight='bold')
        
        # 축 설정
        ax.set_xlabel('멤버', fontsize=12, fontweight='bold')
        ax.set_ylabel('경기 수', fontsize=12, fontweight='bold')
        ax2.set_ylabel('승률 (%)', fontsize=12, fontweight='bold', color=COLOR_SECONDARY)
        ax.set_title('멤버별 전적 비교', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(members, rotation=45, ha='right')
        
        ax.set_ylim(0, max(games) * 1.2)
        ax2.set_ylim(0, 100)
        ax2.tick_params(axis='y', labelcolor=COLOR_SECONDARY)
        
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend(loc='upper left', fontsize=10)
        ax2.legend(loc='upper right', fontsize=10)
        
        plt.tight_layout()
        
        output_path = get_output_path("chart_member_comparison.png", "charts")
        plt.savefig(output_path, dpi=150, facecolor='#1a1a1a')
        plt.close()
        
        print(f"[OK] 저장: {output_path}")
    
    def create_monthly_trend_chart(self):
        """월별 전적 추이 차트"""
        print("\n월별 전적 추이 차트 생성 중...")
        
        monthly = self.team_data['monthly']
        
        months = []
        games = []
        win_rates = []
        
        for month_name, data in sorted(monthly.items(), key=lambda x: x[1]['month']):
            months.append(month_name)
            games.append(data['total_games'])
            win_rates.append(data['win_rate'])
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        x = np.arange(len(months))
        
        # 막대 그래프
        ax.bar(x, games, color=COLOR_PRIMARY, alpha=0.7, label='경기 수')
        
        # 승률 라인
        ax2 = ax.twinx()
        ax2.plot(x, win_rates, color=COLOR_SUCCESS, marker='o', 
                linewidth=2.5, markersize=10, label='승률', linestyle='--')
        
        # 승률 값 표시
        for i, rate in enumerate(win_rates):
            ax2.text(i, rate + 1.5, f'{rate}%', ha='center', va='bottom',
                    color=COLOR_SUCCESS, fontsize=10, fontweight='bold')
        
        ax.set_xlabel('월', fontsize=12, fontweight='bold')
        ax.set_ylabel('경기 수', fontsize=12, fontweight='bold')
        ax2.set_ylabel('승률 (%)', fontsize=12, fontweight='bold', color=COLOR_SUCCESS)
        ax.set_title('월별 전적 추이', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(months)
        
        ax2.set_ylim(0, 100)
        ax2.tick_params(axis='y', labelcolor=COLOR_SUCCESS)
        
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend(loc='upper left', fontsize=10)
        ax2.legend(loc='upper right', fontsize=10)
        
        plt.tight_layout()
        
        output_path = get_output_path("chart_monthly_trend.png", "charts")
        plt.savefig(output_path, dpi=150, facecolor='#1a1a1a')
        plt.close()
        
        print(f"[OK] 저장: {output_path}")
    
    def create_race_comparison_chart(self):
        """종족별 성과 비교 차트"""
        print("\n종족별 성과 비교 차트 생성 중...")
        
        by_race = self.team_data['by_race']
        
        races = list(by_race.keys())
        games = [by_race[race]['total_games'] for race in races]
        win_rates = [by_race[race]['win_rate'] for race in races]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 경기 수 막대 그래프
        colors = [RACE_COLORS.get(race, COLOR_PRIMARY) for race in races]
        ax1.bar(races, games, color=colors, alpha=0.8)
        ax1.set_title('종족별 경기 수', fontsize=14, fontweight='bold')
        ax1.set_ylabel('경기 수', fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        
        for i, (race, game) in enumerate(zip(races, games)):
            ax1.text(i, game + 50, str(game), ha='center', va='bottom',
                    fontsize=11, fontweight='bold')
        
        # 승률 막대 그래프
        ax2.bar(races, win_rates, color=colors, alpha=0.8)
        ax2.set_title('종족별 승률', fontsize=14, fontweight='bold')
        ax2.set_ylabel('승률 (%)', fontsize=11)
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3, axis='y')
        
        for i, (race, wr) in enumerate(zip(races, win_rates)):
            ax2.text(i, wr + 2, f'{wr}%', ha='center', va='bottom',
                    fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        
        output_path = get_output_path("chart_race_comparison.png", "charts")
        plt.savefig(output_path, dpi=150, facecolor='#1a1a1a')
        plt.close()
        
        print(f"[OK] 저장: {output_path}")
    
    def create_matchup_heatmap(self):
        """종족 상성 히트맵"""
        print("\n종족 상성 히트맵 생성 중...")
        
        matchups = self.team_data['matchups']
        
        # 히트맵 데이터 준비
        races = RACES
        matrix = np.zeros((len(races), len(races)))
        
        for i, our_race in enumerate(races):
            for j, opp_race in enumerate(races):
                if our_race in matchups and opp_race in matchups[our_race]:
                    matrix[i][j] = matchups[our_race][opp_race]['win_rate']
        
        # 히트맵 생성
        fig, ax = plt.subplots(figsize=(10, 8))
        
        im = ax.imshow(matrix, cmap='RdYlGn', vmin=0, vmax=100, aspect='auto')
        
        # 축 설정
        ax.set_xticks(np.arange(len(races)))
        ax.set_yticks(np.arange(len(races)))
        ax.set_xticklabels(races)
        ax.set_yticklabels(races)
        
        ax.set_xlabel('상대 종족', fontsize=12, fontweight='bold')
        ax.set_ylabel('아군 종족', fontsize=12, fontweight='bold')
        ax.set_title('종족 상성 매트릭스 (승률 %)', fontsize=14, fontweight='bold', pad=15)
        
        # 숫자 표시
        for i in range(len(races)):
            for j in range(len(races)):
                if matrix[i][j] > 0:
                    text_color = 'white' if matrix[i][j] < 50 else 'black'
                    ax.text(j, i, f'{matrix[i][j]:.1f}%',
                           ha="center", va="center", color=text_color,
                           fontsize=11, fontweight='bold')
        
        # 컬러바
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('승률 (%)', rotation=270, labelpad=20, fontsize=11)
        
        plt.tight_layout()
        
        output_path = get_output_path("chart_matchup_heatmap.png", "charts")
        plt.savefig(output_path, dpi=150, facecolor='#1a1a1a')
        plt.close()
        
        print(f"[OK] 저장: {output_path}")
    
    def create_tier_distribution_chart(self):
        """티어별 분포 차트"""
        print("\n티어별 분포 차트 생성 중...")
        
        by_tier = self.team_data['by_tier']
        
        tiers = [tier for tier in TIER_ORDER if tier in by_tier]
        games = [by_tier[tier]['total_games'] for tier in tiers]
        win_rates = [by_tier[tier]['win_rate'] for tier in tiers]
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        x = np.arange(len(tiers))
        
        # 막대 + 라인
        ax.bar(x, games, color=COLOR_TERTIARY, alpha=0.7, label='경기 수')
        
        ax2 = ax.twinx()
        ax2.plot(x, win_rates, color=COLOR_DANGER, marker='D',
                linewidth=2.5, markersize=8, label='승률', linestyle='--')
        
        for i, wr in enumerate(win_rates):
            ax2.text(i, wr + 1.5, f'{wr}%', ha='center', va='bottom',
                    color=COLOR_DANGER, fontsize=9, fontweight='bold')
        
        ax.set_xlabel('티어', fontsize=12, fontweight='bold')
        ax.set_ylabel('경기 수', fontsize=12, fontweight='bold')
        ax2.set_ylabel('승률 (%)', fontsize=12, fontweight='bold', color=COLOR_DANGER)
        ax.set_title('티어별 전적 분포', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(tiers, rotation=30, ha='right')
        
        ax2.set_ylim(0, 100)
        ax2.tick_params(axis='y', labelcolor=COLOR_DANGER)
        
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend(loc='upper left', fontsize=10)
        ax2.legend(loc='upper right', fontsize=10)
        
        plt.tight_layout()
        
        output_path = get_output_path("chart_tier_distribution.png", "charts")
        plt.savefig(output_path, dpi=150, facecolor='#1a1a1a')
        plt.close()
        
        print(f"[OK] 저장: {output_path}")
    
    def create_game_type_comparison(self):
        """경기 유형별 비교 (스폰 vs 대회)"""
        print("\n경기 유형별 비교 차트 생성 중...")
        
        by_type = self.team_data['by_game_type']
        
        types = list(by_type.keys())
        games = [by_type[t]['total_games'] for t in types]
        win_rates = [by_type[t]['win_rate'] for t in types]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        colors = [COLOR_PRIMARY, COLOR_SECONDARY]
        
        # 경기 수
        ax1.bar(types, games, color=colors, alpha=0.8)
        ax1.set_title('경기 유형별 경기 수', fontsize=14, fontweight='bold')
        ax1.set_ylabel('경기 수', fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        
        for i, game in enumerate(games):
            ax1.text(i, game + 100, str(game), ha='center', va='bottom',
                    fontsize=12, fontweight='bold')
        
        # 승률
        ax2.bar(types, win_rates, color=colors, alpha=0.8)
        ax2.set_title('경기 유형별 승률', fontsize=14, fontweight='bold')
        ax2.set_ylabel('승률 (%)', fontsize=11)
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3, axis='y')
        
        for i, wr in enumerate(win_rates):
            ax2.text(i, wr + 2, f'{wr}%', ha='center', va='bottom',
                    fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        output_path = get_output_path("chart_game_type_comparison.png", "charts")
        plt.savefig(output_path, dpi=150, facecolor='#1a1a1a')
        plt.close()
        
        print(f"[OK] 저장: {output_path}")
    
    def create_top_performers_chart(self):
        """TOP 성과자 차트 (경기 수 100+ 기준)"""
        print("\nTOP 성과자 차트 생성 중...")
        
        # 경기 수 100 이상 필터링
        qualified = {
            name: data for name, data in self.member_data.items()
            if data['overall']['total_games'] >= 100
        }
        
        # 승률 순 정렬
        sorted_members = sorted(
            qualified.items(),
            key=lambda x: x[1]['overall']['win_rate'],
            reverse=True
        )[:10]  # 상위 10명
        
        names = [m[0] for m in sorted_members]
        win_rates = [m[1]['overall']['win_rate'] for m in sorted_members]
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        colors = [COLOR_SUCCESS if wr >= 60 else COLOR_PRIMARY if wr >= 50 else COLOR_DANGER 
                 for wr in win_rates]
        
        bars = ax.barh(names, win_rates, color=colors, alpha=0.8)
        
        ax.set_xlabel('승률 (%)', fontsize=12, fontweight='bold')
        ax.set_title('TOP 성과자 (경기 수 100+ 기준)', fontsize=16, fontweight='bold', pad=15)
        ax.set_xlim(0, 100)
        ax.grid(True, alpha=0.3, axis='x')
        
        for i, (name, wr) in enumerate(zip(names, win_rates)):
            ax.text(wr + 1, i, f'{wr}%', va='center',
                   fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        
        output_path = get_output_path("chart_top_performers.png", "charts")
        plt.savefig(output_path, dpi=150, facecolor='#1a1a1a')
        plt.close()
        
        print(f"[OK] 저장: {output_path}")
    
    def create_mvp_candidates_radar(self):
        """MVP 후보 레이더 차트 (TOP 5)"""
        if not self.mvp_data:
            print("\n[SKIP] MVP 데이터 없음, 레이더 차트 생성 건너뜀")
            return
        
        print("\nMVP 후보 레이더 차트 생성 중...")
        
        top_5 = self.mvp_data['mvp_ranking'][:5]
        
        # 카테고리 (7가지 지표)
        categories = ['활동\n일관성', '성장률', '동티어', '상위\n도전', '하위\n방어', '맵\n적응력', '대회\n성과']
        N = len(categories)
        
        # 각도 계산
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(14, 12), subplot_kw=dict(projection='polar'))
        
        colors = [COLOR_PRIMARY, COLOR_SECONDARY, COLOR_SUCCESS, COLOR_TERTIARY, COLOR_DANGER]
        
        for i, candidate in enumerate(top_5):
            scores = candidate['scores']
            values = [
                scores['activity_consistency']['score'],
                scores['growth_rate']['score'],
                scores['same_tier_dominance']['score'],
                scores['upward_challenge']['score'],
                scores['downward_defense']['score'],
                scores['map_adaptability']['score'],
                scores['tournament_performance']['score']
            ]
            values += values[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2.5, 
                   label=candidate['member_name'], color=colors[i], markersize=8)
            ax.fill(angles, values, alpha=0.15, color=colors[i])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
        ax.grid(True, alpha=0.3)
        
        ax.set_title('MVP 후보 종합 분석 (TOP 5)', fontsize=16, 
                    fontweight='bold', pad=30)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
        
        plt.tight_layout()
        
        output_path = get_output_path("chart_mvp_radar.png", "charts")
        plt.savefig(output_path, dpi=150, facecolor='#1a1a1a', bbox_inches='tight')
        plt.close()
        
        print(f"[OK] 저장: {output_path}")
    
    def create_mvp_ranking_chart(self):
        """MVP 종합 순위 차트 (TOP 10)"""
        if not self.mvp_data:
            print("\n[SKIP] MVP 데이터 없음, 순위 차트 생성 건너뜀")
            return
        
        print("\nMVP 종합 순위 차트 생성 중...")
        
        top_10 = self.mvp_data['mvp_ranking'][:10]
        
        names = [c['member_name'] for c in top_10]
        total_scores = [c['total_score'] for c in top_10]
        activity_scores = [c['scores']['activity_consistency']['score'] for c in top_10]
        growth_scores = [c['scores']['growth_rate']['score'] for c in top_10]
        tier_scores = [c['scores']['same_tier_dominance']['score'] for c in top_10]
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        x = np.arange(len(names))
        width = 0.2
        
        # 3가지 점수 누적 막대
        ax.barh(x - width, activity_scores, width, label='활동량', 
               color=COLOR_PRIMARY, alpha=0.8)
        ax.barh(x, growth_scores, width, label='성장률', 
               color=COLOR_SUCCESS, alpha=0.8)
        ax.barh(x + width, tier_scores, width, label='동티어 경쟁력', 
               color=COLOR_SECONDARY, alpha=0.8)
        
        # 종합 점수 표시
        for i, score in enumerate(total_scores):
            ax.text(score + 2, i, f'{score:.1f}점', va='center',
                   fontsize=10, fontweight='bold', color=COLOR_TERTIARY)
        
        ax.set_yticks(x)
        ax.set_yticklabels(names)
        ax.set_xlabel('점수', fontsize=12, fontweight='bold')
        ax.set_title('MVP 종합 순위 (TOP 10)', fontsize=16, fontweight='bold', pad=15)
        ax.set_xlim(0, max(total_scores) * 1.15)
        ax.grid(True, alpha=0.3, axis='x')
        ax.legend(loc='lower right', fontsize=10)
        
        plt.tight_layout()
        
        output_path = get_output_path("chart_mvp_ranking.png", "charts")
        plt.savefig(output_path, dpi=150, facecolor='#1a1a1a')
        plt.close()
        
        print(f"[OK] 저장: {output_path}")
    
    def create_mvp_growth_comparison(self):
        """MVP 후보 성장 비교 차트 (TOP 5)"""
        if not self.mvp_data:
            print("\n[SKIP] MVP 데이터 없음, 성장 비교 차트 생성 건너뜀")
            return
        
        print("\nMVP 후보 성장 비교 차트 생성 중...")
        
        top_5 = self.mvp_data['mvp_ranking'][:5]
        
        names = []
        growth_rates = []
        
        for candidate in top_5:
            growth_details = candidate['scores']['growth_rate']['details']
            if 'overall_growth' in growth_details:
                names.append(candidate['member_name'])
                growth_rates.append(growth_details['overall_growth'])
        
        if not names:
            print("[SKIP] 성장 데이터 부족")
            return
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        x = np.arange(len(names))
        
        # 성장률 막대 그래프
        colors_bar = [COLOR_SUCCESS if g > 0 else COLOR_DANGER for g in growth_rates]
        bars = ax.bar(x, growth_rates, color=colors_bar, alpha=0.8)
        
        # 0선 강조
        ax.axhline(y=0, color='white', linestyle='--', linewidth=1, alpha=0.5)
        
        # 성장률 값 표시
        for i, growth in enumerate(growth_rates):
            y_pos = growth + (1 if growth > 0 else -1)
            color = COLOR_SUCCESS if growth > 0 else COLOR_DANGER
            ax.text(i, y_pos, f'{growth:+.1f}%p', ha='center',
                   va='bottom' if growth > 0 else 'top',
                   color=color, fontsize=11, fontweight='bold')
        
        ax.set_ylabel('성장률 (%p)', fontsize=12, fontweight='bold')
        ax.set_title('MVP 후보 성장률 비교 (전반기 → 후반기)', 
                    fontsize=16, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=15, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        output_path = get_output_path("chart_mvp_growth.png", "charts")
        plt.savefig(output_path, dpi=150, facecolor='#1a1a1a')
        plt.close()
        
        print(f"[OK] 저장: {output_path}")
    
    def run_generation(self):
        """모든 차트 생성"""
        print("=" * 80)
        print("차트 생성 시작")
        print("=" * 80)
        
        self.load_data()
        
        self.create_member_comparison_chart()
        self.create_monthly_trend_chart()
        self.create_race_comparison_chart()
        self.create_matchup_heatmap()
        self.create_tier_distribution_chart()
        self.create_game_type_comparison()
        self.create_top_performers_chart()
        
        # MVP 차트 (선택적)
        if self.mvp_data:
            self.create_mvp_candidates_radar()
            self.create_mvp_ranking_chart()
            self.create_mvp_growth_comparison()
        
        print("\n" + "=" * 80)
        print("[SUCCESS] 모든 차트 생성 완료")
        print("=" * 80)


if __name__ == "__main__":
    team_json = get_output_path("team_analysis.json")
    member_json = get_output_path("member_analysis.json")
    mvp_json = get_output_path("mvp_analysis.json")
    
    generator = ChartGenerator(team_json, member_json, mvp_json)
    generator.run_generation()
    
    print("\n[SUCCESS] 차트 생성 완료")
    print(f"출력 경로: {CHARTS_DIR}")

