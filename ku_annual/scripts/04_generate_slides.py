"""
Step 4: HTML 슬라이드 생성 (프로토타입: 정서린)

Jinja2 템플릿 기반 HTML 슬라이드 생성
- 해상도: 1920x1080px
- 레퍼런스 디자인 스타일 적용
- 5페이지: 표지, 성과, 종족, 맵, 티어
"""

import json
from pathlib import Path
from jinja2 import Template
import base64

class SlideGenerator:
    def __init__(self):
        """슬라이드 생성기 초기화"""
        self.base_dir = Path(__file__).parent.parent
        self.output_dir = self.base_dir / 'output'
        self.charts_dir = self.output_dir / 'charts'
        self.slides_dir = self.output_dir / 'slides'
        self.slides_dir.mkdir(parents=True, exist_ok=True)
        
        # 분석 데이터 로드
        self.member_stats = self._load_json('data/member_statistics.json')
        
        # 프로토타입 멤버
        self.prototype_member = '정서린'
        
        # 분석 파일 로드
        analysis_file = self.output_dir / 'analysis' / f'{self.prototype_member}_analysis.json'
        with open(analysis_file, 'r', encoding='utf-8') as f:
            self.analysis = json.load(f)
        
        print("✓ 데이터 로드 완료")
        print(f"  - 프로토타입 대상: {self.prototype_member}")
    
    def _load_json(self, relative_path):
        """JSON 파일 로드"""
        file_path = self.output_dir / relative_path
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _image_to_base64(self, image_path):
        """이미지를 base64로 인코딩"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def _get_base_style(self):
        """공통 스타일 CSS"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            width: 1920px;
            height: 1080px;
            font-family: 'Malgun Gothic', sans-serif;
            background: linear-gradient(135deg, #0a0e1a 0%, #1a2332 100%);
            color: #ffffff;
            overflow: hidden;
            position: relative;
        }
        
        .container {
            width: 100%;
            height: 100%;
            padding: 80px 100px;
            display: flex;
            flex-direction: column;
        }
        
        .title {
            font-size: 72px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 20px;
        }
        
        .subtitle {
            font-size: 36px;
            color: #9ca3af;
            margin-bottom: 60px;
        }
        
        .section-title {
            font-size: 48px;
            font-weight: bold;
            color: #3b82f6;
            margin-bottom: 30px;
        }
        
        .content {
            flex: 1;
            display: flex;
            gap: 60px;
        }
        
        .left-column {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 40px;
        }
        
        .right-column {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .stat-box {
            background: rgba(59, 130, 246, 0.1);
            border: 2px solid #3b82f6;
            border-radius: 16px;
            padding: 30px 40px;
        }
        
        .stat-label {
            font-size: 28px;
            color: #9ca3af;
            margin-bottom: 12px;
        }
        
        .stat-value {
            font-size: 56px;
            font-weight: bold;
            color: #ffffff;
        }
        
        .comment-box {
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
            padding: 30px 40px;
        }
        
        .comment-text {
            font-size: 28px;
            line-height: 1.6;
            color: #e5e7eb;
        }
        
        .chart-container {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chart-container img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        
        .watermark {
            position: absolute;
            bottom: 30px;
            right: 50px;
            font-size: 24px;
            color: rgba(255, 255, 255, 0.3);
            font-weight: bold;
        }
        """
    
    def generate_page_1_cover(self, member_name):
        """Page 1: 표지"""
        stats = self.member_stats[member_name]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{member_name} - 2025 Performance Report</title>
            <style>
                {self._get_base_style()}
                
                .cover-container {{
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100%;
                }}
                
                .member-name {{
                    font-size: 120px;
                    font-weight: bold;
                    color: #ffffff;
                    margin-bottom: 40px;
                }}
                
                .member-info {{
                    font-size: 48px;
                    color: #3b82f6;
                    margin-bottom: 80px;
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 40px;
                    width: 100%;
                    max-width: 1400px;
                }}
                
                .cover-stat-box {{
                    background: rgba(59, 130, 246, 0.1);
                    border: 2px solid #3b82f6;
                    border-radius: 16px;
                    padding: 40px;
                    text-align: center;
                }}
                
                .cover-stat-label {{
                    font-size: 32px;
                    color: #9ca3af;
                    margin-bottom: 20px;
                }}
                
                .cover-stat-value {{
                    font-size: 64px;
                    font-weight: bold;
                    color: #ffffff;
                }}
            </style>
        </head>
        <body>
            <div class="cover-container">
                <div class="member-name">{member_name}</div>
                <div class="member-info">{stats['basic_info']['race']} · {stats['basic_info']['last_tier']}</div>
                <div class="stats-grid">
                    <div class="cover-stat-box">
                        <div class="cover-stat-label">총 경기수</div>
                        <div class="cover-stat-value">{stats['overall']['total_games']}</div>
                    </div>
                    <div class="cover-stat-box">
                        <div class="cover-stat-label">전체 승률</div>
                        <div class="cover-stat-value">{stats['overall']['win_rate']}%</div>
                    </div>
                    <div class="cover-stat-box">
                        <div class="cover-stat-label">승 / 패</div>
                        <div class="cover-stat-value">{stats['overall']['wins']} / {stats['overall']['losses']}</div>
                    </div>
                </div>
            </div>
            <div class="watermark">HMD</div>
        </body>
        </html>
        """
        
        output_path = self.slides_dir / f'{member_name}_page_1_cover.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def generate_page_2_performance(self, member_name):
        """Page 2: 성과 세부 내역"""
        comment = self.analysis['comments']['page_2_performance']
        
        # 차트 이미지를 base64로 인코딩
        chart_paths = [
            self.charts_dir / f'{member_name}_monthly_trend.png',
            self.charts_dir / f'{member_name}_performance_breakdown.png'
        ]
        
        chart_images = [self._image_to_base64(p) for p in chart_paths]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{member_name} - 성과 세부 내역</title>
            <style>
                {self._get_base_style()}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="title">{member_name}</div>
                <div class="subtitle">성과 세부 내역</div>
                
                <div class="content">
                    <div class="left-column">
                        <div class="chart-container">
                            <img src="data:image/png;base64,{chart_images[0]}" alt="월별 추세">
                        </div>
                    </div>
                    <div class="right-column">
                        <div style="width: 100%; display: flex; flex-direction: column; gap: 40px;">
                            <div class="chart-container" style="height: 400px;">
                                <img src="data:image/png;base64,{chart_images[1]}" alt="성과 세부">
                            </div>
                            <div class="comment-box">
                                <div class="comment-text">{comment}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="watermark">HMD</div>
        </body>
        </html>
        """
        
        output_path = self.slides_dir / f'{member_name}_page_2_performance.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def generate_page_3_race(self, member_name):
        """Page 3: 종족별 성과 비교"""
        comment = self.analysis['comments']['page_3_race']
        
        # 차트 이미지 2개
        chart_paths = [
            self.charts_dir / f'{member_name}_race_comparison.png',
            self.charts_dir / f'{member_name}_race_opponents.png'
        ]
        
        # 파일 존재 확인
        chart_images = []
        for path in chart_paths:
            if path.exists():
                chart_images.append(self._image_to_base64(path))
            else:
                chart_images.append(None)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{member_name} - 종족별 성과 비교</title>
            <style>
                {self._get_base_style()}
                
                .comment-section {{
                    background: rgba(255, 255, 255, 0.05);
                    border-left: 4px solid #3b82f6;
                    border-radius: 8px;
                    padding: 24px 32px;
                    margin-bottom: 40px;
                }}
                
                .comment-section .comment-text {{
                    font-size: 24px;
                    line-height: 1.5;
                    color: #e5e7eb;
                }}
                
                .charts-row {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 40px;
                    flex: 1;
                }}
                
                .chart-box {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                .chart-box img {{
                    max-width: 100%;
                    max-height: 100%;
                    object-fit: contain;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="title">{member_name}</div>
                <div class="subtitle">상대 종족별 비교</div>
                
                <div class="comment-section">
                    <div class="comment-text">{comment}</div>
                </div>
                
                <div class="charts-row">
                    {"<div class='chart-box'><img src='data:image/png;base64," + chart_images[0] + "' alt='종족별 비교'></div>" if chart_images[0] else "<div class='chart-box'>차트 없음</div>"}
                    {"<div class='chart-box'><img src='data:image/png;base64," + chart_images[1] + "' alt='주요 상대별 전적'></div>" if chart_images[1] else "<div class='chart-box'>차트 없음</div>"}
                </div>
            </div>
            <div class="watermark">HMD</div>
        </body>
        </html>
        """
        
        output_path = self.slides_dir / f'{member_name}_page_3_race.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def generate_page_4_map(self, member_name):
        """Page 4: 맵별 성과 비교"""
        comment = self.analysis['comments']['page_4_map']
        
        # 차트 이미지 2개
        chart_paths = [
            self.charts_dir / f'{member_name}_map_comparison.png',
            self.charts_dir / f'{member_name}_map_opponents.png'
        ]
        
        # 파일 존재 확인
        chart_images = []
        for path in chart_paths:
            if path.exists():
                chart_images.append(self._image_to_base64(path))
            else:
                chart_images.append(None)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{member_name} - 맵별 성과 비교</title>
            <style>
                {self._get_base_style()}
                
                .comment-section {{
                    background: rgba(255, 255, 255, 0.05);
                    border-left: 4px solid #3b82f6;
                    border-radius: 8px;
                    padding: 24px 32px;
                    margin-bottom: 40px;
                }}
                
                .comment-section .comment-text {{
                    font-size: 24px;
                    line-height: 1.5;
                    color: #e5e7eb;
                }}
                
                .charts-row {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 40px;
                    flex: 1;
                }}
                
                .chart-box {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                .chart-box img {{
                    max-width: 100%;
                    max-height: 100%;
                    object-fit: contain;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="title">{member_name}</div>
                <div class="subtitle">주요 맵별 비교</div>
                
                <div class="comment-section">
                    <div class="comment-text">{comment}</div>
                </div>
                
                <div class="charts-row">
                    {"<div class='chart-box'><img src='data:image/png;base64," + chart_images[0] + "' alt='맵별 비교'></div>" if chart_images[0] else "<div class='chart-box'>차트 없음</div>"}
                    {"<div class='chart-box'><img src='data:image/png;base64," + chart_images[1] + "' alt='주요 상대별 전적'></div>" if chart_images[1] else "<div class='chart-box'>차트 없음</div>"}
                </div>
            </div>
            <div class="watermark">HMD</div>
        </body>
        </html>
        """
        
        output_path = self.slides_dir / f'{member_name}_page_4_map.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def generate_page_5_tier(self, member_name):
        """Page 5: 티어별 성과 비교"""
        comment = self.analysis['comments']['page_5_tier']
        
        # 차트 이미지 2개
        chart_paths = [
            self.charts_dir / f'{member_name}_tier_comparison.png',
            self.charts_dir / f'{member_name}_tier_opponents.png'
        ]
        
        # 파일 존재 확인
        chart_images = []
        for path in chart_paths:
            if path.exists():
                chart_images.append(self._image_to_base64(path))
            else:
                chart_images.append(None)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{member_name} - 티어별 성과 비교</title>
            <style>
                {self._get_base_style()}
                
                .comment-section {{
                    background: rgba(255, 255, 255, 0.05);
                    border-left: 4px solid #3b82f6;
                    border-radius: 8px;
                    padding: 24px 32px;
                    margin-bottom: 40px;
                }}
                
                .comment-section .comment-text {{
                    font-size: 24px;
                    line-height: 1.5;
                    color: #e5e7eb;
                }}
                
                .charts-row {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 40px;
                    flex: 1;
                }}
                
                .chart-box {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                .chart-box img {{
                    max-width: 100%;
                    max-height: 100%;
                    object-fit: contain;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="title">{member_name}</div>
                <div class="subtitle">상대 티어별 비교</div>
                
                <div class="comment-section">
                    <div class="comment-text">{comment}</div>
                </div>
                
                <div class="charts-row">
                    {"<div class='chart-box'><img src='data:image/png;base64," + chart_images[0] + "' alt='티어별 비교'></div>" if chart_images[0] else "<div class='chart-box'>차트 없음</div>"}
                    {"<div class='chart-box'><img src='data:image/png;base64," + chart_images[1] + "' alt='주요 상대별 전적'></div>" if chart_images[1] else "<div class='chart-box'>차트 없음</div>"}
                </div>
            </div>
            <div class="watermark">HMD</div>
        </body>
        </html>
        """
        
        output_path = self.slides_dir / f'{member_name}_page_5_tier.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def generate_all_slides(self, member_name):
        """멤버의 모든 슬라이드 생성"""
        print(f"\n{member_name} 슬라이드 생성 시작...\n")
        
        pages = [
            ('page_1_cover', self.generate_page_1_cover),
            ('page_2_performance', self.generate_page_2_performance),
            ('page_3_race', self.generate_page_3_race),
            ('page_4_map', self.generate_page_4_map),
            ('page_5_tier', self.generate_page_5_tier)
        ]
        
        generated_files = []
        
        for i, (page_name, generator_func) in enumerate(pages, 1):
            print(f"[{i}/5] {member_name} - {page_name} 생성 중...")
            output_path = generator_func(member_name)
            print(f"  ✓ 저장: {output_path.relative_to(self.base_dir)}")
            generated_files.append(output_path)
        
        return generated_files

def main():
    print("=" * 80)
    print("Step 4: HTML 슬라이드 생성 (프로토타입: 정서린)")
    print("=" * 80)
    print()
    
    generator = SlideGenerator()
    
    # 정서린 슬라이드 생성
    files = generator.generate_all_slides(generator.prototype_member)
    
    print()
    print("=" * 80)
    print("Step 4 완료: HTML 슬라이드 생성 성공")
    print("=" * 80)
    print()
    print(f"생성된 슬라이드 (5개):")
    for f in files:
        print(f"  - {f.name}")
    print()
    print("✓ Step 4 HTML 슬라이드 생성 완료. Step 5 (PNG 변환) 준비 완료.")

if __name__ == '__main__':
    main()
