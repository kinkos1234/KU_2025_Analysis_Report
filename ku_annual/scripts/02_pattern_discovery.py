"""
Step 2: 패턴 발굴 및 개인별 특성 식별

프로토타입: 정서린, 슬돌이 2명

주요 기능:
1. 자동 강점/약점 식별
2. 원인 규명을 위한 추가 분석 플래닝
3. 개인화된 코멘트 생성 (사람처럼 분석)
4. 개인화된 페이지 구성 결정
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict

class PatternDiscovery:
    def __init__(self):
        """패턴 발굴 초기화"""
        print("=" * 80)
        print("Step 2: 패턴 발굴 및 개인별 특성 식별 (프로토타입)")
        print("=" * 80)
        
        # 데이터 로드
        self.df = pd.read_excel('kuniv_2025_data.xlsx')
        
        data_dir = Path('output/data')
        with open(data_dir / 'tier_history.json', encoding='utf-8') as f:
            self.tier_history = json.load(f)
        with open(data_dir / 'team_statistics.json', encoding='utf-8') as f:
            self.team_stats = json.load(f)
        with open(data_dir / 'member_statistics.json', encoding='utf-8') as f:
            self.member_stats = json.load(f)
        
        self.output_dir = Path('output/analysis')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n✓ 데이터 로드 완료")
        print(f"  - 프로토타입 대상: 정서린, 슬돌이")
    
    def analyze_member_prototype(self, member_name):
        """
        멤버 개인별 심층 분석 (프로토타입)
        
        사람처럼 데이터를 해석:
        1. 강점/약점 자동 식별
        2. 원인 규명을 위한 추가 분석
        3. 스토리 추출
        4. 개인화된 페이지 구성 결정
        """
        print(f"\n{'=' * 80}")
        print(f"[{member_name}] 심층 분석")
        print(f"{'=' * 80}")
        
        member_df = self.df[self.df['멤버 이름'] == member_name]
        stats = self.member_stats[member_name]
        
        analysis = {
            'name': member_name,
            'basic_info': stats['basic_info'],
            'overall_stats': stats['overall'],
            'strengths': [],
            'weaknesses': [],
            'stories': [],
            'deep_analysis': {},
            'page_customization': {},
            'comments': {}
        }
        
        print(f"\n[기본 정보]")
        print(f"  종족: {stats['basic_info']['race']}")
        print(f"  티어: {stats['basic_info']['first_tier']} → {stats['basic_info']['last_tier']}")
        print(f"  전체: {stats['overall']['total_games']}경기, {stats['overall']['win_rate']}%")
        print(f"  스폰: {stats['by_type']['스폰']['win_rate']}%, 대회: {stats['by_type']['대회']['win_rate']}%")
        
        # 1. 강점/약점 자동 식별
        print(f"\n[1/4] 강점/약점 자동 식별 중...")
        self._identify_strengths_weaknesses(member_name, member_df, stats, analysis)
        
        # 2. 원인 규명을 위한 추가 분석
        print(f"\n[2/4] 약점 원인 규명 중...")
        self._deep_dive_analysis(member_name, member_df, stats, analysis)
        
        # 3. 스토리 추출
        print(f"\n[3/4] 개인 스토리 추출 중...")
        self._extract_stories(member_name, member_df, stats, analysis)
        
        # 4. 개인화된 페이지 구성
        print(f"\n[4/4] 개인화된 페이지 구성 결정 중...")
        self._customize_pages(member_name, stats, analysis)
        
        return analysis
    
    def _identify_strengths_weaknesses(self, member_name, member_df, stats, analysis):
        """강점/약점 자동 식별"""
        
        # === 1. 전체 승률 평가 ===
        overall_wr = stats['overall']['win_rate']
        team_avg = self.team_stats['overall']['win_rate']
        
        if overall_wr >= 65:
            analysis['strengths'].append({
                'category': 'overall_performance',
                'type': 'exceptional',
                'value': overall_wr,
                'description': f'전체 승률 {overall_wr}% (팀 평균 {team_avg}% 대비 +{overall_wr - team_avg:.2f}%p)',
                'priority': 'high'
            })
            print(f"  ✓ [강점] 뛰어난 전체 성과: {overall_wr}%")
        elif overall_wr <= 45:
            analysis['weaknesses'].append({
                'category': 'overall_performance',
                'type': 'struggling',
                'value': overall_wr,
                'description': f'전체 승률 {overall_wr}% (팀 평균 {team_avg}% 대비 {overall_wr - team_avg:.2f}%p)',
                'priority': 'high'
            })
            print(f"  ✓ [약점] 전반적 부진: {overall_wr}%")
        
        # === 2. 스폰 vs 대회 비교 ===
        spon_wr = stats['by_type']['스폰']['win_rate']
        tournament_wr = stats['by_type']['대회']['win_rate']
        diff = tournament_wr - spon_wr
        
        if abs(diff) >= 10:
            if diff > 0:
                analysis['strengths'].append({
                    'category': 'tournament_ace',
                    'type': 'clutch_performer',
                    'value': diff,
                    'description': f'대회 승률 {tournament_wr}% (스폰 대비 +{diff:.2f}%p, 클러치 성과)',
                    'priority': 'high'
                })
                print(f"  ✓ [강점] 대회 에이스: 대회 {tournament_wr}% vs 스폰 {spon_wr}% (+{diff:.2f}%p)")
            else:
                analysis['weaknesses'].append({
                    'category': 'tournament_performance',
                    'type': 'tournament_struggle',
                    'value': diff,
                    'description': f'대회 승률 {tournament_wr}% (스폰 대비 {diff:.2f}%p)',
                    'priority': 'medium'
                })
                print(f"  ✓ [약점] 대회 부진: 대회 {tournament_wr}% vs 스폰 {spon_wr}% ({diff:.2f}%p)")
        
        # === 3. 종족별 성과 비교 ===
        races = stats['by_opponent_race']
        race_wrs = {race: data['win_rate'] for race, data in races.items() if data['total_games'] >= 20}
        
        if race_wrs:
            max_race = max(race_wrs, key=race_wrs.get)
            min_race = min(race_wrs, key=race_wrs.get)
            race_diff = race_wrs[max_race] - race_wrs[min_race]
            
            if race_diff >= 10:
                # 최약 종족
                analysis['weaknesses'].append({
                    'category': 'race_matchup',
                    'type': f'{min_race}_weakness',
                    'value': race_wrs[min_race],
                    'description': f'{min_race}전 {race_wrs[min_race]}% (최강 {max_race}전 {race_wrs[max_race]}% 대비 -{race_diff:.2f}%p)',
                    'priority': 'high',
                    'details': {
                        'weak_race': min_race,
                        'weak_wr': race_wrs[min_race],
                        'strong_race': max_race,
                        'strong_wr': race_wrs[max_race],
                        'total_games': races[min_race]['total_games']
                    }
                })
                print(f"  ✓ [약점] {min_race}전 약세: {race_wrs[min_race]}% (vs {max_race}전 {race_wrs[max_race]}%)")
                
                # 최강 종족
                if race_wrs[max_race] >= 60:
                    analysis['strengths'].append({
                        'category': 'race_matchup',
                        'type': f'{max_race}_strength',
                        'value': race_wrs[max_race],
                        'description': f'{max_race}전 {race_wrs[max_race]}% (우수한 성과)',
                        'priority': 'medium'
                    })
                    print(f"  ✓ [강점] {max_race}전 강점: {race_wrs[max_race]}%")
        
        # === 4. 맵별 성과 비교 ===
        maps = stats['by_map']
        if maps:
            map_wrs = {map_name: data['win_rate'] for map_name, data in maps.items()}
            max_map = max(map_wrs, key=map_wrs.get)
            min_map = min(map_wrs, key=map_wrs.get)
            
            # 최다 경기 맵
            max_games_map = max(maps, key=lambda x: maps[x]['total_games'])
            max_games_count = maps[max_games_map]['total_games']
            max_games_wr = maps[max_games_map]['win_rate']
            
            # 최다 경기 맵이 약점인 경우
            if max_games_wr < 50 and max_games_count >= 50:
                analysis['weaknesses'].append({
                    'category': 'map_performance',
                    'type': f'{max_games_map}_weakness',
                    'value': max_games_wr,
                    'description': f'{max_games_map} {max_games_count}경기 {max_games_wr}% (최다 경기 맵에서 약세)',
                    'priority': 'high',
                    'details': {
                        'map': max_games_map,
                        'total_games': max_games_count,
                        'win_rate': max_games_wr
                    }
                })
                print(f"  ✓ [약점] {max_games_map} 약세: {max_games_count}경기 {max_games_wr}%")
            
            # 최다 경기 맵이 강점인 경우
            elif max_games_wr >= 60 and max_games_count >= 50:
                analysis['strengths'].append({
                    'category': 'map_performance',
                    'type': f'{max_games_map}_strength',
                    'value': max_games_wr,
                    'description': f'{max_games_map} {max_games_count}경기 {max_games_wr}% (최다 경기 맵에서 우수)',
                    'priority': 'medium'
                })
                print(f"  ✓ [강점] {max_games_map} 강점: {max_games_count}경기 {max_games_wr}%")
        
        # === 5. 티어별 성과 (경기 시점 기준) ===
        tier_matchup = stats['by_tier_matchup']
        same_tier_wr = tier_matchup['same']['win_rate']
        same_tier_games = tier_matchup['same']['total_games']
        
        if same_tier_games >= 50:
            if same_tier_wr >= 65:
                analysis['strengths'].append({
                    'category': 'tier_dominance',
                    'type': 'same_tier_dominance',
                    'value': same_tier_wr,
                    'description': f'동일 티어 지배력 {same_tier_wr}% ({same_tier_games}경기)',
                    'priority': 'high'
                })
                print(f"  ✓ [강점] 동일 티어 지배: {same_tier_wr}% ({same_tier_games}경기)")
            elif same_tier_wr < 50:
                analysis['weaknesses'].append({
                    'category': 'tier_performance',
                    'type': 'same_tier_struggle',
                    'value': same_tier_wr,
                    'description': f'동일 티어 부진 {same_tier_wr}% ({same_tier_games}경기)',
                    'priority': 'high'
                })
                print(f"  ✓ [약점] 동일 티어 부진: {same_tier_wr}% ({same_tier_games}경기)")
        
        # 상위 티어 도전
        upper_tier_wr = tier_matchup['upper']['win_rate']
        upper_tier_games = tier_matchup['upper']['total_games']
        
        if upper_tier_games >= 20:
            if upper_tier_wr >= 50:
                analysis['strengths'].append({
                    'category': 'tier_challenge',
                    'type': 'upper_tier_success',
                    'value': upper_tier_wr,
                    'description': f'상위 티어 도전 성공 {upper_tier_wr}% ({upper_tier_games}경기)',
                    'priority': 'medium'
                })
                print(f"  ✓ [강점] 상위 티어 선전: {upper_tier_wr}% ({upper_tier_games}경기)")
        
        # === 6. 상대별 성과 (특정 상대 약점) ===
        opponents = stats['by_opponent']
        weak_opponents = []
        
        for opp, data in opponents.items():
            if data['total_games'] >= 15 and data['win_rate'] <= 40:
                weak_opponents.append({
                    'opponent': opp,
                    'win_rate': data['win_rate'],
                    'games': data['total_games']
                })
        
        if weak_opponents:
            # 가장 약한 상대 (경기수 많은 순)
            weakest = max(weak_opponents, key=lambda x: x['games'])
            analysis['weaknesses'].append({
                'category': 'opponent_matchup',
                'type': f'{weakest["opponent"]}_weakness',
                'value': weakest['win_rate'],
                'description': f'{weakest["opponent"]} 상대 {weakest["games"]}경기 {weakest["win_rate"]}% (특정 상대 약세)',
                'priority': 'medium',
                'details': weakest
            })
            print(f"  ✓ [약점] {weakest['opponent']} 약세: {weakest['games']}경기 {weakest['win_rate']}%")
        
        # === 7. 월별 추세 분석 ===
        monthly = stats['by_month']
        if len(monthly) >= 6:
            months = sorted(monthly.keys())
            first_half = months[:len(months)//2]
            second_half = months[len(months)//2:]
            
            first_half_wr = sum(monthly[m]['wins'] for m in first_half) / sum(monthly[m]['total_games'] for m in first_half) * 100
            second_half_wr = sum(monthly[m]['wins'] for m in second_half) / sum(monthly[m]['total_games'] for m in second_half) * 100
            
            growth = second_half_wr - first_half_wr
            
            if abs(growth) >= 8:
                if growth > 0:
                    analysis['strengths'].append({
                        'category': 'growth',
                        'type': 'improving_trend',
                        'value': growth,
                        'description': f'성장세 (전반기 {first_half_wr:.2f}% → 후반기 {second_half_wr:.2f}%, +{growth:.2f}%p)',
                        'priority': 'high'
                    })
                    print(f"  ✓ [강점] 성장세: 전반기 {first_half_wr:.2f}% → 후반기 {second_half_wr:.2f}% (+{growth:.2f}%p)")
                else:
                    analysis['weaknesses'].append({
                        'category': 'trend',
                        'type': 'declining_trend',
                        'value': growth,
                        'description': f'하락세 (전반기 {first_half_wr:.2f}% → 후반기 {second_half_wr:.2f}%, {growth:.2f}%p)',
                        'priority': 'medium'
                    })
                    print(f"  ✓ [약점] 하락세: 전반기 {first_half_wr:.2f}% → 후반기 {second_half_wr:.2f}% ({growth:.2f}%p)")
    
    def _deep_dive_analysis(self, member_name, member_df, stats, analysis):
        """
        약점 원인 규명을 위한 추가 분석
        
        사람처럼 생각하기:
        "왜 이 멤버는 테란전이 약할까?"
        → 특정 맵에서? 특정 상대한테?
        → 추가 데이터 분석으로 원인 규명
        """
        
        deep_analysis = {}
        
        # 약점 중 우선순위 높은 것들에 대해 원인 규명
        high_priority_weaknesses = [w for w in analysis['weaknesses'] if w['priority'] == 'high']
        
        for weakness in high_priority_weaknesses:
            category = weakness['category']
            
            # === 1. 종족별 약점 원인 규명 ===
            if category == 'race_matchup':
                weak_race = weakness['details']['weak_race']
                print(f"  → {weak_race}전 약점 원인 분석 중...")
                
                # 해당 종족전만 필터
                race_df = member_df[member_df['상대 종족'] == weak_race]
                
                # 맵별 분석
                race_map_stats = {}
                for map_name in race_df['맵'].value_counts().index[:5]:  # 상위 5개 맵
                    map_df = race_df[race_df['맵'] == map_name]
                    if len(map_df) >= 10:
                        wins = len(map_df[map_df['결과'] == '승'])
                        race_map_stats[map_name] = {
                            'games': len(map_df),
                            'wins': wins,
                            'win_rate': round(wins / len(map_df) * 100, 2)
                        }
                
                # 상대별 분석
                race_opp_stats = {}
                for opponent in race_df['상대'].value_counts().index[:5]:
                    opp_df = race_df[race_df['상대'] == opponent]
                    if len(opp_df) >= 10:
                        wins = len(opp_df[opp_df['결과'] == '승'])
                        race_opp_stats[opponent] = {
                            'games': len(opp_df),
                            'wins': wins,
                            'win_rate': round(wins / len(opp_df) * 100, 2)
                        }
                
                deep_analysis[f'{weak_race}전_약점'] = {
                    'reason': f'{weak_race}전 약점 원인 규명',
                    'map_breakdown': race_map_stats,
                    'opponent_breakdown': race_opp_stats
                }
                
                # 가장 약한 맵/상대 출력
                if race_map_stats:
                    weakest_map = min(race_map_stats, key=lambda x: race_map_stats[x]['win_rate'])
                    print(f"     - 가장 약한 맵: {weakest_map} ({race_map_stats[weakest_map]['games']}경기, {race_map_stats[weakest_map]['win_rate']}%)")
                
                if race_opp_stats:
                    weakest_opp = min(race_opp_stats, key=lambda x: race_opp_stats[x]['win_rate'])
                    print(f"     - 가장 약한 상대: {weakest_opp} ({race_opp_stats[weakest_opp]['games']}경기, {race_opp_stats[weakest_opp]['win_rate']}%)")
            
            # === 2. 맵별 약점 원인 규명 ===
            elif category == 'map_performance':
                weak_map = weakness['details']['map']
                print(f"  → {weak_map} 맵 약점 원인 분석 중...")
                
                # 해당 맵만 필터
                map_df = member_df[member_df['맵'] == weak_map]
                
                # 종족별 분석
                map_race_stats = {}
                for race in ['테란', '저그', '프로토스']:
                    race_df = map_df[map_df['상대 종족'] == race]
                    if len(race_df) >= 5:
                        wins = len(race_df[race_df['결과'] == '승'])
                        map_race_stats[race] = {
                            'games': len(race_df),
                            'wins': wins,
                            'win_rate': round(wins / len(race_df) * 100, 2)
                        }
                
                # 상대별 분석
                map_opp_stats = {}
                for opponent in map_df['상대'].value_counts().index[:5]:
                    opp_df = map_df[map_df['상대'] == opponent]
                    if len(opp_df) >= 5:
                        wins = len(opp_df[opp_df['결과'] == '승'])
                        map_opp_stats[opponent] = {
                            'games': len(opp_df),
                            'wins': wins,
                            'win_rate': round(wins / len(opp_df) * 100, 2)
                        }
                
                deep_analysis[f'{weak_map}_약점'] = {
                    'reason': f'{weak_map} 맵 약점 원인 규명',
                    'race_breakdown': map_race_stats,
                    'opponent_breakdown': map_opp_stats
                }
                
                # 가장 약한 종족/상대 출력
                if map_race_stats:
                    weakest_race = min(map_race_stats, key=lambda x: map_race_stats[x]['win_rate'])
                    print(f"     - 가장 약한 종족: {weakest_race} ({map_race_stats[weakest_race]['games']}경기, {map_race_stats[weakest_race]['win_rate']}%)")
                
                if map_opp_stats:
                    weakest_opp = min(map_opp_stats, key=lambda x: map_opp_stats[x]['win_rate'])
                    print(f"     - 가장 약한 상대: {weakest_opp} ({map_opp_stats[weakest_opp]['games']}경기, {map_opp_stats[weakest_opp]['win_rate']}%)")
        
        analysis['deep_analysis'] = deep_analysis
    
    def _extract_stories(self, member_name, member_df, stats, analysis):
        """개인 스토리 추출"""
        
        stories = []
        
        # 1. 티어 성장 스토리
        tier_changes = self.tier_history[member_name]['tier_count']
        if tier_changes > 1:
            first_tier = self.tier_history[member_name]['first_tier']
            last_tier = self.tier_history[member_name]['last_tier']
            
            tier_order = {'베이비': 9, '8티어': 8, '7티어': 7, '6티어': 6, '5티어': 5, '4티어': 4, '3티어': 3, '2티어': 2}
            growth = tier_order[first_tier] - tier_order[last_tier]
            
            if growth >= 2:
                stories.append({
                    'type': 'explosive_growth',
                    'title': f'{first_tier}에서 {last_tier}로 {growth}단계 승급',
                    'description': f'{member_name}는 시즌 시작 {first_tier}에서 {last_tier}까지 {growth}단계 상승하며 폭발적인 성장을 보였습니다.',
                    'priority': 'high'
                })
                print(f"  ✓ [스토리] 폭발적 성장: {first_tier} → {last_tier} ({growth}단계)")
            elif growth == 1:
                stories.append({
                    'type': 'promotion',
                    'title': f'{first_tier}에서 {last_tier}로 승급',
                    'description': f'{member_name}는 시즌 중 {last_tier}로 승급하며 성장세를 보였습니다.',
                    'priority': 'medium'
                })
                print(f"  ✓ [스토리] 승급: {first_tier} → {last_tier}")
        
        # 2. 완벽한 달 (100% 승률)
        monthly = stats['by_month']
        perfect_months = []
        for month, data in monthly.items():
            if data['total_games'] >= 10 and data['win_rate'] == 100.0:
                perfect_months.append((month, data['total_games']))
        
        if perfect_months:
            for month, games in perfect_months:
                stories.append({
                    'type': 'perfect_month',
                    'title': f'{month} 완벽한 달 (100% 승률)',
                    'description': f'{member_name}는 {month}에 {games}경기 전승을 기록하며 완벽한 한 달을 보냈습니다.',
                    'priority': 'high'
                })
                print(f"  ✓ [스토리] 완벽한 달: {month} {games}경기 100%")
        
        # 3. 신인 이야기 (베이비 티어 시작)
        if self.tier_history[member_name]['first_tier'] == '베이비':
            overall_wr = stats['overall']['win_rate']
            if overall_wr >= 60:
                stories.append({
                    'type': 'rookie_star',
                    'title': '신인왕 후보',
                    'description': f'{member_name}는 베이비 티어에서 시작하여 {overall_wr}%의 뛰어난 승률을 기록하며 신인왕 후보로 떠올랐습니다.',
                    'priority': 'high'
                })
                print(f"  ✓ [스토리] 신인 스타: 베이비 시작, {overall_wr}% 달성")
        
        # 4. 대회 클러치 성과
        tournament_wr = stats['by_type']['대회']['win_rate']
        spon_wr = stats['by_type']['스폰']['win_rate']
        
        if tournament_wr - spon_wr >= 15 and stats['by_type']['대회']['total_games'] >= 20:
            stories.append({
                'type': 'tournament_clutch',
                'title': '클러치 플레이어',
                'description': f'{member_name}는 중요한 순간에 강한 모습을 보이며, 대회 승률 {tournament_wr}%로 스폰 대비 {tournament_wr - spon_wr:.2f}%p 높은 성과를 냈습니다.',
                'priority': 'high'
            })
            print(f"  ✓ [스토리] 클러치 성과: 대회 {tournament_wr}% vs 스폰 {spon_wr}%")
        
        analysis['stories'] = stories
    
    def _customize_pages(self, member_name, stats, analysis):
        """
        개인화된 페이지 구성 결정
        
        멤버별로 다른 차트/분석 구성
        """
        
        page_config = {
            'cover': {'standard': True},
            'page_1_monthly': {'standard': True},
            'page_2_performance': {'standard': True, 'comment_focus': []},
            'page_3': {'type': None, 'charts': []},
            'page_4': {'type': None, 'charts': []},
            'page_5': {'type': None, 'charts': []},
        }
        
        # Page 2 코멘트 포커스 결정
        high_priority = [s['type'] for s in analysis['strengths'] if s['priority'] == 'high']
        high_priority += [w['type'] for w in analysis['weaknesses'] if w['priority'] == 'high']
        page_config['page_2_performance']['comment_focus'] = high_priority
        
        # Page 3-5 구성 결정
        weaknesses = analysis['weaknesses']
        
        # 종족별 약점이 있는 경우
        race_weakness = next((w for w in weaknesses if w['category'] == 'race_matchup'), None)
        map_weakness = next((w for w in weaknesses if w['category'] == 'map_performance'), None)
        
        if race_weakness:
            # Page 3: 종족별 비교 (표준) + 약점 종족 세부 분석
            weak_race = race_weakness['details']['weak_race']
            page_config['page_3'] = {
                'type': 'race_comparison_with_deep_dive',
                'charts': [
                    {'type': 'race_bar_chart', 'title': '상대 종족별 성과'},
                    {'type': 'weak_race_map_breakdown', 'title': f'{weak_race}전 맵별 세부 분석', 'race': weak_race}
                ]
            }
            print(f"  ✓ Page 3: 종족별 비교 + {weak_race}전 맵별 세부 분석")
        else:
            # 표준 종족별 비교
            page_config['page_3'] = {
                'type': 'standard_race_comparison',
                'charts': [{'type': 'race_bar_chart', 'title': '상대 종족별 성과'}]
            }
            print(f"  ✓ Page 3: 표준 종족별 비교")
        
        if map_weakness:
            # Page 4: 맵별 비교 (표준) + 약점 맵 종족별 세부 분석
            weak_map = map_weakness['details']['map']
            page_config['page_4'] = {
                'type': 'map_comparison_with_deep_dive',
                'charts': [
                    {'type': 'map_bar_chart', 'title': '주요 맵별 성과'},
                    {'type': 'weak_map_race_breakdown', 'title': f'{weak_map} 종족별 세부 분석', 'map': weak_map}
                ]
            }
            print(f"  ✓ Page 4: 맵별 비교 + {weak_map} 종족별 세부 분석")
        else:
            # 표준 맵별 비교
            page_config['page_4'] = {
                'type': 'standard_map_comparison',
                'charts': [{'type': 'map_bar_chart', 'title': '주요 맵별 성과'}]
            }
            print(f"  ✓ Page 4: 표준 맵별 비교")
        
        # Page 5: 티어별 비교 (표준)
        page_config['page_5'] = {
            'type': 'standard_tier_comparison',
            'charts': [{'type': 'tier_bar_chart', 'title': '상대 티어별 성과'}]
        }
        print(f"  ✓ Page 5: 표준 티어별 비교")
        
        analysis['page_customization'] = page_config
    
    def generate_comments(self, member_name, analysis):
        """
        사람처럼 분석하는 코멘트 생성
        
        구조: [핵심 인사이트] + [구체적 원인/맥락] + [미래 지향적 제안/관찰]
        """
        print(f"\n[코멘트 생성] {member_name}")
        
        comments = {}
        
        # Page 2: 성과 세부 내역 코멘트
        comments['page_2_performance'] = self._generate_performance_comment(member_name, analysis)
        
        # Page 3: 종족별 코멘트
        comments['page_3_race'] = self._generate_race_comment(member_name, analysis)
        
        # Page 4: 맵별 코멘트
        comments['page_4_map'] = self._generate_map_comment(member_name, analysis)
        
        # Page 5: 티어별 코멘트
        comments['page_5_tier'] = self._generate_tier_comment(member_name, analysis)
        
        analysis['comments'] = comments
        
        return comments
    
    def _generate_performance_comment(self, member_name, analysis):
        """성과 세부 내역 코멘트"""
        stats = analysis['overall_stats']
        type_stats = self.member_stats[member_name]['by_type']
        monthly = self.member_stats[member_name]['by_month']
        
        spon_wr = type_stats['스폰']['win_rate']
        tournament_wr = type_stats['대회']['win_rate']
        diff = tournament_wr - spon_wr
        
        spon_games = type_stats['스폰']['total_games']
        tournament_games = type_stats['대회']['total_games']
        
        # 스토리 활용
        stories = analysis['stories']
        growth_story = next((s for s in stories if s['type'] in ['explosive_growth', 'promotion']), None)
        perfect_story = next((s for s in stories if s['type'] == 'perfect_month'), None)
        clutch_story = next((s for s in stories if s['type'] == 'tournament_clutch'), None)
        rookie_story = next((s for s in stories if s['type'] == 'rookie_star'), None)
        
        comment_parts = []
        
        # 핵심 인사이트 (대회 vs 스폰)
        if tournament_games >= 15:
            if clutch_story or (diff >= 15 and tournament_wr >= 65):
                # 대회 에이스
                comment_parts.append(f"대회 승률 {tournament_wr}%로 스폰 대비 {diff:.2f}%p 높은 성과는 매우 고무적")
            elif diff >= 10:
                comment_parts.append(f"대회 승률이 스폰보다 {diff:.2f}%p 높아 중요한 순간에 강한 모습")
            elif diff <= -10:
                comment_parts.append(f"스폰 승률 {spon_wr}%에 비해 대회 {tournament_wr}%로 다소 아쉬운 모습")
            elif diff <= -5:
                # 소폭 대회 부진
                comment_parts.append(f"대회 승률 {tournament_wr}%는 스폰 {spon_wr}%에 비해 다소 낮음")
            elif abs(diff) <= 5:
                if spon_wr >= 60:
                    comment_parts.append(f"스폰 {spon_wr}%, 대회 {tournament_wr}%로 모두 우수한 성과")
                else:
                    comment_parts.append(f"스폰 {spon_wr}%, 대회 {tournament_wr}%로 안정적인 성과")
            else:
                comment_parts.append(f"스폰 {spon_wr}%, 대회 {tournament_wr}% 기록")
        else:
            # 대회 경기가 적은 경우
            if spon_games >= 50:
                comment_parts.append(f"스폰 {spon_games}경기 {spon_wr}% 기록")
            else:
                comment_parts.append(f"총 {stats['total_games']}경기 진행")
        
        # 특별한 성과/맥락
        if perfect_story:
            # 완벽한 달
            month_title = perfect_story['title']
            # "2025-08 완벽한 달 (100% 승률)" → "8월 완벽한 달을 기록한 점은 특기할 만함"
            month_str = month_title.split()[0]  # "2025-08"
            try:
                month_num = int(month_str.split('-')[1])
                comment_parts.append(f"{month_num}월 완벽한 달을 기록한 점은 특기할 만함")
            except:
                comment_parts.append("완벽한 달을 기록한 점은 특기할 만함")
        
        # 월별 특이점 (급등/급락)
        if len(monthly) >= 3:
            monthly_wrs = [(month, data['win_rate']) for month, data in monthly.items() if data['total_games'] >= 10]
            if len(monthly_wrs) >= 3:
                # 최고/최저 승률 달
                max_month = max(monthly_wrs, key=lambda x: x[1])
                min_month = min(monthly_wrs, key=lambda x: x[1])
                
                wr_diff = max_month[1] - min_month[1]
                
                if wr_diff >= 25 and not perfect_story:
                    # 큰 변동성
                    try:
                        max_month_num = int(max_month[0].split('-')[1])
                        min_month_num = int(min_month[0].split('-')[1])
                        
                        if min_month_num < max_month_num:
                            # 성장 패턴
                            comment_parts.append(f"{min_month_num}월 부진({min_month[1]}%) 이후 {max_month_num}월 {max_month[1]}%까지 개선된 점은 고무적")
                        else:
                            # 하락 패턴
                            comment_parts.append(f"{max_month_num}월 {max_month[1]}% 이후 {min_month_num}월 {min_month[1]}%로 다소 하락")
                    except:
                        pass
        
        # 성장 스토리
        if growth_story:
            # "정서린는 시즌 시작 베이비에서 7티어까지 2단계 상승하며 폭발적인 성장을 보였습니다" 
            # → 자연스럽게 연결
            growth_desc = growth_story['description']
            # "정서린는" → 제거, "시즌 시작" 제거
            growth_desc = growth_desc.replace(f"{member_name}는 ", "").replace("시즌 시작 ", "").strip()
            
            if growth_story['type'] == 'explosive_growth':
                # 폭발적 성장
                # "베이비에서 7티어까지..." → 그대로 사용
                comment_parts.append(growth_desc.rstrip('.'))  # 마침표 제거
            elif growth_story['type'] == 'promotion':
                # 일반 승급
                tier_info = growth_story['title']  # "3티어에서 2티어로 승급"
                comment_parts.append(f"{tier_info}하며 성장세를 보임")
        
        # 미래 지향적 제안/관찰
        if tournament_wr < spon_wr - 10 and tournament_games >= 15:
            comment_parts.append("대회 경기에서의 안정성 보완이 필요해 보임")
        elif rookie_story and stats['win_rate'] >= 65 and not perfect_story:
            # 신인에 대한 신중한 낙관 (완벽한 달 있으면 제외)
            comment_parts.append("하지만 아직 초반이니 조금 더 지켜볼 필요가 있음")
        
        return '. '.join(comment_parts) + '.'
    
    def _evaluate_win_rate(self, win_rate):
        """
        승률 구간 평가
        
        - 65% 이상: 뛰어난/우수한
        - 55~64%: 우수한
        - 50~54%: 안정적/준수한
        - 45~49%: 다소 개선 필요
        - 45% 미만: 개선 시급
        """
        if win_rate >= 65:
            return 'exceptional'  # 뛰어난
        elif win_rate >= 55:
            return 'good'  # 우수한
        elif win_rate >= 50:
            return 'stable'  # 안정적/준수한
        elif win_rate >= 45:
            return 'needs_improvement'  # 다소 개선 필요
        else:
            return 'urgent_improvement'  # 개선 시급
    
    def _get_performance_description(self, win_rate, context='neutral'):
        """승률에 따른 표현 반환"""
        level = self._evaluate_win_rate(win_rate)
        
        if context == 'positive':
            # 긍정적 맥락
            if level == 'exceptional':
                return '뛰어난 성과'
            elif level == 'good':
                return '우수한 성과'
            elif level == 'stable':
                return '준수한 성과'
            elif level == 'needs_improvement':
                return '다소 아쉬운 성과'
            else:
                return '개선이 필요한 성과'
        elif context == 'negative':
            # 부정적 맥락
            if level == 'exceptional':
                return '뛰어남'
            elif level == 'good':
                return '우수함'
            elif level == 'stable':
                return '준수함'
            elif level == 'needs_improvement':
                return '다소 아쉬움'
            else:
                return '개선 시급'
        else:
            # 중립적
            if level == 'exceptional':
                return '뛰어난'
            elif level == 'good':
                return '우수한'
            elif level == 'stable':
                return '안정적인'
            elif level == 'needs_improvement':
                return '다소 아쉬운'
            else:
                return '부진한'
    
    def _generate_race_comment(self, member_name, analysis):
        """종족별 성과 코멘트"""
        stats = self.member_stats[member_name]['by_opponent_race']
        
        race_wrs = {race: data['win_rate'] for race, data in stats.items() if data['total_games'] >= 10}
        if not race_wrs:
            return "종족별 경기 수가 충분하지 않아 평가가 제한적입니다."
        
        max_race = max(race_wrs, key=race_wrs.get)
        min_race = min(race_wrs, key=race_wrs.get)
        race_diff = race_wrs[max_race] - race_wrs[min_race]
        
        comment_parts = []
        
        # 핵심 인사이트 (종족별 밸런스)
        if race_diff >= 15:
            # 큰 차이: 명확한 약점 표현
            comment_parts.append(f"{min_race}전 승률 {race_wrs[min_race]}%는 타 종족전({max_race} {race_wrs[max_race]}%)에 비해 소폭 낮음")
        elif race_diff >= 10:
            # 중간 차이: 양호하지만 약점 언급
            comment_parts.append(f"세 종족전 모두 양호한 승률을 보였으나, {min_race}전은 타 종족전에 비해 소폭 낮은 승률")
        else:
            # 작은 차이: 균형잡힌
            if all(wr >= 55 for wr in race_wrs.values()):
                comment_parts.append(f"세 종족전 모두 우수한 승률을 기록")
            else:
                comment_parts.append(f"세 종족전 모두 균형잡힌 승률을 보임")
        
        # 구체적 원인 (deep_analysis 활용)
        deep = analysis['deep_analysis']
        race_deep = next((v for k, v in deep.items() if min_race in k), None)
        
        if race_deep and 'opponent_breakdown' in race_deep:
            opp_breakdown = race_deep['opponent_breakdown']
            if opp_breakdown:
                # 승률 40% 이하 상대 찾기
                weak_opps = sorted(opp_breakdown.items(), key=lambda x: x[1]['win_rate'])[:3]
                weak_names = [opp for opp, data in weak_opps if data['win_rate'] <= 40]
                
                if weak_names:
                    # 구체적 상대 언급 (레퍼런스 스타일)
                    if len(weak_names) == 1:
                        opp_data = opp_breakdown[weak_names[0]]
                        comment_parts.append(f"{weak_names[0]} 상대로의 경기가 다소 약세였음을 참조하여 교육 및 연습이 필요해 보임")
                    elif len(weak_names) == 2:
                        comment_parts.append(f"{'&'.join(weak_names)} 상대로의 경기가 다소 약세였음을 참조하여 교육 및 연습이 필요해 보임")
                    else:
                        # 3명 이상이면 2명만 언급
                        comment_parts.append(f"{'&'.join(weak_names[:2])} 상대로의 약세가 두드러짐")
        
        # 제안 (심각한 경우만)
        if race_wrs[min_race] < 45 and race_diff >= 15:
            comment_parts.append(f"{min_race}전 집중 연습이 더 필요해 보임")
        
        return '. '.join(comment_parts) + '.' if comment_parts else "전반적으로 양호한 종족별 성과를 보이고 있습니다."
    
    def _generate_map_comment(self, member_name, analysis):
        """맵별 성과 코멘트"""
        stats = self.member_stats[member_name]['by_map']
        
        if not stats:
            return "맵별 경기 수가 충분하지 않아 평가가 제한적입니다."
        
        # 최다 경기 맵
        max_games_map = max(stats, key=lambda x: stats[x]['total_games'])
        max_games_data = stats[max_games_map]
        max_games_wr = max_games_data['win_rate']
        
        # 최고/최저 승률 맵
        max_wr_map = max(stats, key=lambda x: stats[x]['win_rate'])
        min_wr_map = min(stats, key=lambda x: stats[x]['win_rate'])
        
        comment_parts = []
        
        # 핵심 인사이트 (최다 경기 맵 - 승률 절대 평가 우선)
        wr_level = self._evaluate_win_rate(max_games_wr)
        
        if wr_level in ['exceptional', 'good']:
            # 65% 이상 또는 55~64%: 우수한 성과
            perf_desc = self._get_performance_description(max_games_wr, 'positive')
            comment_parts.append(f"가장 많은 경기를 진행한 {max_games_map}에서 {max_games_wr}%의 {perf_desc}")
        elif wr_level == 'stable':
            # 50~54%: 안정적
            if max_games_map == min_wr_map:
                # 최다 경기 맵이 최저 승률이지만 50% 이상
                comment_parts.append(f"가장 많은 경기를 진행한 {max_games_map}에서 {max_games_wr}%로 안정적이나 타 맵 대비 다소 낮은 편")
            else:
                comment_parts.append(f"가장 많은 경기를 진행한 {max_games_map}에서 {max_games_wr}%의 안정적인 성과")
        else:
            # 50% 미만: 개선 필요
            perf_desc = self._get_performance_description(max_games_wr, 'negative')
            comment_parts.append(f"가장 많은 경기를 진행한 {max_games_map}에서 {max_games_wr}%로 {perf_desc}")
        
        # 구체적 원인 (deep_analysis 활용)
        deep = analysis['deep_analysis']
        map_deep = next((v for k, v in deep.items() if max_games_map in k), None)
        
        weak_detail_parts = []
        
        if map_deep:
            # 약점 종족 찾기
            if 'race_breakdown' in map_deep:
                race_breakdown = map_deep['race_breakdown']
                if race_breakdown:
                    weak_races = [(race, data) for race, data in race_breakdown.items() if data['win_rate'] < 50]
                    if weak_races:
                        weak_race, weak_data = min(weak_races, key=lambda x: x[1]['win_rate'])
                        weak_detail_parts.append(f"{weak_race}전에서 다소 어려움")
            
            # 약점 상대 찾기
            if 'opponent_breakdown' in map_deep:
                opp_breakdown = map_deep['opponent_breakdown']
                if opp_breakdown:
                    weak_opps = sorted(opp_breakdown.items(), key=lambda x: x[1]['win_rate'])[:2]
                    weak_names = [opp for opp, data in weak_opps if data['win_rate'] < 40]
                    
                    if weak_names:
                        # 캐주얼한 톤 (레퍼런스 스타일)
                        if len(weak_names) == 1:
                            if weak_detail_parts:
                                # 종족+상대 조합
                                weak_detail_parts.append(f"{weak_names[0]} 상대로의 약세가 두드러짐")
                            else:
                                weak_detail_parts.append(f"{weak_names[0]} 상대로 고전")
                        else:
                            weak_detail_parts.append(f"{'&'.join(weak_names)} 상대로의 약세")
        
        # 약점 디테일 연결
        if weak_detail_parts:
            comment_parts.append(', '.join(weak_detail_parts))
        
        # 다른 맵 언급 (최저 승률 맵이 다르고 의미있는 경우)
        if min_wr_map != max_games_map and stats[min_wr_map]['total_games'] >= 20:
            min_wr_data = stats[min_wr_map]
            min_wr = min_wr_data['win_rate']
            
            if min_wr < 50:
                # 최저 승률 맵 약점 분석
                min_map_deep = next((v for k, v in deep.items() if min_wr_map in k), None)
                
                if min_map_deep and 'opponent_breakdown' in min_map_deep:
                    min_opp_breakdown = min_map_deep['opponent_breakdown']
                    if min_opp_breakdown:
                        min_weak_opps = sorted(min_opp_breakdown.items(), key=lambda x: x[1]['win_rate'])[:1]
                        if min_weak_opps and min_weak_opps[0][1]['win_rate'] < 35:
                            # 캐주얼한 표현 사용
                            comment_parts.append(f"{min_wr_map}에서 {min_weak_opps[0][0]} 상대로 무드러 맞음")
                        else:
                            comment_parts.append(f"{min_wr_map}은 {min_wr}%로 아쉬움")
                else:
                    comment_parts.append(f"{min_wr_map}은 {min_wr}%로 약세")
        
        # 제안
        if max_games_wr < 50 or (weak_detail_parts and max_games_wr < 55):
            # 구체적인 약점이 있으면 맵+매치업 연습 제안
            if weak_detail_parts and 'race_breakdown' in (map_deep or {}):
                race_breakdown = map_deep.get('race_breakdown', {})
                weak_races = [race for race, data in race_breakdown.items() if data['win_rate'] < 50]
                if weak_races:
                    comment_parts.append(f"{max_games_map} {weak_races[0]}전 연습 및 교육이 더 필요해 보임")
                else:
                    comment_parts.append(f"{max_games_map} 맵 연습이 더 필요해 보임")
            else:
                comment_parts.append(f"{max_games_map} 맵 연습이 더 필요해 보임")
        
        return '. '.join(comment_parts) + '.' if comment_parts else "맵별 성과는 전반적으로 양호합니다."
    
    def _generate_tier_comment(self, member_name, analysis):
        """티어별 성과 코멘트"""
        tier_stats = self.member_stats[member_name]['by_tier_matchup']
        member_df = self.df[self.df['멤버 이름'] == member_name]
        
        same = tier_stats['same']
        upper = tier_stats['upper']
        lower = tier_stats['lower']
        
        comment_parts = []
        
        # 핵심 인사이트 (동일 티어)
        if same['total_games'] >= 30:
            if same['win_rate'] >= 65:
                comment_parts.append(f"동일 티어 상대로 {same['win_rate']}%의 우수한 승률을 기록하며 티어 지배력을 보임")
            elif same['win_rate'] >= 50:
                comment_parts.append(f"동일 티어 상대로 {same['win_rate']}%의 준수한 성과")
            else:
                comment_parts.append(f"동일 티어 상대로 {same['win_rate']}%로 다소 부진한 모습")
            
            # 동일 티어 내 종족별 약점 분석 (레퍼런스 스타일)
            # 동일 티어 경기만 필터
            tier_history = self.tier_history
            same_tier_games = []
            
            for _, row in member_df.iterrows():
                game_date = row['날짜']
                opponent = row['상대']
                
                member_tier = self._get_tier_at_date(member_name, game_date, tier_history)
                opponent_tier = self._get_tier_at_date_opponent(opponent, game_date)
                
                if member_tier == opponent_tier:
                    same_tier_games.append(row)
            
            if same_tier_games:
                same_tier_df = pd.DataFrame(same_tier_games)
                
                # 동일 티어 내 종족별 승률
                race_wrs = {}
                for race in ['테란', '저그', '프로토스']:
                    race_games = same_tier_df[same_tier_df['상대 종족'] == race]
                    if len(race_games) >= 15:
                        wins = len(race_games[race_games['결과'] == '승'])
                        race_wrs[race] = {
                            'win_rate': round(wins / len(race_games) * 100, 2),
                            'games': len(race_games)
                        }
                
                if race_wrs:
                    # 약점 종족 찾기
                    min_race = min(race_wrs, key=lambda x: race_wrs[x]['win_rate'])
                    min_wr = race_wrs[min_race]['win_rate']
                    
                    if min_wr < same['win_rate'] - 10 and min_wr < 55:
                        # 레퍼런스 스타일: "동일 티어 중에도 테란전은 다소 부족"
                        comment_parts.append(f"다만, 동일 티어 중에도 {min_race}전은 다소 부족한 모습")
        
        # 상위 티어 도전
        if upper['total_games'] >= 15:
            if upper['win_rate'] >= 50:
                comment_parts.append(f"상위 티어 상대로도 {upper['win_rate']}%의 선전")
            else:
                comment_parts.append(f"상위 티어 상대로는 {upper['win_rate']}%로 경험 쌓기가 필요")
        
        # 미래 지향적 제안
        if same['win_rate'] >= 65:
            if upper['total_games'] < 30:
                comment_parts.append("승급을 대비해 상위 티어 상대와의 경험 쌓기가 필요해 보임")
            elif upper['win_rate'] < 45:
                comment_parts.append("승급 후 안착을 위해 상위 티어 상대 연구가 더 필요해 보임")
        elif same['win_rate'] < 50:
            comment_parts.append("동일 티어 내 경쟁력 강화가 우선적으로 필요")
        
        return '. '.join(comment_parts) + '.' if comment_parts else "티어별 성과는 전반적으로 양호합니다."
    
    def _get_tier_at_date(self, member, date, tier_history):
        """특정 날짜의 멤버 티어 반환"""
        if member not in tier_history:
            return None
        
        changes = tier_history[member]['changes']
        date_str = date.strftime('%Y-%m-%d') if isinstance(date, pd.Timestamp) else date
        
        current_tier = None
        for change in changes:
            if change['date'] <= date_str:
                current_tier = change['tier']
            else:
                break
        
        return current_tier
    
    def _get_tier_at_date_opponent(self, opponent, date):
        """특정 날짜의 상대 티어 반환"""
        # 상대 티어 이력에서 찾기
        opp_df = self.df[self.df['상대'] == opponent].sort_values('날짜')
        if len(opp_df) == 0:
            return None
        
        date_str = date.strftime('%Y-%m-%d') if isinstance(date, pd.Timestamp) else date
        
        # 해당 날짜 이전 가장 최근 경기의 상대 티어
        before_games = opp_df[opp_df['날짜'] <= date]
        if len(before_games) > 0:
            return before_games.iloc[-1]['상대 티어']
        
        return None
    
    def run_prototype(self):
        """프로토타입 실행"""
        target_members = ['정서린', '슬돌이']
        results = {}
        
        for member in target_members:
            # 분석
            analysis = self.analyze_member_prototype(member)
            
            # 코멘트 생성
            comments = self.generate_comments(member, analysis)
            
            # 저장
            output_path = self.output_dir / f'{member}_analysis.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            
            print(f"\n{'=' * 80}")
            print(f"[{member}] 분석 완료")
            print(f"  - 저장 위치: {output_path}")
            print(f"  - 강점: {len(analysis['strengths'])}개")
            print(f"  - 약점: {len(analysis['weaknesses'])}개")
            print(f"  - 스토리: {len(analysis['stories'])}개")
            print(f"  - 심층 분석: {len(analysis['deep_analysis'])}개")
            print(f"{'=' * 80}")
            
            # 코멘트 출력
            print(f"\n[생성된 코멘트]")
            for page, comment in comments.items():
                print(f"\n{page}:")
                print(f"  {comment}")
            
            results[member] = analysis
        
        print(f"\n{'=' * 80}")
        print("Step 2 프로토타입 완료")
        print(f"{'=' * 80}")
        print(f"\n생성된 파일:")
        for member in target_members:
            print(f"  - output/analysis/{member}_analysis.json")
        
        return results


if __name__ == '__main__':
    discovery = PatternDiscovery()
    results = discovery.run_prototype()
    
    print("\n✓ Step 2 프로토타입 완료. 코멘트 품질 검증 후 전체 확장 진행.")
