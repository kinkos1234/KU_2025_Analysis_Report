# -*- coding: utf-8 -*-
"""
KU Annual 2025 보고서 자동 생성 마스터 스크립트
- 원클릭 실행으로 전체 파이프라인 수행
- 2026-01-01 최종 데이터 투입 후 실행
"""

import sys
import subprocess
from pathlib import Path
import time

def print_header(message):
    """헤더 출력"""
    print("\n" + "=" * 80)
    print(message)
    print("=" * 80 + "\n")

def run_script(script_path, description):
    """스크립트 실행"""
    print(f"[STEP] {description}")
    print(f"실행: {script_path}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"[OK] {description} 완료 (소요시간: {elapsed:.1f}초)")
            if result.stdout:
                # 주요 정보만 출력
                for line in result.stdout.split('\n'):
                    if '[OK]' in line or '[SUCCESS]' in line or '경기' in line:
                        print(f"  {line.strip()}")
            return True
        else:
            print(f"[FAIL] {description} 실패")
            print(f"에러:\n{result.stderr}")
            return False
    
    except Exception as e:
        print(f"[ERROR] 실행 중 오류 발생: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    print_header("K UNIVERSITY 2025 연간 보고서 자동 생성 시작")
    
    total_start = time.time()
    
    # 스크립트 목록 (실행 순서)
    scripts = [
        ("scripts/01_validate_data.py", "1. 데이터 검증 및 기본 통계"),
        ("scripts/02_analyze_team.py", "2. 팀 분석"),
        ("scripts/03_analyze_members.py", "3. 멤버별 분석"),
        ("scripts/05_analyze_mvp.py", "4. MVP 선정 분석"),
        ("scripts/04_generate_charts.py", "5. 차트 생성"),
        ("scripts/06_generate_report.py", "6. 보고서 생성 (Markdown)"),
    ]
    
    failed = []
    
    for script_path, description in scripts:
        if not run_script(script_path, description):
            failed.append(description)
            print(f"\n[WARNING] {description} 실패했으나 계속 진행합니다...")
        print("")  # 구분선
    
    total_elapsed = time.time() - total_start
    
    print_header("보고서 생성 완료")
    
    if failed:
        print("[WARNING] 다음 단계에서 실패가 발생했습니다:")
        for f in failed:
            print(f"  - {f}")
        print("\n일부 실패가 있었으나 생성 가능한 결과물은 output 폴더에 저장되었습니다.")
    else:
        print("[SUCCESS] 모든 분석 단계가 성공적으로 완료되었습니다!")
    
    print(f"\n총 소요시간: {total_elapsed:.1f}초 ({total_elapsed/60:.1f}분)")
    
    print("\n[출력 파일 위치]")
    print("  - 분석 데이터: output/data/")
    print("  - 차트 이미지: output/charts/")
    print("  - 보고서: output/reports/")
    print("  - 개인 Booklet: output/reports/booklets/")
    
    print("\n" + "=" * 80)
    print("최종 보고서를 확인하세요:")
    print("  - output/reports/01_팀분석_보고서.md")
    print("  - output/reports/02_MVP_선정.md")
    print("  - output/reports/booklets/ (개인별 Booklet)")
    print("=" * 80)
    
    return len(failed) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

