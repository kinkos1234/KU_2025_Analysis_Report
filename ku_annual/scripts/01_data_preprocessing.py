"""
Step 1: 데이터 전처리 및 기본 통계 추출

주요 기능:
1. 티어 이력 추적 시스템 구현 (경기 시점 기준)
2. 팀 전체 통계 추출
3. 14명 멤버별 기본 통계 추출
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class DataPreprocessor:
    def __init__(self, excel_path):
        """데이터 전처리 초기화"""
        print("=" * 80)
        print("Step 1: 데이터 전처리 및 기본 통계 추출")
        print("=" * 80)
        
        self.df = pd.read_excel(excel_path)
        self.output_dir = Path('output/data')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 티어 순서 정의
        self.tier_order = {
            '2티어': 2, '3티어': 3, '4티어': 4, '5티어': 5,
            '6티어': 6, '7티어': 7, '8티어': 8, '베이비': 9
        }
        
        print(f"\n✓ Excel 데이터 로드 완료")
        print(f"  - 총 경기 수: {len(self.df):,}개")
        print(f"  - 기간: {self.df['날짜'].min().date()} ~ {self.df['날짜'].max().date()}")
        print(f"  - 멤버 수: {self.df['멤버 이름'].nunique()}명")
    
    def build_tier_history(self):
        """
        티어 이력 추적 시스템 구축
        
        각 멤버의 티어 변동 이력을 날짜별로 추적
        경기 시점 기준 티어 비교를 위한 기반 데이터
        """
        print("\n[1/4] 티어 이력 추적 시스템 구축 중...")
        
        tier_history = {}
        
        # 멤버별 처리
        for member in self.df['멤버 이름'].unique():
            member_df = self.df[self.df['멤버 이름'] == member].sort_values('날짜')
            
            # 티어 변동 추출
            tier_changes = []
            prev_tier = None
            
            for _, row in member_df.iterrows():
                curr_tier = row['멤버 티어']
                if curr_tier != prev_tier:
                    tier_changes.append({
                        'date': row['날짜'].strftime('%Y-%m-%d'),
                        'tier': curr_tier,
                        'tier_num': self.tier_order.get(curr_tier, 99)
                    })
                    prev_tier = curr_tier
            
            tier_history[member] = {
                'changes': tier_changes,
                'first_tier': tier_changes[0]['tier'] if tier_changes else None,
                'last_tier': tier_changes[-1]['tier'] if tier_changes else None,
                'tier_count': len(tier_changes)
            }
        
        # 저장
        output_path = self.output_dir / 'tier_history.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tier_history, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ 티어 이력 추출 완료: {output_path}")
        
        # 티어 변동 있는 멤버 출력
        print("\n  [티어 변동 멤버]")
        for member, history in tier_history.items():
            if history['tier_count'] > 1:
                print(f"    - {member}: {history['first_tier']} → {history['last_tier']} "
                      f"({history['tier_count']}회 변동)")
        
        return tier_history
    
    def get_tier_at_date(self, member, date, tier_history):
        """특정 날짜의 멤버 티어 반환"""
        if member not in tier_history:
            return None
        
        changes = tier_history[member]['changes']
        date_str = date.strftime('%Y-%m-%d') if isinstance(date, pd.Timestamp) else date
        
        # 해당 날짜 이전 가장 최근 티어 찾기
        current_tier = None
        for change in changes:
            if change['date'] <= date_str:
                current_tier = change['tier']
            else:
                break
        
        return current_tier
    
    def classify_tier_matchup(self, member_tier, opponent_tier):
        """티어 매치업 분류 (동일/상위/하위)"""
        if not member_tier or not opponent_tier:
            return 'unknown'
        
        member_num = self.tier_order.get(member_tier, 99)
        opponent_num = self.tier_order.get(opponent_tier, 99)
        
        if member_num == opponent_num:
            return 'same'
        elif member_num > opponent_num:
            return 'upper'  # 상대가 상위 티어
        else:
            return 'lower'  # 상대가 하위 티어
    
    def extract_team_statistics(self):
        """팀 전체 통계 추출"""
        print("\n[2/4] 팀 전체 통계 추출 중...")
        
        stats = {}
        
        # 1. 전체 통계
        total_games = len(self.df)
        wins = len(self.df[self.df['결과'] == '승'])
        losses = total_games - wins
        
        stats['overall'] = {
            'total_games': total_games,
            'wins': wins,
            'losses': losses,
            'win_rate': round(wins / total_games * 100, 2) if total_games > 0 else 0
        }
        
        # 2. 구분별 통계 (스폰, 대회)
        stats['by_type'] = {}
        
        # 스폰: '스폰'이 포함된 구분
        spon_df = self.df[self.df['구분'].str.contains('스폰', na=False)]
        spon_games = len(spon_df)
        spon_wins = len(spon_df[spon_df['결과'] == '승'])
        
        stats['by_type']['스폰'] = {
            'total_games': spon_games,
            'wins': spon_wins,
            'losses': spon_games - spon_wins,
            'win_rate': round(spon_wins / spon_games * 100, 2) if spon_games > 0 else 0
        }
        
        # 대회: '스폰'이 포함되지 않은 구분
        tournament_df = self.df[~self.df['구분'].str.contains('스폰', na=False)]
        tournament_games = len(tournament_df)
        tournament_wins = len(tournament_df[tournament_df['결과'] == '승'])
        
        stats['by_type']['대회'] = {
            'total_games': tournament_games,
            'wins': tournament_wins,
            'losses': tournament_games - tournament_wins,
            'win_rate': round(tournament_wins / tournament_games * 100, 2) if tournament_games > 0 else 0
        }
        
        # 3. 월별 통계
        self.df['month'] = self.df['날짜'].dt.to_period('M')
        stats['by_month'] = {}
        
        for month in sorted(self.df['month'].unique()):
            month_df = self.df[self.df['month'] == month]
            month_games = len(month_df)
            month_wins = len(month_df[month_df['결과'] == '승'])
            
            stats['by_month'][str(month)] = {
                'total_games': month_games,
                'wins': month_wins,
                'losses': month_games - month_wins,
                'win_rate': round(month_wins / month_games * 100, 2) if month_games > 0 else 0
            }
        
        # 4. 종족별 통계 (아군 종족)
        stats['by_race'] = {}
        for race in ['테란', '저그', '프로토스']:
            race_df = self.df[self.df['멤버 종족'] == race]
            race_games = len(race_df)
            race_wins = len(race_df[race_df['결과'] == '승'])
            
            stats['by_race'][race] = {
                'total_games': race_games,
                'wins': race_wins,
                'losses': race_games - race_wins,
                'win_rate': round(race_wins / race_games * 100, 2) if race_games > 0 else 0
            }
        
        # 저장
        output_path = self.output_dir / 'team_statistics.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ 팀 전체 통계 추출 완료: {output_path}")
        print(f"\n  [팀 전체 성과]")
        print(f"    - 전체: {stats['overall']['total_games']}경기, "
              f"{stats['overall']['win_rate']}% ({stats['overall']['wins']}승 {stats['overall']['losses']}패)")
        print(f"    - 스폰: {stats['by_type']['스폰']['total_games']}경기, "
              f"{stats['by_type']['스폰']['win_rate']}%")
        print(f"    - 대회: {stats['by_type']['대회']['total_games']}경기, "
              f"{stats['by_type']['대회']['win_rate']}%")
        
        return stats
    
    def extract_member_statistics(self, tier_history):
        """
        14명 멤버별 기본 통계 추출
        
        각 멤버에 대해 동일한 기본 분석 수행:
        1. 전체/스폰/대회 승률
        2. 월별 성과
        3. 종족별 성과
        4. 맵별 성과
        5. 티어별 성과 (경기 시점 기준)
        6. 상대별 성과
        """
        print("\n[3/4] 14명 멤버별 기본 통계 추출 중...")
        
        all_members_stats = {}
        
        # 상대 티어 이력도 구축 (경기 시점 티어 비교용)
        print("  - 상대방 티어 이력 구축 중...")
        opponent_tier_history = self._build_opponent_tier_history()
        
        for idx, member in enumerate(sorted(self.df['멤버 이름'].unique()), 1):
            print(f"\n  [{idx}/14] {member} 분석 중...")
            
            member_df = self.df[self.df['멤버 이름'] == member]
            member_stats = {}
            
            # 1. 기본 정보
            member_stats['basic_info'] = {
                'name': member,
                'race': member_df['멤버 종족'].mode()[0],
                'first_tier': tier_history[member]['first_tier'],
                'last_tier': tier_history[member]['last_tier'],
                'tier_changes': tier_history[member]['tier_count']
            }
            
            # 2. 전체 성과
            total_games = len(member_df)
            wins = len(member_df[member_df['결과'] == '승'])
            
            member_stats['overall'] = {
                'total_games': total_games,
                'wins': wins,
                'losses': total_games - wins,
                'win_rate': round(wins / total_games * 100, 2) if total_games > 0 else 0
            }
            
            # 3. 구분별 성과
            member_stats['by_type'] = {}
            
            # 스폰
            spon_df = member_df[member_df['구분'].str.contains('스폰', na=False)]
            spon_games = len(spon_df)
            spon_wins = len(spon_df[spon_df['결과'] == '승'])
            
            member_stats['by_type']['스폰'] = {
                'total_games': spon_games,
                'wins': spon_wins,
                'losses': spon_games - spon_wins,
                'win_rate': round(spon_wins / spon_games * 100, 2) if spon_games > 0 else 0
            }
            
            # 대회
            tournament_df = member_df[~member_df['구분'].str.contains('스폰', na=False)]
            tournament_games = len(tournament_df)
            tournament_wins = len(tournament_df[tournament_df['결과'] == '승'])
            
            member_stats['by_type']['대회'] = {
                'total_games': tournament_games,
                'wins': tournament_wins,
                'losses': tournament_games - tournament_wins,
                'win_rate': round(tournament_wins / tournament_games * 100, 2) if tournament_games > 0 else 0
            }
            
            # 4. 월별 성과
            member_stats['by_month'] = {}
            member_df_copy = member_df.copy()
            member_df_copy['month'] = member_df_copy['날짜'].dt.to_period('M')
            
            for month in sorted(member_df_copy['month'].unique()):
                month_df = member_df_copy[member_df_copy['month'] == month]
                month_games = len(month_df)
                month_wins = len(month_df[month_df['결과'] == '승'])
                
                member_stats['by_month'][str(month)] = {
                    'total_games': month_games,
                    'wins': month_wins,
                    'losses': month_games - month_wins,
                    'win_rate': round(month_wins / month_games * 100, 2) if month_games > 0 else 0
                }
            
            # 5. 상대 종족별 성과
            member_stats['by_opponent_race'] = {}
            for race in ['테란', '저그', '프로토스']:
                race_df = member_df[member_df['상대 종족'] == race]
                race_games = len(race_df)
                race_wins = len(race_df[race_df['결과'] == '승'])
                
                member_stats['by_opponent_race'][race] = {
                    'total_games': race_games,
                    'wins': race_wins,
                    'losses': race_games - race_wins,
                    'win_rate': round(race_wins / race_games * 100, 2) if race_games > 0 else 0
                }
            
            # 6. 맵별 성과 (경기수 20+ 맵만)
            member_stats['by_map'] = {}
            map_counts = member_df['맵'].value_counts()
            
            for map_name in map_counts[map_counts >= 20].index:
                map_df = member_df[member_df['맵'] == map_name]
                map_games = len(map_df)
                map_wins = len(map_df[map_df['결과'] == '승'])
                
                member_stats['by_map'][map_name] = {
                    'total_games': map_games,
                    'wins': map_wins,
                    'losses': map_games - map_wins,
                    'win_rate': round(map_wins / map_games * 100, 2) if map_games > 0 else 0
                }
            
            # 7. 티어별 성과 (경기 시점 기준 - 중요!)
            member_stats['by_tier_matchup'] = self._analyze_tier_matchup(
                member, member_df, tier_history, opponent_tier_history
            )
            
            # 8. 상대별 성과 (경기수 15+ 상대만)
            member_stats['by_opponent'] = {}
            opponent_counts = member_df['상대'].value_counts()
            
            for opponent in opponent_counts[opponent_counts >= 15].index:
                opp_df = member_df[member_df['상대'] == opponent]
                opp_games = len(opp_df)
                opp_wins = len(opp_df[opp_df['결과'] == '승'])
                
                member_stats['by_opponent'][opponent] = {
                    'total_games': opp_games,
                    'wins': opp_wins,
                    'losses': opp_games - opp_wins,
                    'win_rate': round(opp_wins / opp_games * 100, 2) if opp_games > 0 else 0
                }
            
            all_members_stats[member] = member_stats
            
            print(f"      ✓ 전체: {total_games}경기, {member_stats['overall']['win_rate']}%")
            print(f"      ✓ 종족별: {len(member_stats['by_opponent_race'])}개")
            print(f"      ✓ 맵별: {len(member_stats['by_map'])}개 (20경기 이상)")
            print(f"      ✓ 상대별: {len(member_stats['by_opponent'])}개 (15경기 이상)")
        
        # 저장
        output_path = self.output_dir / 'member_statistics.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_members_stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n  ✓ 멤버별 통계 추출 완료: {output_path}")
        
        return all_members_stats
    
    def _build_opponent_tier_history(self):
        """상대방 티어 이력 구축"""
        opponent_tier_history = {}
        
        # 상대 이름별로 티어 변동 추적
        for opponent in self.df['상대'].unique():
            opp_df = self.df[self.df['상대'] == opponent].sort_values('날짜')
            
            tier_changes = []
            prev_tier = None
            
            for _, row in opp_df.iterrows():
                curr_tier = row['상대 티어']
                if curr_tier != prev_tier:
                    tier_changes.append({
                        'date': row['날짜'].strftime('%Y-%m-%d'),
                        'tier': curr_tier,
                        'tier_num': self.tier_order.get(curr_tier, 99)
                    })
                    prev_tier = curr_tier
            
            opponent_tier_history[opponent] = {
                'changes': tier_changes,
                'first_tier': tier_changes[0]['tier'] if tier_changes else None,
                'last_tier': tier_changes[-1]['tier'] if tier_changes else None
            }
        
        return opponent_tier_history
    
    def _analyze_tier_matchup(self, member, member_df, tier_history, opponent_tier_history):
        """
        티어별 매치업 분석 (경기 시점 기준)
        
        중요: 경기 당시의 양측 티어로 비교
        - 11월 3일 경기: 양측 모두 11월 3일 시점 티어
        - 상대가 2주 후 승급해도, 11월 3일엔 동일 티어로 간주
        """
        tier_matchup_stats = {
            'same': {'total_games': 0, 'wins': 0, 'losses': 0, 'win_rate': 0},
            'upper': {'total_games': 0, 'wins': 0, 'losses': 0, 'win_rate': 0},
            'lower': {'total_games': 0, 'wins': 0, 'losses': 0, 'win_rate': 0},
            'unknown': {'total_games': 0, 'wins': 0, 'losses': 0, 'win_rate': 0}
        }
        
        for _, row in member_df.iterrows():
            game_date = row['날짜']
            opponent = row['상대']
            result = row['결과']
            
            # 경기 시점 양측 티어 확인
            member_tier = self.get_tier_at_date(member, game_date, tier_history)
            opponent_tier = self.get_tier_at_date(opponent, game_date, opponent_tier_history)
            
            # 매치업 분류
            matchup_type = self.classify_tier_matchup(member_tier, opponent_tier)
            
            # 통계 업데이트
            tier_matchup_stats[matchup_type]['total_games'] += 1
            if result == '승':
                tier_matchup_stats[matchup_type]['wins'] += 1
            else:
                tier_matchup_stats[matchup_type]['losses'] += 1
        
        # 승률 계산
        for matchup_type in tier_matchup_stats:
            games = tier_matchup_stats[matchup_type]['total_games']
            wins = tier_matchup_stats[matchup_type]['wins']
            if games > 0:
                tier_matchup_stats[matchup_type]['win_rate'] = round(wins / games * 100, 2)
        
        return tier_matchup_stats
    
    def generate_summary(self, tier_history, team_stats, member_stats):
        """전체 요약 보고서 생성"""
        print("\n[4/4] 전체 요약 보고서 생성 중...")
        
        summary = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_period': {
                'start': self.df['날짜'].min().strftime('%Y-%m-%d'),
                'end': self.df['날짜'].max().strftime('%Y-%m-%d')
            },
            'team_summary': {
                'total_games': team_stats['overall']['total_games'],
                'overall_win_rate': team_stats['overall']['win_rate'],
                'spon_win_rate': team_stats['by_type']['스폰']['win_rate'],
                'tournament_win_rate': team_stats['by_type']['대회']['win_rate']
            },
            'member_summary': {}
        }
        
        # 멤버별 요약
        for member, stats in member_stats.items():
            summary['member_summary'][member] = {
                'race': stats['basic_info']['race'],
                'tier': stats['basic_info']['last_tier'],
                'total_games': stats['overall']['total_games'],
                'overall_win_rate': stats['overall']['win_rate'],
                'spon_win_rate': stats['by_type']['스폰']['win_rate'],
                'tournament_win_rate': stats['by_type']['대회']['win_rate']
            }
        
        # 저장
        output_path = self.output_dir / 'preprocessing_summary.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ 요약 보고서 생성 완료: {output_path}")
        
        return summary
    
    def run(self):
        """전체 전처리 프로세스 실행"""
        try:
            # 1. 티어 이력 추적
            tier_history = self.build_tier_history()
            
            # 2. 팀 전체 통계
            team_stats = self.extract_team_statistics()
            
            # 3. 멤버별 통계
            member_stats = self.extract_member_statistics(tier_history)
            
            # 4. 요약 보고서
            summary = self.generate_summary(tier_history, team_stats, member_stats)
            
            print("\n" + "=" * 80)
            print("Step 1 완료: 데이터 전처리 및 기본 통계 추출 성공")
            print("=" * 80)
            print(f"\n생성된 파일:")
            print(f"  - output/data/tier_history.json")
            print(f"  - output/data/team_statistics.json")
            print(f"  - output/data/member_statistics.json")
            print(f"  - output/data/preprocessing_summary.json")
            
            return {
                'tier_history': tier_history,
                'team_stats': team_stats,
                'member_stats': member_stats,
                'summary': summary
            }
            
        except Exception as e:
            print(f"\n✗ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return None


if __name__ == '__main__':
    # 실행
    preprocessor = DataPreprocessor('kuniv_2025_data.xlsx')
    result = preprocessor.run()
    
    if result:
        print("\n✓ Step 1 전처리 완료. Step 2 (패턴 발굴) 준비 완료.")
