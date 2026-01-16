import json

with open('output/data/member_statistics.json', encoding='utf-8') as f:
    data = json.load(f)

jungseo = data['정서린']

print('=== 정서린 종족별 성과 ===')
for race, stats in jungseo['by_opponent_race'].items():
    print(f"{race}: {stats['total_games']}경기, {stats['win_rate']}%")

print('\n=== 맵별 성과 ===')
for map_name, stats in sorted(jungseo['by_map'].items(), key=lambda x: x[1]['total_games'], reverse=True):
    print(f"{map_name}: {stats['total_games']}경기, {stats['win_rate']}%")

print('\n=== 상대별 성과 (상위 10개, 경기수 순) ===')
opps = sorted(jungseo['by_opponent'].items(), key=lambda x: x[1]['total_games'], reverse=True)[:10]
for opp, stats in opps:
    print(f"{opp}: {stats['total_games']}경기, {stats['win_rate']}%")
