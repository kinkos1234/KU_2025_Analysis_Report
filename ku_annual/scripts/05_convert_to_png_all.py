"""
Step 5: PNG 변환 (전체 멤버)

Chrome Headless를 사용한 HTML → PNG 변환
- 해상도: 1920x1080px
- 각 슬라이드를 고품질 PNG로 저장
"""

import subprocess
from pathlib import Path
import os
import sys
import json

class PNGConverter:
    def __init__(self):
        """PNG 변환기 초기화"""
        self.base_dir = Path(__file__).parent.parent
        self.slides_dir = self.base_dir / 'output' / 'slides'
        self.images_dir = self.base_dir / 'output' / 'images'
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Chrome 실행 파일 찾기
        self.chrome_path = self._find_chrome()
        
        print("✓ PNG 변환기 초기화 완료")
        print(f"  - Chrome 경로: {self.chrome_path}")
        print(f"  - 전체 멤버 PNG 변환 모드")
    
    def _find_chrome(self):
        """Chrome 실행 파일 경로 찾기"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        print("❌ Chrome을 찾을 수 없습니다.")
        print("다음 경로 중 하나에 Chrome이 설치되어 있어야 합니다:")
        for path in possible_paths:
            print(f"  - {path}")
        sys.exit(1)
    
    def convert_html_to_png(self, html_path, output_path):
        """HTML 파일을 PNG로 변환"""
        # Chrome Headless 명령어
        cmd = [
            self.chrome_path,
            '--headless=new',
            f'--screenshot={output_path}',
            '--window-size=1920,1080',
            '--hide-scrollbars',
            f'file:///{html_path.as_posix()}'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and output_path.exists():
                return True
            else:
                print(f"  ❌ 변환 실패: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            print(f"  ❌ 타임아웃: 30초 초과")
            return False
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            return False
    
    def convert_member_slides(self, member_name):
        """멤버의 모든 슬라이드를 PNG로 변환"""
        print(f"\n{member_name} 슬라이드 PNG 변환 시작...\n")
        
        # 슬라이드 파일 목록
        pages = [
            'page_1_cover',
            'page_2_performance',
            'page_3_race',
            'page_4_map',
            'page_5_tier'
        ]
        
        converted_files = []
        
        for i, page_name in enumerate(pages, 1):
            html_filename = f'{member_name}_{page_name}.html'
            png_filename = f'{member_name}_{page_name}.png'
            
            html_path = self.slides_dir / html_filename
            output_path = self.images_dir / png_filename
            
            if not html_path.exists():
                print(f"[{i}/5] ❌ HTML 파일이 없습니다: {html_filename}")
                continue
            
            print(f"[{i}/5] {member_name} - {page_name} 변환 중...")
            
            if self.convert_html_to_png(html_path, output_path):
                print(f"  ✓ 저장: {output_path.relative_to(self.base_dir)}")
                converted_files.append(output_path)
            else:
                print(f"  ❌ 실패: {page_name}")
        
        return converted_files
    
    def convert_for_all_members(self):
        """모든 멤버의 슬라이드를 PNG로 변환"""
        # member_statistics.json에서 멤버 목록 로드
        stats_file = self.base_dir / 'output' / 'data' / 'member_statistics.json'
        with open(stats_file, 'r', encoding='utf-8') as f:
            member_stats = json.load(f)
        
        all_members = list(member_stats.keys())
        
        print(f"\n총 {len(all_members)}명 멤버 PNG 변환 시작...")
        print(f"멤버 목록: {', '.join(all_members)}\n")
        
        total_files = []
        
        for i, member in enumerate(all_members, 1):
            print(f"\n{'=' * 80}")
            print(f"[{i}/{len(all_members)}] {member} PNG 변환")
            print(f"{'=' * 80}")
            
            files = self.convert_member_slides(member)
            total_files.extend(files)
        
        print(f"\n{'=' * 80}")
        print(f"Step 5 완료: 전체 멤버 PNG 변환 성공 ({len(all_members)}명)")
        print(f"{'=' * 80}")
        print(f"\n변환된 이미지: {len(total_files)}개 ({len(all_members)}명 × 5페이지)")
        
        # 총 파일 크기 계산
        total_size = sum(f.stat().st_size for f in total_files) / (1024 * 1024)  # MB
        print(f"  - 총 크기: {total_size:.1f} MB")
        print(f"  - output/images/ 디렉토리 확인")
        print(f"\n✓ Step 5 PNG 변환 완료. 전체 파이프라인 완료!")

def main():
    print("=" * 80)
    print("Step 5: PNG 변환 (전체 멤버)")
    print("=" * 80)
    print()
    
    converter = PNGConverter()
    converter.convert_for_all_members()

if __name__ == '__main__':
    main()
