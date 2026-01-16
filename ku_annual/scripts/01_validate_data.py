# -*- coding: utf-8 -*-
"""
데이터 검증 및 기본 통계 추출 모듈
- 데이터 품질 체크
- 멤버/상대 이름 목록 추출 (오타 방지)
- 기본 통계 산출
"""

import pandas as pd
import json
from pathlib import Path
import sys

# config 모듈 임포트
sys.path.append(str(Path(__file__).parent))
from config import *

class DataValidator:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "stats": {}
        }
        
    def load_data(self):
        """데이터 로드 및 필터링 (이벤트 제외)"""
        try:
            print(f"데이터 로드 중: {self.data_path}")
            df_raw = pd.read_excel(self.data_path)
            df_raw[COL_DATE] = pd.to_datetime(df_raw[COL_DATE])
            
            total_count = len(df_raw)
            print(f"[OK] 원본 데이터 로드: {total_count}건")
            
            # 이벤트 전적 제외 필터링
            event_count = len(df_raw[df_raw[COL_TYPE] == GAME_TYPE_EVENT])
            self.df = df_raw[df_raw[COL_TYPE].isin(ANALYSIS_GAME_TYPES)].copy()
            
            if event_count > 0:
                print(f"  → 이벤트 전적 {event_count}건 제외")
                self.validation_result["stats"]["excluded_events"] = event_count
            
            print(f"[OK] 분석 대상 데이터: {len(self.df)}건 (스폰 + 대회)")
            
            return True
        except Exception as e:
            self.validation_result["is_valid"] = False
            self.validation_result["errors"].append(f"데이터 로드 실패: {str(e)}")
            return False
    
    def validate_schema(self):
        """스키마 검증 (필수 컬럼 존재 확인)"""
        print("\n스키마 검증 중...")
        missing_cols = []
        for col in REQUIRED_COLUMNS:
            if col not in self.df.columns:
                missing_cols.append(col)
        
        if missing_cols:
            self.validation_result["is_valid"] = False
            self.validation_result["errors"].append(
                f"필수 컬럼 누락: {', '.join(missing_cols)}"
            )
            return False
        
        print("[OK] 스키마 검증 통과")
        return True
    
    def check_missing_values(self):
        """결측치 체크"""
        print("\n결측치 검사 중...")
        missing_summary = {}
        has_critical_missing = False
        
        for col in REQUIRED_COLUMNS:
            null_count = self.df[col].isnull().sum()
            if null_count > 0:
                missing_summary[col] = int(null_count)
                
                # 결과 필드 결측은 critical error
                if col == COL_RESULT:
                    has_critical_missing = True
                    self.validation_result["errors"].append(
                        f"'{COL_RESULT}' 필드에 결측치 {null_count}건 발견"
                    )
                else:
                    self.validation_result["warnings"].append(
                        f"'{col}' 필드에 결측치 {null_count}건"
                    )
        
        if missing_summary:
            print(f"  [WARNING] 결측치 발견: {missing_summary}")
            if has_critical_missing:
                self.validation_result["is_valid"] = False
        else:
            print("[OK] 결측치 없음")
        
        self.validation_result["stats"]["missing_values"] = missing_summary
        return not has_critical_missing
    
    def validate_result_values(self):
        """결과 값 검증 (승/패 이외의 값 체크)"""
        print("\n결과 값 검증 중...")
        valid_results = [RESULT_WIN, RESULT_LOSE]
        
        # 결측이 아닌 행만 체크
        non_null_results = self.df[self.df[COL_RESULT].notna()][COL_RESULT]
        invalid_results = non_null_results[~non_null_results.isin(valid_results)]
        
        if len(invalid_results) > 0:
            unique_invalid = invalid_results.unique().tolist()
            self.validation_result["warnings"].append(
                f"'{COL_RESULT}' 필드에 예상치 못한 값: {unique_invalid} ({len(invalid_results)}건)"
            )
            print(f"  ⚠ 비정상 결과 값: {unique_invalid}")
        else:
            print("[OK] 결과 값 검증 통과")
        
        return True
    
    def extract_names(self):
        """멤버 및 상대 이름 추출 (오타 방지를 위해 데이터에서 직접 추출)"""
        print("\n이름 목록 추출 중...")
        
        # 멤버 이름 (케이대 소속)
        member_names = sorted(self.df[COL_MEMBER_NAME].unique().tolist())
        
        # 상대 이름 (전체 상대)
        opponent_names = sorted(self.df[COL_OPPONENT].unique().tolist())
        
        self.validation_result["stats"]["members"] = member_names
        self.validation_result["stats"]["opponents"] = opponent_names
        self.validation_result["stats"]["member_count"] = len(member_names)
        self.validation_result["stats"]["opponent_count"] = len(opponent_names)
        
        print(f"[OK] 멤버 {len(member_names)}명 추출")
        print(f"  -> {', '.join(member_names)}")
        print(f"[OK] 상대 {len(opponent_names)}명 추출")
        
        return member_names, opponent_names
    
    def extract_basic_stats(self):
        """기본 통계 추출"""
        print("\n기본 통계 추출 중...")
        
        stats = {}
        
        # 전체 통계
        stats["total_games"] = len(self.df)
        stats["total_wins"] = len(self.df[self.df[COL_RESULT] == RESULT_WIN])
        stats["total_losses"] = len(self.df[self.df[COL_RESULT] == RESULT_LOSE])
        stats["win_rate"] = (stats["total_wins"] / stats["total_games"] * 100) if stats["total_games"] > 0 else 0
        
        # 기간
        stats["date_start"] = self.df[COL_DATE].min().strftime("%Y-%m-%d")
        stats["date_end"] = self.df[COL_DATE].max().strftime("%Y-%m-%d")
        
        # 종족별
        stats["races"] = self.df[COL_MEMBER_RACE].value_counts().to_dict()
        
        # 티어별
        stats["tiers"] = self.df[COL_MEMBER_TIER].value_counts().to_dict()
        
        # 경기 유형별 (분석 대상만)
        stats["game_types"] = self.df[COL_TYPE].value_counts().to_dict()
        
        # 유형별 승률
        for game_type in ANALYSIS_GAME_TYPES:
            type_df = self.df[self.df[COL_TYPE] == game_type]
            if len(type_df) > 0:
                type_wins = len(type_df[type_df[COL_RESULT] == RESULT_WIN])
                type_wr = (type_wins / len(type_df) * 100) if len(type_df) > 0 else 0
                stats[f"{game_type}_win_rate"] = type_wr
                stats[f"{game_type}_games"] = len(type_df)
                stats[f"{game_type}_wins"] = type_wins
        
        # 월별
        self.df["month"] = self.df[COL_DATE].dt.month
        stats["monthly"] = self.df["month"].value_counts().sort_index().to_dict()
        
        self.validation_result["stats"].update(stats)
        
        print(f"[OK] 전체 경기: {stats['total_games']}경기")
        print(f"[OK] 전체 승률: {stats['win_rate']:.2f}% ({stats['total_wins']}승 {stats['total_losses']}패)")
        print(f"[OK] 기간: {stats['date_start']} ~ {stats['date_end']}")
        
        return stats
    
    def run_validation(self):
        """전체 검증 실행"""
        print("=" * 80)
        print("데이터 검증 시작")
        print("=" * 80)
        
        # 1. 데이터 로드
        if not self.load_data():
            return self.validation_result
        
        # 2. 스키마 검증
        if not self.validate_schema():
            return self.validation_result
        
        # 3. 결측치 체크
        self.check_missing_values()
        
        # 4. 결과 값 검증
        self.validate_result_values()
        
        # 5. 이름 추출
        self.extract_names()
        
        # 6. 기본 통계
        self.extract_basic_stats()
        
        print("\n" + "=" * 80)
        if self.validation_result["is_valid"]:
            print("[SUCCESS] 데이터 검증 완료: 이상 없음")
        else:
            print("[FAIL] 데이터 검증 실패")
            for error in self.validation_result["errors"]:
                print(f"  - ERROR: {error}")
        
        if self.validation_result["warnings"]:
            print("\n경고:")
            for warning in self.validation_result["warnings"]:
                print(f"  - WARNING: {warning}")
        
        print("=" * 80)
        
        return self.validation_result
    
    def save_results(self, output_path):
        """검증 결과 저장"""
        ensure_dirs()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n검증 결과 저장: {output_path}")
    
    def get_dataframe(self):
        """검증된 데이터프레임 반환"""
        return self.df


if __name__ == "__main__":
    # 검증 실행
    validator = DataValidator(DATA_FILE)
    result = validator.run_validation()
    
    # 결과 저장
    output_file = get_output_path("validation_result.json")
    validator.save_results(output_file)
    
    # 검증 통과 시 데이터프레임도 저장
    if result["is_valid"]:
        df = validator.get_dataframe()
        csv_file = get_output_path("validated_data.csv")
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"검증된 데이터 저장: {csv_file}")
        
        # 멤버 이름 리스트 별도 저장 (오타 방지용)
        members_file = get_output_path("member_names.json")
        with open(members_file, 'w', encoding='utf-8') as f:
            json.dump({
                "members": result["stats"]["members"],
                "count": result["stats"]["member_count"]
            }, f, ensure_ascii=False, indent=2)
        print(f"멤버 이름 목록 저장: {members_file}")
        
        print("\n[SUCCESS] 모든 검증 및 저장 완료")
        sys.exit(0)
    else:
        print("\n[FAIL] 검증 실패: 데이터를 수정한 후 다시 실행하세요")
        sys.exit(1)

