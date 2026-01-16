"""
Step 3: 차트 생성 (전체 멤버)

matplotlib 기반 레퍼런스 스타일 차트 생성
- 배경: 검정/다크 블루 그라데이션
- 텍스트: 흰색/회색
- 차트: 회색 막대 + 파란 선
- 개선: 8개 차트 생성 (막대+선 복합, 주요 상대별 전적)
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import json
from pathlib import Path
import pandas as pd

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class ChartGenerator:
    def __init__(self):
        """차트 생성기 초기화"""
        print("=" * 80)
        print("Step 3: 차트 생성 (전체 멤버)")
        print("=" * 80)
        
        # 데이터 로드
        self.df = pd.read_excel('kuniv_2025_data.xlsx')
        
        data_dir = Path('output/data')
        with open(data_dir / 'member_statistics.json', encoding='utf-8') as f:
            self.member_stats = json.load(f)
        
        self.output_dir = Path('output/charts')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 레퍼런스 스타일 색상
        self.colors = {
            'bg_dark': '#0a0e1a',
            'bg_light': '#1a2332',
            'text_white': '#ffffff',
            'text_gray': '#9ca3af',
            'bar_gray': '#4b5563',
            'line_blue': '#3b82f6',
            'accent_blue': '#0066ff'
        }
        
        print(f"\n✓ 데이터 로드 완료")
        print(f"  - 전체 멤버 차트 생성 모드")
    
    def set_chart_style(self, fig, ax):
        """레퍼런스 스타일 적용"""
        # 배경색
        fig.patch.set_facecolor(self.colors['bg_dark'])
        ax.set_facecolor(self.colors['bg_dark'])
        
        # 축 색상
        ax.spines['bottom'].set_color(self.colors['text_gray'])
        ax.spines['left'].set_color(self.colors['text_gray'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # 눈금 색상
        ax.tick_params(colors=self.colors['text_gray'], labelsize=10)
        
        # 그리드
        ax.grid(True, alpha=0.1, color=self.colors['text_gray'], linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
    
    def generate_monthly_trend(self, member_name='정서린'):
        """월별 성과 추세 차트 (Page 1)"""
        print(f"\n[1/5] {member_name} - 월별 성과 추세 차트 생성 중...")
        
        stats = self.member_stats[member_name]
        monthly = stats['by_month']
        
        # 데이터 준비
        months = sorted(monthly.keys())
        games = [monthly[m]['total_games'] for m in months]
        win_rates = [monthly[m]['win_rate'] for m in months]
        
        # 월 라벨 (2025-01 → 1월)
        month_labels = [m.split('-')[1] + '월' for m in months]
        
        # 차트 생성
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # 막대 (경기수)
        bars = ax1.bar(month_labels, games, color=self.colors['bar_gray'], alpha=0.7, label='경기수')
        ax1.set_xlabel('월', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax1.set_ylabel('경기수', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        
        # 선 (승률)
        ax2 = ax1.twinx()
        line = ax2.plot(month_labels, win_rates, color=self.colors['line_blue'], 
                       marker='o', linewidth=2.5, markersize=8, label='승률')
        ax2.set_ylabel('승률 (%)', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 100)
        
        # 스타일 적용
        self.set_chart_style(fig, ax1)
        ax2.spines['bottom'].set_color(self.colors['text_gray'])
        ax2.spines['right'].set_color(self.colors['text_gray'])
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.tick_params(colors=self.colors['text_gray'], labelsize=10)
        
        # 타이틀
        plt.title('월별 성과 추세', color=self.colors['text_white'], 
                 fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # 저장
        output_path = self.output_dir / f'{member_name}_monthly_trend.png'
        plt.savefig(output_path, dpi=150, facecolor=self.colors['bg_dark'], 
                   edgecolor='none', bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 저장: {output_path}")
        
        return output_path
    
    def generate_performance_breakdown(self, member_name='정서린'):
        """성과 세부 내역 차트 (Page 2)"""
        print(f"\n[2/5] {member_name} - 성과 세부 내역 차트 생성 중...")
        
        stats = self.member_stats[member_name]
        type_stats = stats['by_type']
        
        # 데이터 준비
        categories = ['스폰', '대회']
        win_rates = [type_stats['스폰']['win_rate'], type_stats['대회']['win_rate']]
        games = [type_stats['스폰']['total_games'], type_stats['대회']['total_games']]
        
        # 차트 생성
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(categories))
        width = 0.5
        
        # 막대
        bars = ax.bar(x, win_rates, width, color=self.colors['bar_gray'], alpha=0.8)
        
        # 막대 위에 값 표시
        for i, (bar, wr, game) in enumerate(zip(bars, win_rates, games)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'{wr}%\n({game}경기)',
                   ha='center', va='bottom', color=self.colors['text_white'],
                   fontsize=11, fontweight='bold')
        
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.set_ylabel('승률 (%)', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax.set_ylim(0, 100)
        
        # 스타일 적용
        self.set_chart_style(fig, ax)
        
        # 타이틀
        plt.title('성과 세부 내역', color=self.colors['text_white'], 
                 fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # 저장
        output_path = self.output_dir / f'{member_name}_performance_breakdown.png'
        plt.savefig(output_path, dpi=150, facecolor=self.colors['bg_dark'], 
                   edgecolor='none', bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 저장: {output_path}")
        
        return output_path
    
    def _calculate_top_opponents(self, member_name, filter_func=None, top_n=5):
        """주요 상대별 전적 계산
        
        Args:
            member_name: 멤버 이름
            filter_func: DataFrame 필터 함수 (예: lambda df: df['상대 종족'] == '테란')
            top_n: 상위 N명
            
        Returns:
            [(상대이름, {games, wins, win_rate}), ...]
        """
        # 멤버 데이터 추출
        member_df = self.df[self.df['멤버 이름'] == member_name].copy()
        
        # 조건 필터링
        if filter_func is not None:
            member_df = member_df[filter_func(member_df)]
        
        # 상대별 집계
        opponent_stats = {}
        for _, row in member_df.iterrows():
            opp = row['상대']
            if opp not in opponent_stats:
                opponent_stats[opp] = {'games': 0, 'wins': 0}
            opponent_stats[opp]['games'] += 1
            if row['결과'] == '승':
                opponent_stats[opp]['wins'] += 1
        
        # 승률 계산
        for opp in opponent_stats:
            stats = opponent_stats[opp]
            stats['win_rate'] = round(stats['wins'] / stats['games'] * 100, 2) if stats['games'] > 0 else 0
        
        # 경기수 많은 순으로 정렬
        sorted_opponents = sorted(opponent_stats.items(), key=lambda x: x[1]['games'], reverse=True)[:top_n]
        
        return sorted_opponents
    
    def generate_race_comparison(self, member_name):
        """종족별 성과 비교 차트 (Page 3 좌측) - 막대+선 복합"""
        print(f"\n[3/8] {member_name} - 종족별 성과 비교 차트 생성 중...")
        
        stats = self.member_stats[member_name]
        race_stats = stats['by_opponent_race']
        
        # 데이터 준비
        races = ['테란', '저그', '프로토스']
        win_rates = [race_stats[r]['win_rate'] for r in races]
        games = [race_stats[r]['total_games'] for r in races]
        
        # 차트 생성
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(races))
        width = 0.5
        
        # 막대 (경기수)
        bars = ax1.bar(x, games, width, color=self.colors['bar_gray'], alpha=0.7, label='경기수')
        ax1.set_ylabel('경기수', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(races)
        
        # 막대 위에 경기수 표시
        for i, (bar, game) in enumerate(zip(bars, games)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(games)*0.02,
                    f'{game}경기',
                    ha='center', va='bottom', color=self.colors['text_gray'],
                    fontsize=10)
        
        # 선 (승률)
        ax2 = ax1.twinx()
        line = ax2.plot(x, win_rates, color=self.colors['line_blue'], 
                       marker='o', linewidth=2.5, markersize=8, label='승률')
        ax2.set_ylabel('승률 (%)', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 100)
        
        # 승률 값 표시 (선 위)
        for i, wr in enumerate(win_rates):
            ax2.text(i, wr + 3, f'{wr}%',
                    ha='center', va='bottom', color=self.colors['line_blue'],
                    fontsize=11, fontweight='bold')
        
        # 스타일 적용
        self.set_chart_style(fig, ax1)
        ax2.spines['bottom'].set_color(self.colors['text_gray'])
        ax2.spines['right'].set_color(self.colors['text_gray'])
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.tick_params(colors=self.colors['text_gray'], labelsize=10)
        
        # 타이틀
        plt.title('종족별 전적 비교', color=self.colors['text_white'], 
                 fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # 저장
        output_path = self.output_dir / f'{member_name}_race_comparison.png'
        plt.savefig(output_path, dpi=150, facecolor=self.colors['bg_dark'], 
                   edgecolor='none', bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 저장: {output_path}")
        
        return output_path
    
    def generate_race_opponents(self, member_name):
        """종족전 주요 상대별 전적 차트 (Page 3 우측) - 막대+선 복합"""
        print(f"\n[4/8] {member_name} - 종족전 주요 상대별 전적 차트 생성 중...")
        
        # 승률 낮은 종족 찾기 (약점 종족)
        stats = self.member_stats[member_name]
        race_stats = stats['by_opponent_race']
        
        races_by_wr = sorted(race_stats.items(), key=lambda x: x[1]['win_rate'])
        target_race = races_by_wr[0][0]
        
        # 해당 종족 상대 중 경기수 많은 상위 5명
        filter_func = lambda df: df['상대 종족'] == target_race
        opponents = self._calculate_top_opponents(member_name, filter_func, top_n=5)
        
        if not opponents:
            print(f"  ! {target_race}전 주요 상대 데이터 없음 - 건너뜀")
            return None
        
        # 데이터 준비
        opp_names = [o[0] for o in opponents]
        win_rates = [o[1]['win_rate'] for o in opponents]
        games = [o[1]['games'] for o in opponents]
        
        # 차트 생성
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(opp_names))
        width = 0.5
        
        # 막대 (경기수)
        bars = ax1.bar(x, games, width, color=self.colors['bar_gray'], alpha=0.7, label='경기수')
        ax1.set_ylabel('경기수', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(opp_names)
        
        # 막대 위에 경기수 표시
        max_games = max(games) if games else 1
        for i, (bar, game) in enumerate(zip(bars, games)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max_games*0.02,
                    f'{game}경기',
                    ha='center', va='bottom', color=self.colors['text_gray'],
                    fontsize=10)
        
        # 선 (승률)
        ax2 = ax1.twinx()
        line = ax2.plot(x, win_rates, color=self.colors['line_blue'], 
                       marker='o', linewidth=2.5, markersize=8, label='승률')
        ax2.set_ylabel('승률 (%)', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 100)
        
        # 승률 값 표시 (선 위)
        for i, wr in enumerate(win_rates):
            ax2.text(i, wr + 3, f'{wr}%',
                    ha='center', va='bottom', color=self.colors['line_blue'],
                    fontsize=11, fontweight='bold')
        
        # 스타일 적용
        self.set_chart_style(fig, ax1)
        ax2.spines['bottom'].set_color(self.colors['text_gray'])
        ax2.spines['right'].set_color(self.colors['text_gray'])
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.tick_params(colors=self.colors['text_gray'], labelsize=10)
        
        # 타이틀
        plt.title(f'{target_race}전 주요 상대별 전적', color=self.colors['text_white'], 
                 fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # 저장
        output_path = self.output_dir / f'{member_name}_race_opponents.png'
        plt.savefig(output_path, dpi=150, facecolor=self.colors['bg_dark'], 
                   edgecolor='none', bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 저장: {output_path}")
        
        return output_path
    
    def generate_map_comparison(self, member_name):
        """맵별 성과 비교 차트 (Page 4 좌측) - 막대+선 복합"""
        print(f"\n[5/8] {member_name} - 맵별 성과 비교 차트 생성 중...")
        
        stats = self.member_stats[member_name]
        map_stats = stats['by_map']
        
        # 경기수 많은 순으로 상위 4개 맵
        sorted_maps = sorted(map_stats.items(), key=lambda x: x[1]['total_games'], reverse=True)[:4]
        
        # 데이터 준비
        maps = [m[0] for m in sorted_maps]
        win_rates = [m[1]['win_rate'] for m in sorted_maps]
        games = [m[1]['total_games'] for m in sorted_maps]
        
        # 차트 생성
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(maps))
        width = 0.5
        
        # 막대 (경기수)
        bars = ax1.bar(x, games, width, color=self.colors['bar_gray'], alpha=0.7, label='경기수')
        ax1.set_ylabel('경기수', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(maps)
        
        # 막대 위에 경기수 표시
        for i, (bar, game) in enumerate(zip(bars, games)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(games)*0.02,
                    f'{game}경기',
                    ha='center', va='bottom', color=self.colors['text_gray'],
                    fontsize=10)
        
        # 선 (승률)
        ax2 = ax1.twinx()
        line = ax2.plot(x, win_rates, color=self.colors['line_blue'], 
                       marker='o', linewidth=2.5, markersize=8, label='승률')
        ax2.set_ylabel('승률 (%)', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 100)
        
        # 승률 값 표시 (선 위)
        for i, wr in enumerate(win_rates):
            ax2.text(i, wr + 3, f'{wr}%',
                    ha='center', va='bottom', color=self.colors['line_blue'],
                    fontsize=11, fontweight='bold')
        
        # 스타일 적용
        self.set_chart_style(fig, ax1)
        ax2.spines['bottom'].set_color(self.colors['text_gray'])
        ax2.spines['right'].set_color(self.colors['text_gray'])
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.tick_params(colors=self.colors['text_gray'], labelsize=10)
        
        # 타이틀
        plt.title('주요 맵별 전적 비교', color=self.colors['text_white'], 
                 fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # 저장
        output_path = self.output_dir / f'{member_name}_map_comparison.png'
        plt.savefig(output_path, dpi=150, facecolor=self.colors['bg_dark'], 
                   edgecolor='none', bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 저장: {output_path}")
        
        return output_path
    
    def generate_map_opponents(self, member_name):
        """맵별 주요 상대별 전적 차트 (Page 4 우측) - 막대+선 복합"""
        print(f"\n[6/8] {member_name} - 맵별 주요 상대별 전적 차트 생성 중...")
        
        # 경기수 많은 맵 찾기
        stats = self.member_stats[member_name]
        map_stats = stats['by_map']
        
        sorted_maps = sorted(map_stats.items(), key=lambda x: x[1]['total_games'], reverse=True)
        if len(sorted_maps) < 2:
            print(f"  ! 맵 데이터 부족 - 건너뜀")
            return None
        
        # 경기수 2번째로 많은 맵 선택 (1번째는 너무 흔할 수 있음)
        target_map = sorted_maps[1][0] if len(sorted_maps) > 1 else sorted_maps[0][0]
        
        # 해당 맵에서 경기수 많은 상위 5명
        filter_func = lambda df: df['맵'] == target_map
        opponents = self._calculate_top_opponents(member_name, filter_func, top_n=5)
        
        if not opponents:
            print(f"  ! {target_map} 주요 상대 데이터 없음 - 건너뜀")
            return None
        
        # 데이터 준비
        opp_names = [o[0] for o in opponents]
        win_rates = [o[1]['win_rate'] for o in opponents]
        games = [o[1]['games'] for o in opponents]
        
        # 차트 생성
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(opp_names))
        width = 0.5
        
        # 막대 (경기수)
        bars = ax1.bar(x, games, width, color=self.colors['bar_gray'], alpha=0.7, label='경기수')
        ax1.set_ylabel('경기수', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(opp_names)
        
        # 막대 위에 경기수 표시
        max_games = max(games) if games else 1
        for i, (bar, game) in enumerate(zip(bars, games)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max_games*0.02,
                    f'{game}경기',
                    ha='center', va='bottom', color=self.colors['text_gray'],
                    fontsize=10)
        
        # 선 (승률)
        ax2 = ax1.twinx()
        line = ax2.plot(x, win_rates, color=self.colors['line_blue'], 
                       marker='o', linewidth=2.5, markersize=8, label='승률')
        ax2.set_ylabel('승률 (%)', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 100)
        
        # 승률 값 표시 (선 위)
        for i, wr in enumerate(win_rates):
            ax2.text(i, wr + 3, f'{wr}%',
                    ha='center', va='bottom', color=self.colors['line_blue'],
                    fontsize=11, fontweight='bold')
        
        # 스타일 적용
        self.set_chart_style(fig, ax1)
        ax2.spines['bottom'].set_color(self.colors['text_gray'])
        ax2.spines['right'].set_color(self.colors['text_gray'])
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.tick_params(colors=self.colors['text_gray'], labelsize=10)
        
        # 타이틀
        plt.title(f'{target_map} 주요 상대별 전적', color=self.colors['text_white'], 
                 fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # 저장
        output_path = self.output_dir / f'{member_name}_map_opponents.png'
        plt.savefig(output_path, dpi=150, facecolor=self.colors['bg_dark'], 
                   edgecolor='none', bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 저장: {output_path}")
        
        return output_path
    
    def generate_tier_comparison(self, member_name):
        """티어별 성과 비교 차트 (Page 5 좌측) - 막대+선 복합"""
        print(f"\n[7/8] {member_name} - 티어별 성과 비교 차트 생성 중...")
        
        stats = self.member_stats[member_name]
        tier_stats = stats['by_tier_matchup']
        
        # 데이터 준비
        tiers = ['상위 티어', '동일 티어', '하위 티어']
        tier_keys = ['upper', 'same', 'lower']
        
        win_rates = []
        games = []
        tier_labels = []
        
        for key, label in zip(tier_keys, tiers):
            if tier_stats[key]['total_games'] > 0:
                win_rates.append(tier_stats[key]['win_rate'])
                games.append(tier_stats[key]['total_games'])
                tier_labels.append(label)
            else:
                win_rates.append(0)
                games.append(0)
                tier_labels.append(label)
        
        # 차트 생성
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(tier_labels))
        width = 0.5
        
        # 막대 (경기수)
        bars = ax1.bar(x, games, width, color=self.colors['bar_gray'], alpha=0.7, label='경기수')
        ax1.set_ylabel('경기수', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(tier_labels)
        
        # 막대 위에 경기수 표시
        max_games = max(games) if games else 1
        for i, (bar, game) in enumerate(zip(bars, games)):
            if game > 0:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + max_games*0.02,
                        f'{game}경기',
                        ha='center', va='bottom', color=self.colors['text_gray'],
                        fontsize=10)
        
        # 선 (승률)
        ax2 = ax1.twinx()
        line = ax2.plot(x, win_rates, color=self.colors['line_blue'], 
                       marker='o', linewidth=2.5, markersize=8, label='승률')
        ax2.set_ylabel('승률 (%)', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 100)
        
        # 승률 값 표시 (선 위)
        for i, wr in enumerate(win_rates):
            if games[i] > 0:
                ax2.text(i, wr + 3, f'{wr}%',
                        ha='center', va='bottom', color=self.colors['line_blue'],
                        fontsize=11, fontweight='bold')
        
        # 스타일 적용
        self.set_chart_style(fig, ax1)
        ax2.spines['bottom'].set_color(self.colors['text_gray'])
        ax2.spines['right'].set_color(self.colors['text_gray'])
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.tick_params(colors=self.colors['text_gray'], labelsize=10)
        
        # 타이틀
        plt.title('상대 티어별 전적 비교', color=self.colors['text_white'], 
                 fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # 저장
        output_path = self.output_dir / f'{member_name}_tier_comparison.png'
        plt.savefig(output_path, dpi=150, facecolor=self.colors['bg_dark'], 
                   edgecolor='none', bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 저장: {output_path}")
        
        return output_path
    
    def generate_tier_opponents(self, member_name):
        """동일 티어 주요 상대별 전적 차트 (Page 5 우측) - 막대+선 복합"""
        print(f"\n[8/8] {member_name} - 동일 티어 주요 상대별 전적 차트 생성 중...")
        
        # 동일 티어 경기만 필터링
        member_df = self.df[self.df['멤버 이름'] == member_name].copy()
        
        # 동일 티어 필터 (멤버 티어 == 상대 티어)
        filter_func = lambda df: df['멤버 티어'] == df['상대 티어']
        opponents = self._calculate_top_opponents(member_name, filter_func, top_n=5)
        
        if not opponents:
            print(f"  ! 동일 티어 주요 상대 데이터 없음 - 건너뜀")
            return None
        
        # 데이터 준비
        opp_names = [o[0] for o in opponents]
        win_rates = [o[1]['win_rate'] for o in opponents]
        games = [o[1]['games'] for o in opponents]
        
        # 차트 생성
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(opp_names))
        width = 0.5
        
        # 막대 (경기수)
        bars = ax1.bar(x, games, width, color=self.colors['bar_gray'], alpha=0.7, label='경기수')
        ax1.set_ylabel('경기수', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(opp_names)
        
        # 막대 위에 경기수 표시
        max_games = max(games) if games else 1
        for i, (bar, game) in enumerate(zip(bars, games)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max_games*0.02,
                    f'{game}경기',
                    ha='center', va='bottom', color=self.colors['text_gray'],
                    fontsize=10)
        
        # 선 (승률)
        ax2 = ax1.twinx()
        line = ax2.plot(x, win_rates, color=self.colors['line_blue'], 
                       marker='o', linewidth=2.5, markersize=8, label='승률')
        ax2.set_ylabel('승률 (%)', color=self.colors['text_white'], fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 100)
        
        # 승률 값 표시 (선 위)
        for i, wr in enumerate(win_rates):
            ax2.text(i, wr + 3, f'{wr}%',
                    ha='center', va='bottom', color=self.colors['line_blue'],
                    fontsize=11, fontweight='bold')
        
        # 스타일 적용
        self.set_chart_style(fig, ax1)
        ax2.spines['bottom'].set_color(self.colors['text_gray'])
        ax2.spines['right'].set_color(self.colors['text_gray'])
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.tick_params(colors=self.colors['text_gray'], labelsize=10)
        
        # 타이틀
        plt.title('동일 티어 주요 상대별 전적', color=self.colors['text_white'], 
                 fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # 저장
        output_path = self.output_dir / f'{member_name}_tier_opponents.png'
        plt.savefig(output_path, dpi=150, facecolor=self.colors['bg_dark'], 
                   edgecolor='none', bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 저장: {output_path}")
        
        return output_path
    
    def generate_all_charts(self, member_name):
        """멤버의 모든 차트 생성 (8개)"""
        print(f"\n{member_name} 차트 생성 시작...")
        
        charts = {}
        
        charts['monthly_trend'] = self.generate_monthly_trend(member_name)
        charts['performance_breakdown'] = self.generate_performance_breakdown(member_name)
        charts['race_comparison'] = self.generate_race_comparison(member_name)
        charts['race_opponents'] = self.generate_race_opponents(member_name)
        charts['map_comparison'] = self.generate_map_comparison(member_name)
        charts['map_opponents'] = self.generate_map_opponents(member_name)
        charts['tier_comparison'] = self.generate_tier_comparison(member_name)
        charts['tier_opponents'] = self.generate_tier_opponents(member_name)
        
        return charts
    
    def generate_for_all_members(self):
        """모든 멤버의 차트 생성"""
        # member_statistics.json에서 멤버 목록 로드
        stats_file = Path('output/data/member_statistics.json')
        with open(stats_file, 'r', encoding='utf-8') as f:
            member_stats = json.load(f)
        
        all_members = list(member_stats.keys())
        
        print(f"\n총 {len(all_members)}명 멤버 차트 생성 시작...")
        print(f"멤버 목록: {', '.join(all_members)}\n")
        
        for i, member in enumerate(all_members, 1):
            print(f"\n{'=' * 80}")
            print(f"[{i}/{len(all_members)}] {member} 차트 생성")
            print(f"{'=' * 80}")
            
            self.generate_all_charts(member)
        
        print(f"\n{'=' * 80}")
        print(f"Step 3 완료: 전체 멤버 차트 생성 성공 ({len(all_members)}명)")
        print(f"{'=' * 80}")
        print(f"\n생성된 차트: {len(all_members) * 8}개 ({len(all_members)}명 × 8종류)")
        print(f"  - output/charts/ 디렉토리 확인")
        print(f"\n✓ Step 3 차트 생성 완료. Step 4 (HTML 슬라이드) 준비 완료.")


if __name__ == '__main__':
    generator = ChartGenerator()
    generator.generate_for_all_members()
