import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import warnings
# 경고 무시
warnings.filterwarnings('ignore')

class DiabetesAnalyzer:
    """당뇨 관련 데이터 분석 클래스"""
    
    def __init__(self, df):
        self.df = df
        
    def get_summary_stats(self):
        """기본 통계량 계산"""
        summary = {
            'total_students': len(self.df),
        }
        
        # 혈당수준 분포 추가
        if '혈당수준' in self.df.columns:
            summary['diabetes_risk'] = {
                'normal': (self.df['혈당수준'] == '정상').sum(),
                'prediabetes': (self.df['혈당수준'] == '전당뇨').sum(),
                'diabetes': (self.df['혈당수준'] == '당뇨의심').sum()
            }
        
        # 혈당치 통계량 추가
        if '혈당치_mgdL' in self.df.columns:
            summary['blood_glucose'] = {
                'mean': self.df['혈당치_mgdL'].mean(),
                'median': self.df['혈당치_mgdL'].median(),
                'std': self.df['혈당치_mgdL'].std(),
                'min': self.df['혈당치_mgdL'].min(),
                'max': self.df['혈당치_mgdL'].max()
            }
        
        # BMI 분포 추가
        if 'BMI' in self.df.columns:
            summary['bmi'] = {
                'mean': self.df['BMI'].mean(),
                'underweight': (self.df['BMI'] < 18.5).sum(),
                'normal': ((self.df['BMI'] >= 18.5) & (self.df['BMI'] < 23)).sum(),
                'overweight': ((self.df['BMI'] >= 23) & (self.df['BMI'] < 25)).sum(),
                'obese': (self.df['BMI'] >= 25).sum()
            }
            
        return summary
    
    def correlation_analysis(self):
        """상관관계 분석"""
        # 주요 변수 상관관계 계산
        # 실제 존재하는 컬럼만 사용
        potential_cols = [
            '혈당치_mgdL', 'BMI', '허리둘레_cm', 
            '라면', '음료수', '패스트푸드',
            '주3회이상운동', '하루30분이상운동',
            'TV시청2시간이상', '게임2시간이상'
        ]
        
        numeric_cols = [col for col in potential_cols if col in self.df.columns]
        
        # 충분한 수치형 변수가 있을 경우에만 상관관계 분석
        if len(numeric_cols) > 1 and '혈당치_mgdL' in numeric_cols:
            # NaN 값 제거
            corr_df = self.df[numeric_cols].dropna()
            corr_matrix = corr_df.corr().round(3)
            
            # 혈당치와의 상관관계만 추출
            glucose_corr = corr_matrix['혈당치_mgdL'].sort_values(ascending=False)
            
            return {
                'correlation_matrix': corr_matrix.to_dict(),
                'glucose_correlation': glucose_corr.to_dict()
            }
        else:
            # 충분한 변수가 없는 경우 빈 결과 반환
            return {
                'correlation_matrix': {},
                'glucose_correlation': {}
            }
    
    def lifestyle_impact_analysis(self):
        """생활습관이 혈당치에 미치는 영향 분석"""
        # 분석에 필요한 모든 변수가 있는지 확인
        if '혈당치_mgdL' not in self.df.columns:
            return {
                'model_summary': {
                    'r_squared': 0,
                    'adj_r_squared': 0,
                    'f_pvalue': 1
                },
                'coefficients': {'error': '혈당치 변수가 없습니다'}
            }
        
        # 회귀 분석 가능한 변수 선택
        potential_vars = [
            'BMI', '라면', '음료수', '패스트푸드',
            '주3회이상운동', '하루30분이상운동',
            'TV시청2시간이상', '게임2시간이상'
        ]
        
        # 실제 데이터에 존재하는 변수만 사용
        X_vars = [var for var in potential_vars if var in self.df.columns]
        
        # 충분한 변수가 없는 경우
        if len(X_vars) < 1:
            return {
                'model_summary': {
                    'r_squared': 0,
                    'adj_r_squared': 0,
                    'f_pvalue': 1
                },
                'coefficients': {'error': '회귀분석에 필요한 독립변수가 없습니다'}
            }
        
        try:
            # 결측치가 있는 행 제거
            analysis_df = self.df[X_vars + ['혈당치_mgdL']].dropna()
            
            if len(analysis_df) < 10:  # 샘플 수가 너무 적은 경우
                return {
                    'model_summary': {
                        'r_squared': 0,
                        'adj_r_squared': 0,
                        'f_pvalue': 1
                    },
                    'coefficients': {'error': '분석에 필요한 데이터가 충분하지 않습니다'}
                }
            
            # 회귀 모델 적합
            X = sm.add_constant(analysis_df[X_vars])
            y = analysis_df['혈당치_mgdL']
            
            model = sm.OLS(y, X).fit()
            
            # 결과 정리
            results = {
                'model_summary': {
                    'r_squared': model.rsquared,
                    'adj_r_squared': model.rsquared_adj,
                    'f_pvalue': model.f_pvalue
                },
                'coefficients': {}
            }
            
            # 계수 정보 정리
            for variable, coef, pval in zip(X.columns, model.params, model.pvalues):
                results['coefficients'][variable] = {
                    'coefficient': coef,
                    'p_value': pval,
                    'significant': pval < 0.05
                }
            
            return results
            
        except Exception as e:
            # 오류 발생 시 기본 결과 반환
            print(f"회귀분석 오류: {str(e)}")
            return {
                'model_summary': {
                    'r_squared': 0,
                    'adj_r_squared': 0,
                    'f_pvalue': 1
                },
                'coefficients': {'error': f'분석 중 오류 발생: {str(e)}'}
            }