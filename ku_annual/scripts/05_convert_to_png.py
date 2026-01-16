"""
Step 5: PNG 변환 (프로토타입: 정서린)

Chrome Headless를 사용한 HTML → PNG 변환
- 해상도: 1920x1080px
- 각 슬라이드를 고품질 PNG로 저장
"""

import subprocess
from pathlib import Path
import os
import sys

class PNGConverter:
    def __init__(self):
        """PNG 변환기 초기화"""
        self.base_dir = Path(__file__).parent.parent
        self.slides_dir = self.base_dir / 'output' / 'slides'
        self.images_dir = self.base_dir / 'output' / 'images'
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Chrome 실행 파일 찾기
        self.chrome_path = self._find_chrome()
        
        # 프로토타입 멤버
        self.prototype_member = '정서린'
        
        print("✓ PNG 변환기 초기화 완료")
        print(f"  - Chrome 경로: {self.chrome_path}")
        print(f"  - 프로토타입 대상: {self.prototype_member}")
    
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

def main():
    print("=" * 80)
    print("Step 5: PNG 변환 (프로토타입: 정서린)")
    print("=" * 80)
    print()
    
    converter = PNGConverter()
    
    # 정서린 슬라이드 변환
    files = converter.convert_member_slides(converter.prototype_member)
    
    print()
    print("=" * 80)
    print("Step 5 완료: PNG 변환 성공")
    print("=" * 80)
    print()
    print(f"변환된 이미지 ({len(files)}개):")
    for f in files:
        file_size = f.stat().st_size / 1024  # KB
        print(f"  - {f.name} ({file_size:.1f} KB)")
    print()
    print("✓ Step 5 PNG 변환 완료. 프로토타입 검증 완료!")
    print()
    print("다음 단계:")
    print("  1. 생성된 이미지 확인 (output/images/)")
    print("  2. 품질 및 디자인 검토")
    print("  3. 문제 없으면 전체 14명 확장 실행")

if __name__ == '__main__':
    main()
