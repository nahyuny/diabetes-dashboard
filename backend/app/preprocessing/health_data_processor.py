import pandas as pd
import numpy as np

class HealthDataProcessor:
    """학생 건강검사 데이터 전처리 클래스"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        
    def load_data(self):
        """데이터 로드 및 기본 전처리"""
        try:
            # 다양한 인코딩 시도
            encodings = ['cp949', 'euc-kr', 'utf-8', 'cp1252']
            
            for encoding in encodings:
                try:
                    print(f"[DEBUG] {encoding} 인코딩으로 시도")
                    self.df = pd.read_csv(self.file_path, encoding=encoding)
                    print(f"[DEBUG] {encoding} 인코딩으로 성공")
                    break
                except UnicodeDecodeError:
                    print(f"[DEBUG] {encoding} 인코딩으로 실패")
                    continue
                except Exception as e:
                    print(f"[DEBUG] 다른 오류 발생: {str(e)}")
                    continue
            
            # 모든 인코딩 시도 후에도 실패했는지 확인
            if not hasattr(self, 'df'):
                print(f"[DEBUG] 모든 인코딩으로 시도했으나 실패")
                return False
                
            # 데이터프레임이 비어있지 않은지 확인
            if self.df.empty:
                print(f"[DEBUG] 데이터프레임이 비어있음")
                return False
                
            print(f"[DEBUG] 데이터 로드 성공: {len(self.df)} 행, {len(self.df.columns)} 열")
            print(f"[DEBUG] 컬럼: {self.df.columns[:5].tolist()}...")
            return True
        except Exception as e:
            print(f"데이터 로드 오류: {str(e)}")
            return False
    
    def preprocess(self):
        """데이터 전처리 수행"""
        if not hasattr(self, 'df'):
            if not self.load_data():
                return False
        
        # 1. 컬럼명 정리 (인코딩 문제 해결)
        # 실제 구현에서는 매핑 테이블 사용
        column_mapping = {
            'ÇÐ³âµµ': '학년도',
            'ÃÖÁ¾°¡ÁßÄ¡': '최종가중치',
            # ... 나머지 컬럼 매핑
            'Ç÷´ù½ÄÀü_mgdL': '혈당치_mgdL'
        }

        # 컬럼명이 이미 한글로 정리되어 있다면 매핑 건너뛰기
        if '학년도' in self.df.columns:
            pass
        else:
            # 가능한 컬럼만 매핑
            for old_col, new_col in column_mapping.items():
                if old_col in self.df.columns:
                    self.df = self.df.rename(columns={old_col: new_col})
        
        # 2. 결측치 처리
        # 주요 분석 컬럼의 결측치 처리
        if '혈당치_mgdL' in self.df.columns:
            self.df['혈당치_mgdL'].fillna(self.df['혈당치_mgdL'].median(), inplace=True)
        
        # 3. 파생변수 생성
        # BMI 계산
        if '몸무게_kg' in self.df.columns and '키_cm' in self.df.columns:
            self.df['BMI'] = self.df['몸무게_kg'] / ((self.df['키_cm']/100) ** 2)
        
        # 혈당 수준 분류
        if '혈당치_mgdL' in self.df.columns:
            self.df['혈당수준'] = pd.cut(
                self.df['혈당치_mgdL'],
                bins=[0, 100, 125, float('inf')],
                labels=['정상', '전당뇨', '당뇨의심']
            )
        
        return True

    def get_diabetes_risk_factors(self):
        """당뇨 위험 요인 분석을 위한 데이터셋 준비"""
        # 관련 변수 선택
        # 실제 데이터에 따라 컬럼을 조정해야 함
        try:
            risk_factors_cols = [
                '학년', '성별', '키_cm', '몸무게_kg', 'BMI', '비만여부', 
                '허리둘레_cm', '혈당치_mgdL', '혈당수준'
            ]
            
            # 생활습관 변수들 추가 (실제 데이터에 따라 조정)
            lifestyle_cols = [
                '라면', '음료수', '패스트푸드', '우유유제품', '과일',
                '주3회이상운동', '하루30분이상운동',
                'TV시청2시간이상', '게임2시간이상'
            ]
            
            # 실제 존재하는 컬럼만 필터링
            risk_factors_cols = [col for col in risk_factors_cols if col in self.df.columns]
            lifestyle_cols = [col for col in lifestyle_cols if col in self.df.columns]
            
            all_cols = risk_factors_cols + lifestyle_cols
            risk_factors_df = self.df[all_cols].copy()
            
            return risk_factors_df
            
        except Exception as e:
            print(f"위험 요인 추출 오류: {str(e)}")
            # 가능한 한 많은 데이터를 반환
            return self.df