import json

analysis = json.load(open('output/analysis/정서린_analysis.json', 'r', encoding='utf-8'))
print('약점 종족 주요 상대:')
breakdown = analysis['deep_analysis']['테란전_약점']['opponent_breakdown']
for name, stats in list(breakdown.items())[:5]:
    print(f'  {name}: {stats["games"]}경기, {stats["win_rate"]:.1f}%')
