"""
Step 4: HTML 슬라이드 생성 v2 (HTML/CSS 차트 직접 구현)

matplotlib 차트 이미지 대신 HTML/CSS로 차트 직접 렌더링
- 레퍼런스 디자인 완벽 재현
- 막대 내부 라벨, 그라데이션, 통일된 스타일
- 기업 분석보고서 수준의 디자인
"""

import json
from pathlib import Path

class SlideGeneratorV2:
    def __init__(self):
        """슬라이드 생성기 초기화"""
        self.base_dir = Path(__file__).parent.parent
        self.output_dir = self.base_dir / 'output'
        self.slides_dir = self.output_dir / 'slides_v2'
        self.slides_dir.mkdir(parents=True, exist_ok=True)
        
        # 데이터 로드
        self.member_stats = self._load_json('data/member_statistics.json')
        
        # 색상 팔레트
        self.colors = {
            'bg_dark': '#0a0e1a',
            'bg_light': '#1a2332',
            'text_white': '#ffffff',
            'text_gray': '#9ca3af',
            'text_light_gray': '#e5e7eb',
            'bar_gray': '#4b5563',
            'bar_gray_light': '#6b7280',
            'line_blue': '#3b82f6',
            'accent_blue': '#0066ff',
            'border_white': 'rgba(255,255,255,0.3)',
        }
        
        print("✓ 데이터 로드 완료")
        print(f"  - HTML/CSS 차트 직접 렌더링 모드")
    
    def _load_json(self, relative_path):
        """JSON 파일 로드"""
        file_path = self.output_dir / relative_path
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _get_base_style(self):
        """공통 스타일 CSS"""
        return f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            width: 1920px;
            height: 1080px;
            font-family: 'Malgun Gothic', sans-serif;
            background: linear-gradient(135deg, {self.colors['bg_dark']} 0%, {self.colors['bg_light']} 100%);
            color: {self.colors['text_white']};
            overflow: hidden;
            position: relative;
        }}
        
        .container {{
            width: 100%;
            height: 100%;
            padding: 80px 100px;
            display: flex;
            flex-direction: column;
        }}
        
        .title {{
            font-size: 72px;
            font-weight: bold;
            color: {self.colors['text_white']};
            margin-bottom: 20px;
        }}
        
        .subtitle {{
            font-size: 36px;
            color: {self.colors['text_gray']};
            margin-bottom: 60px;
        }}
        
        .watermark {{
            position: absolute;
            bottom: 40px;
            right: 60px;
            font-size: 24px;
            color: {self.colors['text_gray']};
            opacity: 0.5;
        }}
        """
    
    def _get_top_opponents(self, analysis):
        """약점 종족 주요 상대 5명 추출
        
        Args:
            analysis: 분석 JSON 데이터
            
        Returns:
            [(상대이름, 경기수, 승률), ...] 또는 None
        """
        # 약점 종족 찾기
        weak_race = None
        for weakness in analysis.get('weaknesses', []):
            if weakness.get('category') == 'race_matchup' and 'weak_race' in weakness.get('details', {}):
                weak_race = weakness['details']['weak_race']
                break
        
        if not weak_race:
            return None
        
        # deep_analysis에서 주요 상대 찾기
        deep_key = f"{weak_race}전_약점"
        if deep_key not in analysis.get('deep_analysis', {}):
            return None
        
        opponent_breakdown = analysis['deep_analysis'][deep_key].get('opponent_breakdown', {})
        
        # [(이름, 경기수, 승률), ...] 형식으로 변환
        opponents_data = []
        for name, stats in opponent_breakdown.items():
            opponents_data.append((name, stats['games'], stats['win_rate']))
        
        # 경기수 순으로 정렬 (이미 정렬되어 있지만 확실하게)
        opponents_data.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 5명
        return opponents_data[:5]
    
    def _create_bar_chart_svg(self, data, max_games, chart_width=800, chart_height=400):
        """막대 차트 SVG 생성 (선 없음)
        
        Args:
            data: [(label, games, win_rate), ...]
            max_games: 최대 경기수 (Y축 범위)
            chart_width: 차트 너비
            chart_height: 차트 높이
        """
        margin_left = 80
        margin_right = 80
        margin_top = 40
        margin_bottom = 60
        
        plot_width = chart_width - margin_left - margin_right
        plot_height = chart_height - margin_top - margin_bottom
        
        num_bars = len(data)
        bar_width = plot_width / num_bars * 0.6
        bar_gap = plot_width / num_bars * 0.4
        
        svg_parts = []
        
        svg_parts.append(f'<svg width="{chart_width}" height="{chart_height}" xmlns="http://www.w3.org/2000/svg">')
        
        y_ticks = [0, max_games // 2, max_games]
        for tick in y_ticks:
            y = margin_top + plot_height - (tick / max_games * plot_height)
            svg_parts.append(f'<line x1="{margin_left}" y1="{y}" x2="{chart_width - margin_right}" y2="{y}" stroke="{self.colors["text_gray"]}" stroke-width="1" opacity="0.2"/>')
            svg_parts.append(f'<text x="{margin_left - 10}" y="{y + 5}" text-anchor="end" fill="{self.colors["text_gray"]}" font-size="14">{tick}</text>')
        
        svg_parts.append(f'<text x="{margin_left - 60}" y="{margin_top + plot_height / 2}" text-anchor="middle" fill="{self.colors["text_white"]}" font-size="16" font-weight="bold" transform="rotate(-90, {margin_left - 60}, {margin_top + plot_height / 2})">경기수</text>')
        
        wr_ticks = [0, 50, 100]
        for tick in wr_ticks:
            y = margin_top + plot_height - (tick / 100 * plot_height)
            svg_parts.append(f'<text x="{chart_width - margin_right + 10}" y="{y + 5}" text-anchor="start" fill="{self.colors["text_gray"]}" font-size="14">{tick}%</text>')
        
        svg_parts.append(f'<text x="{chart_width - margin_right + 60}" y="{margin_top + plot_height / 2}" text-anchor="middle" fill="{self.colors["text_white"]}" font-size="16" font-weight="bold" transform="rotate(90, {chart_width - margin_right + 60}, {margin_top + plot_height / 2})">승률 (%)</text>')
        
        for i, (label, games, win_rate) in enumerate(data):
            x = margin_left + i * (plot_width / num_bars) + bar_gap / 2
            bar_height = (games / max_games) * plot_height
            y_bar = margin_top + plot_height - bar_height
            
            gradient_id = f"grad_{i}"
            svg_parts.append(f'''
            <defs>
                <linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:{self.colors["bar_gray_light"]};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:{self.colors["bar_gray"]};stop-opacity:1" />
                </linearGradient>
            </defs>
            ''')
            
            svg_parts.append(f'<rect x="{x}" y="{y_bar}" width="{bar_width}" height="{bar_height}" fill="url(#{gradient_id})" rx="4"/>')
            
            label_y = y_bar + bar_height / 2
            svg_parts.append(f'<text x="{x + bar_width / 2}" y="{label_y + 5}" text-anchor="middle" fill="{self.colors["text_white"]}" font-size="18" font-weight="bold">{games}</text>')
            
            svg_parts.append(f'<text x="{x + bar_width / 2}" y="{chart_height - margin_bottom + 25}" text-anchor="middle" fill="{self.colors["text_gray"]}" font-size="16">{label}</text>')
            
            wr_y = margin_top + plot_height - (win_rate / 100 * plot_height)
            svg_parts.append(f'<text x="{x + bar_width / 2}" y="{wr_y - 15}" text-anchor="middle" fill="{self.colors["line_blue"]}" font-size="16" font-weight="bold">{win_rate:.1f}%</text>')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def _create_area_chart_svg(self, data, chart_width=800, chart_height=400):
        """영역 차트 SVG 생성 (월별 승률 추이)
        
        Args:
            data: [(month, win_rate), ...] (예: [("01", 50.0), ("02", 60.0)])
            chart_width: 차트 너비
            chart_height: 차트 높이
        """
        margin_left = 60
        margin_right = 40
        margin_top = 40
        margin_bottom = 60
        
        plot_width = chart_width - margin_left - margin_right
        plot_height = chart_height - margin_top - margin_bottom
        
        svg_parts = []
        svg_parts.append(f'<svg width="{chart_width}" height="{chart_height}" xmlns="http://www.w3.org/2000/svg">')
        
        svg_parts.append(f'''
        <defs>
            <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{self.colors["line_blue"]};stop-opacity:0.6" />
                <stop offset="100%" style="stop-color:{self.colors["line_blue"]};stop-opacity:0.1" />
            </linearGradient>
        </defs>
        ''')
        
        y_ticks = [0, 50, 100]
        for tick in y_ticks:
            y = margin_top + plot_height - (tick / 100 * plot_height)
            svg_parts.append(f'<line x1="{margin_left}" y1="{y}" x2="{chart_width - margin_right}" y2="{y}" stroke="{self.colors["text_gray"]}" stroke-width="1" opacity="0.2"/>')
            svg_parts.append(f'<text x="{margin_left - 10}" y="{y + 5}" text-anchor="end" fill="{self.colors["text_gray"]}" font-size="14">{tick}%</text>')
        
        svg_parts.append(f'<text x="{margin_left - 50}" y="{margin_top + plot_height / 2}" text-anchor="middle" fill="{self.colors["text_white"]}" font-size="16" font-weight="bold" transform="rotate(-90, {margin_left - 50}, {margin_top + plot_height / 2})">승률 (%)</text>')
        
        if not data:
            svg_parts.append('</svg>')
            return '\n'.join(svg_parts)
        
        num_points = len(data)
        x_step = plot_width / (num_points - 1) if num_points > 1 else plot_width
        
        points = []
        for i, (month, win_rate) in enumerate(data):
            x = margin_left + i * x_step if num_points > 1 else margin_left + plot_width / 2
            y = margin_top + plot_height - (win_rate / 100 * plot_height)
            points.append((x, y, month, win_rate))
        
        path_d = f"M {margin_left} {margin_top + plot_height}"
        if points:
            path_d += f" L {points[0][0]} {points[0][1]}"
            for x, y, _, _ in points[1:]:
                path_d += f" L {x} {y}"
            path_d += f" L {points[-1][0]} {margin_top + plot_height}"
        path_d += " Z"
        
        svg_parts.append(f'<path d="{path_d}" fill="url(#areaGradient)"/>')
        
        line_d = f"M {points[0][0]} {points[0][1]}"
        for x, y, _, _ in points[1:]:
            line_d += f" L {x} {y}"
        svg_parts.append(f'<path d="{line_d}" stroke="{self.colors["line_blue"]}" stroke-width="3" fill="none"/>')
        
        for x, y, month, win_rate in points:
            svg_parts.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{self.colors["line_blue"]}" stroke="{self.colors["bg_dark"]}" stroke-width="2"/>')
            svg_parts.append(f'<text x="{x}" y="{y - 15}" text-anchor="middle" fill="{self.colors["line_blue"]}" font-size="16" font-weight="bold">{win_rate:.1f}%</text>')
            svg_parts.append(f'<text x="{x}" y="{chart_height - margin_bottom + 25}" text-anchor="middle" fill="{self.colors["text_gray"]}" font-size="16">{month}</text>')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def _create_bar_line_chart_svg(self, data, max_games, chart_width=800, chart_height=400):
        """막대+선 복합 차트 SVG 생성
        
        Args:
            data: [(label, games, win_rate), ...]
            max_games: 최대 경기수 (Y축 범위)
            chart_width: 차트 너비
            chart_height: 차트 높이
        """
        margin_left = 80
        margin_right = 80
        margin_top = 40
        margin_bottom = 60
        
        plot_width = chart_width - margin_left - margin_right
        plot_height = chart_height - margin_top - margin_bottom
        
        num_bars = len(data)
        bar_width = plot_width / num_bars * 0.6
        bar_gap = plot_width / num_bars * 0.4
        
        svg_parts = []
        
        # SVG 시작
        svg_parts.append(f'<svg width="{chart_width}" height="{chart_height}" xmlns="http://www.w3.org/2000/svg">')
        
        # Y축 (경기수)
        y_ticks = [0, max_games // 2, max_games]
        for tick in y_ticks:
            y = margin_top + plot_height - (tick / max_games * plot_height)
            svg_parts.append(f'<line x1="{margin_left}" y1="{y}" x2="{chart_width - margin_right}" y2="{y}" stroke="{self.colors["text_gray"]}" stroke-width="1" opacity="0.2"/>')
            svg_parts.append(f'<text x="{margin_left - 10}" y="{y + 5}" text-anchor="end" fill="{self.colors["text_gray"]}" font-size="14">{tick}</text>')
        
        # Y축 레이블 (경기수)
        svg_parts.append(f'<text x="{margin_left - 60}" y="{margin_top + plot_height / 2}" text-anchor="middle" fill="{self.colors["text_white"]}" font-size="16" font-weight="bold" transform="rotate(-90, {margin_left - 60}, {margin_top + plot_height / 2})">경기수</text>')
        
        # Y축 2 (승률%)
        wr_ticks = [0, 50, 100]
        for tick in wr_ticks:
            y = margin_top + plot_height - (tick / 100 * plot_height)
            svg_parts.append(f'<text x="{chart_width - margin_right + 10}" y="{y + 5}" text-anchor="start" fill="{self.colors["text_gray"]}" font-size="14">{tick}%</text>')
        
        # Y축 2 레이블 (승률)
        svg_parts.append(f'<text x="{chart_width - margin_right + 60}" y="{margin_top + plot_height / 2}" text-anchor="middle" fill="{self.colors["text_white"]}" font-size="16" font-weight="bold" transform="rotate(90, {chart_width - margin_right + 60}, {margin_top + plot_height / 2})">승률 (%)</text>')
        
        # 막대 + 선 포인트
        line_points = []
        for i, (label, games, win_rate) in enumerate(data):
            # 막대 X 위치
            x = margin_left + i * (plot_width / num_bars) + bar_gap / 2
            
            # 막대 높이
            bar_height = (games / max_games) * plot_height
            y_bar = margin_top + plot_height - bar_height
            
            # 그라데이션 막대
            gradient_id = f"grad_{i}"
            svg_parts.append(f'''
            <defs>
                <linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:{self.colors["bar_gray_light"]};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:{self.colors["bar_gray"]};stop-opacity:1" />
                </linearGradient>
            </defs>
            ''')
            
            svg_parts.append(f'<rect x="{x}" y="{y_bar}" width="{bar_width}" height="{bar_height}" fill="url(#{gradient_id})" rx="4"/>')
            
            # 막대 내부 경기수 라벨
            label_y = y_bar + bar_height / 2
            svg_parts.append(f'<text x="{x + bar_width / 2}" y="{label_y + 5}" text-anchor="middle" fill="{self.colors["text_white"]}" font-size="18" font-weight="bold">{games}</text>')
            
            # X축 라벨
            svg_parts.append(f'<text x="{x + bar_width / 2}" y="{chart_height - margin_bottom + 25}" text-anchor="middle" fill="{self.colors["text_gray"]}" font-size="16">{label}</text>')
            
            # 선 포인트 계산
            wr_y = margin_top + plot_height - (win_rate / 100 * plot_height)
            line_points.append((x + bar_width / 2, wr_y, win_rate))
        
        # 선 그리기
        if len(line_points) > 1:
            path_d = f"M {line_points[0][0]} {line_points[0][1]}"
            for x, y, _ in line_points[1:]:
                path_d += f" L {x} {y}"
            svg_parts.append(f'<path d="{path_d}" stroke="{self.colors["line_blue"]}" stroke-width="3" fill="none"/>')
        
        # 선 포인트 + 승률 라벨
        for x, y, win_rate in line_points:
            svg_parts.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{self.colors["line_blue"]}" stroke="{self.colors["bg_dark"]}" stroke-width="2"/>')
            svg_parts.append(f'<text x="{x}" y="{y - 15}" text-anchor="middle" fill="{self.colors["line_blue"]}" font-size="16" font-weight="bold">{win_rate:.1f}%</text>')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def generate_page_3_race(self, member_name):
        """Page 3: 종족별 성과 비교 (HTML/CSS 차트)"""
        # 분석 JSON 로드
        analysis_file = self.output_dir / 'analysis' / f'{member_name}_analysis.json'
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
        
        comment = analysis['comments']['page_3_race']
        stats = self.member_stats[member_name]
        
        # 종족별 데이터
        race_stats = stats['by_opponent_race']
        races = ['테란', '저그', '프로토스']
        chart_data = [(r, race_stats[r]['total_games'], race_stats[r]['win_rate']) for r in races]
        max_games = max(race_stats[r]['total_games'] for r in races)
        
        # 차트 1: 종족별 비교
        chart1_svg = self._create_bar_line_chart_svg(chart_data, max_games, chart_width=800, chart_height=400)
        
        # 차트 2: 약점 종족 주요 상대
        top_opponents = self._get_top_opponents(analysis)
        if top_opponents:
            opponent_chart_data = top_opponents
            max_opponent_games = max(games for _, games, _ in opponent_chart_data)
            chart2_svg = self._create_bar_line_chart_svg(opponent_chart_data, max_opponent_games, chart_width=800, chart_height=400)
        else:
            chart2_svg = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #9ca3af; font-size: 20px;">데이터 없음</div>'
        
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
                    border-left: 4px solid {self.colors['accent_blue']};
                    border-radius: 8px;
                    padding: 24px 32px;
                    margin-bottom: 40px;
                }}
                
                .comment-text {{
                    font-size: 24px;
                    line-height: 1.5;
                    color: {self.colors['text_light_gray']};
                }}
                
                .charts-row {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 40px;
                    flex: 1;
                }}
                
                .chart-container {{
                    background: rgba(255, 255, 255, 0.02);
                    border: 1px solid {self.colors['border_white']};
                    border-radius: 12px;
                    padding: 30px;
                    display: flex;
                    flex-direction: column;
                }}
                
                .chart-title {{
                    font-size: 22px;
                    font-weight: bold;
                    color: {self.colors['text_white']};
                    margin-bottom: 20px;
                    text-align: center;
                }}
                
                .chart-content {{
                    flex: 1;
                    display: flex;
                    align-items: center;
                    justify-content: center;
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
                    <div class="chart-container">
                        <div class="chart-title">종족별 전적 비교</div>
                        <div class="chart-content">
                            {chart1_svg}
                        </div>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">주요 상대별 전적</div>
                        <div class="chart-content">
                            {chart2_svg}
                        </div>
                    </div>
                </div>
            </div>
            <div class="watermark">HMD</div>
        </body>
        </html>
        """
        
        output_path = self.slides_dir / f'{member_name}_page_3_race.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ 생성: {output_path}")
        
        return output_path
    
    def generate_page_2_performance(self, member_name):
        """Page 2: 전적 상세 (타입별 + 월별 승률)"""
        analysis_file = self.output_dir / 'analysis' / f'{member_name}_analysis.json'
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
        
        comment = analysis['comments']['page_2_performance']
        stats = self.member_stats[member_name]
        
        type_stats = stats['by_type']
        type_data = []
        for type_name in ['스폰', '대회']:
            if type_name in type_stats:
                type_data.append((type_name, type_stats[type_name]['total_games'], type_stats[type_name]['win_rate']))
        
        max_type_games = max(t[1] for t in type_data) if type_data else 1
        chart1_svg = self._create_bar_chart_svg(type_data, max_type_games, chart_width=800, chart_height=400)
        
        month_stats = stats['by_month']
        months_with_data = []
        for month_key in sorted(month_stats.keys()):
            month_data = month_stats[month_key]
            if month_data['total_games'] > 0:
                month_label = month_key.split('-')[1]
                months_with_data.append((month_label, month_data['win_rate']))
        
        chart2_svg = self._create_area_chart_svg(months_with_data, chart_width=800, chart_height=400)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{member_name} - 전적 상세</title>
            <style>
                {self._get_base_style()}
                
                .comment-section {{
                    background: rgba(255, 255, 255, 0.05);
                    border-left: 4px solid {self.colors['accent_blue']};
                    border-radius: 8px;
                    padding: 24px 32px;
                    margin-bottom: 40px;
                }}
                
                .comment-text {{
                    font-size: 24px;
                    line-height: 1.5;
                    color: {self.colors['text_light_gray']};
                }}
                
                .charts-row {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 40px;
                    flex: 1;
                }}
                
                .chart-container {{
                    background: rgba(255, 255, 255, 0.02);
                    border: 1px solid {self.colors['border_white']};
                    border-radius: 12px;
                    padding: 30px;
                    display: flex;
                    flex-direction: column;
                }}
                
                .chart-title {{
                    font-size: 22px;
                    font-weight: bold;
                    color: {self.colors['text_white']};
                    margin-bottom: 20px;
                    text-align: center;
                }}
                
                .chart-content {{
                    flex: 1;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="title">{member_name}</div>
                <div class="subtitle">전적 상세</div>
                
                <div class="comment-section">
                    <div class="comment-text">{comment}</div>
                </div>
                
                <div class="charts-row">
                    <div class="chart-container">
                        <div class="chart-title">타입별 승률 비교</div>
                        <div class="chart-content">
                            {chart1_svg}
                        </div>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">월별 승률 추이</div>
                        <div class="chart-content">
                            {chart2_svg}
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
        
        print(f"✓ 생성: {output_path}")
        
        return output_path
    
    def generate_page_4_map(self, member_name):
        """Page 4: 맵별 성과 비교"""
        analysis_file = self.output_dir / 'analysis' / f'{member_name}_analysis.json'
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
        
        comment = analysis['comments']['page_4_map']
        stats = self.member_stats[member_name]
        
        map_stats = stats['by_map']
        map_data = []
        for map_name, map_info in sorted(map_stats.items(), key=lambda x: x[1]['total_games'], reverse=True)[:4]:
            map_data.append((map_name, map_info['total_games'], map_info['win_rate']))
        
        max_map_games = max(m[1] for m in map_data) if map_data else 1
        chart1_svg = self._create_bar_line_chart_svg(map_data, max_map_games, chart_width=800, chart_height=400)
        
        top_opponents = self._get_top_opponents(analysis)
        if top_opponents:
            max_opponent_games = max(games for _, games, _ in top_opponents)
            chart2_svg = self._create_bar_line_chart_svg(top_opponents, max_opponent_games, chart_width=800, chart_height=400)
        else:
            chart2_svg = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #9ca3af; font-size: 20px;">데이터 없음</div>'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{member_name} - 맵별 성과</title>
            <style>
                {self._get_base_style()}
                
                .comment-section {{
                    background: rgba(255, 255, 255, 0.05);
                    border-left: 4px solid {self.colors['accent_blue']};
                    border-radius: 8px;
                    padding: 24px 32px;
                    margin-bottom: 40px;
                }}
                
                .comment-text {{
                    font-size: 24px;
                    line-height: 1.5;
                    color: {self.colors['text_light_gray']};
                }}
                
                .charts-row {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 40px;
                    flex: 1;
                }}
                
                .chart-container {{
                    background: rgba(255, 255, 255, 0.02);
                    border: 1px solid {self.colors['border_white']};
                    border-radius: 12px;
                    padding: 30px;
                    display: flex;
                    flex-direction: column;
                }}
                
                .chart-title {{
                    font-size: 22px;
                    font-weight: bold;
                    color: {self.colors['text_white']};
                    margin-bottom: 20px;
                    text-align: center;
                }}
                
                .chart-content {{
                    flex: 1;
                    display: flex;
                    align-items: center;
                    justify-content: center;
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
                    <div class="chart-container">
                        <div class="chart-title">주요 맵별 전적 비교</div>
                        <div class="chart-content">
                            {chart1_svg}
                        </div>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">주요 상대별 전적</div>
                        <div class="chart-content">
                            {chart2_svg}
                        </div>
                    </div>
                </div>
            </div>
            <div class="watermark">HMD</div>
        </body>
        </html>
        """
        
        output_path = self.slides_dir / f'{member_name}_page_4_map.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ 생성: {output_path}")
        
        return output_path
    
    def generate_page_5_tier(self, member_name):
        """Page 5: 티어별 성과 비교"""
        analysis_file = self.output_dir / 'analysis' / f'{member_name}_analysis.json'
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
        
        comment = analysis['comments']['page_5_tier']
        stats = self.member_stats[member_name]
        
        tier_stats = stats['by_tier_matchup']
        tier_labels = {
            'upper': '상위 티어',
            'same': '동일 티어',
            'lower': '하위 티어'
        }
        
        tier_data = []
        for tier_key in ['upper', 'same', 'lower']:
            if tier_key in tier_stats and tier_stats[tier_key]['total_games'] > 0:
                tier_data.append((tier_labels[tier_key], tier_stats[tier_key]['total_games'], tier_stats[tier_key]['win_rate']))
        
        max_tier_games = max(t[1] for t in tier_data) if tier_data else 1
        chart1_svg = self._create_bar_line_chart_svg(tier_data, max_tier_games, chart_width=800, chart_height=400)
        
        opponent_stats = stats.get('by_opponent', {})
        top_opponents = sorted(opponent_stats.items(), key=lambda x: x[1]['total_games'], reverse=True)[:5]
        opponent_data = [(name, opp['total_games'], opp['win_rate']) for name, opp in top_opponents]
        
        if opponent_data:
            max_opponent_games = max(g for _, g, _ in opponent_data)
            chart2_svg = self._create_bar_line_chart_svg(opponent_data, max_opponent_games, chart_width=800, chart_height=400)
        else:
            chart2_svg = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #9ca3af; font-size: 20px;">데이터 없음</div>'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{member_name} - 티어별 성과</title>
            <style>
                {self._get_base_style()}
                
                .comment-section {{
                    background: rgba(255, 255, 255, 0.05);
                    border-left: 4px solid {self.colors['accent_blue']};
                    border-radius: 8px;
                    padding: 24px 32px;
                    margin-bottom: 40px;
                }}
                
                .comment-text {{
                    font-size: 24px;
                    line-height: 1.5;
                    color: {self.colors['text_light_gray']};
                }}
                
                .charts-row {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 40px;
                    flex: 1;
                }}
                
                .chart-container {{
                    background: rgba(255, 255, 255, 0.02);
                    border: 1px solid {self.colors['border_white']};
                    border-radius: 12px;
                    padding: 30px;
                    display: flex;
                    flex-direction: column;
                }}
                
                .chart-title {{
                    font-size: 22px;
                    font-weight: bold;
                    color: {self.colors['text_white']};
                    margin-bottom: 20px;
                    text-align: center;
                }}
                
                .chart-content {{
                    flex: 1;
                    display: flex;
                    align-items: center;
                    justify-content: center;
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
                    <div class="chart-container">
                        <div class="chart-title">상대 티어별 전적 비교</div>
                        <div class="chart-content">
                            {chart1_svg}
                        </div>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">주요 상대별 전적</div>
                        <div class="chart-content">
                            {chart2_svg}
                        </div>
                    </div>
                </div>
            </div>
            <div class="watermark">HMD</div>
        </body>
        </html>
        """
        
        output_path = self.slides_dir / f'{member_name}_page_5_tier.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ 생성: {output_path}")
        
        return output_path
    
    def generate_for_all_members(self, pages=['page_2', 'page_3', 'page_4', 'page_5']):
        """전체 멤버에 대해 슬라이드 생성
        
        Args:
            pages: 생성할 페이지 목록 (기본: 모든 페이지)
        """
        page_generators = {
            'page_2': self.generate_page_2_performance,
            'page_3': self.generate_page_3_race,
            'page_4': self.generate_page_4_map,
            'page_5': self.generate_page_5_tier
        }
        
        member_names = list(self.member_stats.keys())
        total_members = len(member_names)
        
        print(f"\n전체 {total_members}명 멤버에 대해 슬라이드 생성 시작...")
        print(f"생성할 페이지: {', '.join(pages)}")
        print("=" * 80)
        
        for idx, member_name in enumerate(member_names, 1):
            print(f"\n[{idx}/{total_members}] {member_name}")
            
            for page_key in pages:
                if page_key in page_generators:
                    page_name = {
                        'page_2': '전적 상세',
                        'page_3': '종족별 성과',
                        'page_4': '맵별 성과',
                        'page_5': '티어별 성과'
                    }[page_key]
                    
                    print(f"  - {page_name}...", end=' ')
                    try:
                        page_generators[page_key](member_name)
                        print("✓")
                    except Exception as e:
                        print(f"✗ (오류: {e})")
        
        print(f"\n{'=' * 80}")
        print(f"전체 멤버 슬라이드 생성 완료")
        print(f"출력 디렉토리: {self.slides_dir}")

def main():
    """전체 멤버 슬라이드 생성"""
    print("=" * 80)
    print("Step 4 v2: HTML/CSS 차트 - 전체 멤버 슬라이드 생성")
    print("=" * 80)
    
    generator = SlideGeneratorV2()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        member_name = "정서린"
        print(f"\n테스트 모드: {member_name} 슬라이드만 생성")
        print(f"\n  Page 2: 전적 상세")
        generator.generate_page_2_performance(member_name)
        
        print(f"\n  Page 3: 종족별 성과")
        generator.generate_page_3_race(member_name)
        
        print(f"\n  Page 4: 맵별 성과")
        generator.generate_page_4_map(member_name)
        
        print(f"\n  Page 5: 티어별 성과")
        generator.generate_page_5_tier(member_name)
        
        print(f"\n{'=' * 80}")
        print("테스트 슬라이드 생성 완료")
        print(f"{'=' * 80}")
    else:
        generator.generate_for_all_members()
        
        print(f"\n{'=' * 80}")
        print("다음 단계: Chrome Headless로 PNG 변환")
        print(f"{'=' * 80}")

if __name__ == '__main__':
    main()
