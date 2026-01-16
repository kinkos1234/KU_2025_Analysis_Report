"""
전체 파이프라인 실행 (14명 전체)

Step 1: 데이터 전처리 (완료)
Step 2: 패턴 발견 및 분석 (14명 전체)
Step 3: 차트 생성 (14명 전체)
Step 4: HTML 슬라이드 생성 (14명 전체)
Step 5: PNG 변환 (14명 전체)
"""

import subprocess
import sys
from pathlib import Path
import json

class PipelineRunner:
    def __init__(self):
        """파이프라인 실행기 초기화"""
        self.base_dir = Path(__file__).parent
        self.scripts_dir = self.base_dir / 'scripts'
        self.python_path = self.base_dir / '.venv' / 'Scripts' / 'python.exe'
        
        # 멤버 목록 로드
        stats_file = self.base_dir / 'output' / 'data' / 'member_statistics.json'
        with open(stats_file, 'r', encoding='utf-8') as f:
            self.member_stats = json.load(f)
        
        self.all_members = list(self.member_stats.keys())
        
        print("=" * 80)
        print("전체 파이프라인 실행 (14명 멤버)")
        print("=" * 80)
        print()
        print(f"✓ 초기화 완료")
        print(f"  - 총 멤버 수: {len(self.all_members)}")
        print(f"  - 멤버 목록: {', '.join(self.all_members)}")
        print()
    
    def run_script(self, script_name, description):
        """스크립트 실행"""
        print("=" * 80)
        print(f"{description}")
        print("=" * 80)
        print()
        
        script_path = self.scripts_dir / script_name
        
        try:
            result = subprocess.run(
                [str(self.python_path), str(script_path)],
                capture_output=True,
                text=True,
                timeout=600,  # 10분 타임아웃
                encoding='utf-8'
            )
            
            print(result.stdout)
            
            if result.returncode != 0:
                print(f"❌ 오류 발생:")
                print(result.stderr)
                return False
            
            return True
        
        except subprocess.TimeoutExpired:
            print(f"❌ 타임아웃: 10분 초과")
            return False
        except Exception as e:
            print(f"❌ 실행 오류: {e}")
            return False
    
    def run_all(self):
        """전체 파이프라인 실행"""
        steps = [
            ('02_pattern_discovery_all.py', 'Step 2: 패턴 발견 및 분석 (14명 전체)'),
            ('03_generate_charts_all.py', 'Step 3: 차트 생성 (14명 전체)'),
            ('04_generate_slides_all.py', 'Step 4: HTML 슬라이드 생성 (14명 전체)'),
            ('05_convert_to_png_all.py', 'Step 5: PNG 변환 (14명 전체)')
        ]
        
        for script_name, description in steps:
            if not self.run_script(script_name, description):
                print()
                print("=" * 80)
                print(f"❌ 파이프라인 실패: {description}")
                print("=" * 80)
                return False
        
        print()
        print("=" * 80)
        print("✓ 전체 파이프라인 완료!")
        print("=" * 80)
        print()
        print("생성된 결과물:")
        print(f"  - 분석 파일: output/analysis/ ({len(self.all_members)}명)")
        print(f"  - 차트: output/charts/ ({len(self.all_members) * 8}개)")
        print(f"  - HTML 슬라이드: output/slides/ ({len(self.all_members) * 5}개)")
        print(f"  - PNG 이미지: output/images/ ({len(self.all_members) * 5}개)")
        print()
        return True

def main():
    runner = PipelineRunner()
    
    # 전체 파이프라인 실행
    success = runner.run_all()
    
    if success:
        print("✓ 모든 작업 완료!")
    else:
        print("❌ 작업 중 오류 발생")
        sys.exit(1)

if __name__ == '__main__':
    main()
