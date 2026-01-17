#!/usr/bin/env python3
"""
K UNIVERSITY 2025 연간 보고서 PDF 병합
- 모든 PNG 이미지를 순서대로 하나의 PDF로 병합
"""

import img2pdf
from pathlib import Path
from PIL import Image
import io

OUTPUT_DIR = Path(__file__).parent / "output"
PDF_OUTPUT = Path(__file__).parent / "K_UNIVERSITY_2025_Annual_Report.pdf"


def get_sorted_images():
    """이미지 파일을 보고서 순서대로 정렬"""
    images = list(OUTPUT_DIR.glob("*.png"))
    
    # 정렬 키 함수
    def sort_key(path):
        name = path.stem
        
        # 섹션별 우선순위
        section_order = {
            '00': 0,   # 표지
            '01': 1,   # 요약
            '02': 2,   # 전체 전적
            '03': 3,   # 멤버별 분석
            '04': 4,   # 대회 분석
            '05': 5,   # 맵 분석
            '06': 6,   # 상대 분석
            '07': 7,   # POTY
            '08': 8,   # 타임라인
            '09': 9,   # 엔딩
        }
        
        # 파일명에서 섹션 번호 추출
        parts = name.split('_')[0].split('-')
        section = parts[0]
        
        # 섹션 내 순서
        if len(parts) == 1:
            sub_order = 0
            sub_sub_order = 0
        elif len(parts) == 2:
            sub_order = int(parts[1]) if parts[1].isdigit() else ord(parts[1])
            sub_sub_order = 0
        else:
            sub_order = int(parts[1]) if parts[1].isdigit() else 0
            sub_sub_order = int(parts[2]) if parts[2].isdigit() else 0
        
        return (section_order.get(section, 99), sub_order, sub_sub_order, name)
    
    return sorted(images, key=sort_key)


def convert_to_rgb(image_path):
    """PNG를 RGB로 변환 (PDF 호환성을 위해)"""
    with Image.open(image_path) as img:
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            # 투명 배경을 흰색으로 대체
            background = Image.new('RGB', img.size, (26, 26, 26))  # 다크 배경
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 바이트로 변환
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95)
        output.seek(0)
        return output.read()


def main():
    print("PDF 병합 시작...")
    
    # 정렬된 이미지 목록
    images = get_sorted_images()
    print(f"총 {len(images)}개 이미지 발견")
    
    # 순서 출력
    print("\n=== 페이지 순서 ===")
    for i, img in enumerate(images, 1):
        print(f"{i:3d}. {img.name}")
    
    # RGB 변환
    print("\n이미지 변환 중...")
    image_data = []
    for img_path in images:
        data = convert_to_rgb(img_path)
        image_data.append(data)
    
    # PDF 생성
    print("\nPDF 생성 중...")
    pdf_bytes = img2pdf.convert(image_data)
    
    with open(PDF_OUTPUT, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"\n✅ PDF 생성 완료: {PDF_OUTPUT}")
    print(f"   파일 크기: {PDF_OUTPUT.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
