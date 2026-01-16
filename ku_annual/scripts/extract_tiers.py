import pandas as pd

# Read Excel data
df = pd.read_excel('kuniv_2025_data.xlsx')

print('=== 전체 데이터 정보 ===')
print(f'총 경기 수: {len(df)}')
print(f'데이터 기간: {df["날짜"].min()} ~ {df["날짜"].max()}')
print()

# Get unique member-tier combinations
member_tiers = df[['멤버 이름', '멤버 티어']].drop_duplicates()
print(f'총 멤버-티어 조합: {len(member_tiers)}개')
print()

# For each member, get the latest tier based on most recent game date
print('=== 각 멤버의 최신 티어 (마지막 경기 기준) ===')
latest_tiers = []
for member in df['멤버 이름'].unique():
    member_df = df[df['멤버 이름'] == member]
    latest_game = member_df.loc[member_df['날짜'].idxmax()]
    latest_tiers.append({
        '멤버 이름': member,
        '최신 티어': latest_game['멤버 티어'],
        '최신 종족': latest_game['멤버 종족'],
        '마지막 경기일': latest_game['날짜'],
        '총 경기수': len(member_df)
    })

latest_df = pd.DataFrame(latest_tiers)

# Define tier order
tier_order = ['2티어', '3티어', '4티어', '5티어', '6티어', '7티어', '8티어', '베이비']
latest_df['티어순서'] = latest_df['최신 티어'].map({tier: i for i, tier in enumerate(tier_order)})
latest_df = latest_df.sort_values('티어순서')

print(latest_df[['멤버 이름', '최신 티어', '최신 종족', '총 경기수', '마지막 경기일']].to_string(index=False))
print(f'\n총 {len(latest_df)}명')
