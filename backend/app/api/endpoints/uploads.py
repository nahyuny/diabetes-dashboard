from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.file_service import validate_file, save_file
from app.services.auth_service import get_current_user
import numpy as np
import pandas as pd
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# NumPy 및 Pandas 타입을 JSON 직렬화 가능한 표준 Python 타입으로 변환하는 함수
def convert_to_serializable(obj):
    """NumPy/Pandas 타입을 표준 Python 타입으로 변환"""
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return [convert_to_serializable(i) for i in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

router = APIRouter()

@router.post("/upload")
async def upload_health_data(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """학생 건강검사 CSV 파일 업로드 엔드포인트"""
    # 파일 검증
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "CSV 파일만 업로드 가능합니다.")
    
    # 파일 저장 및 처리 작업 생성
    try:
        file_id = await save_file(file, current_user.id)
        
        # 동기식으로 직접 처리 (개발 모드용)
        # 필요한 함수들 가져오기
        from app.preprocessing.health_data_processor import HealthDataProcessor
        from app.analysis.diabetes_analyzer import DiabetesAnalyzer
        from app.db.crud import update_task_status, save_analysis_results, get_file_info
        import uuid
        
        # 임시 task_id 생성
        task_id = str(uuid.uuid4())
        
        # 파일 정보 가져오기
        file_info = get_file_info(file_id)
        file_path = file_info['path']
        
        # 1. 데이터 전처리
        processor = HealthDataProcessor(file_path)
        preprocess_result = processor.preprocess()
        print(f"[DEBUG] 전처리 결과: {preprocess_result}")
        
        # 2. 당뇨 관련 데이터 추출
        try:
            diabetes_data = processor.get_diabetes_risk_factors()
            # 성공적으로 데이터 추출 완료
        except Exception as e:
            print(f"[DEBUG] 데이터 추출 오류: {str(e)}")
            raise
        
        # 3. 간단한 분석 수행
        try:
            analyzer = DiabetesAnalyzer(diabetes_data)
            # 분석기 초기화
            
            # 기본 통계량 계산
            try:
                summary_stats = analyzer.get_summary_stats()
                # 모든 분석 완료
            except Exception as e:
                print(f"[DEBUG] 통계량 계산 오류: {str(e)}")
                summary_stats = {'message': '통계량 계산 중 오류 발생'}
            
            # 상관관계 분석
            try:
                correlation_analysis = analyzer.correlation_analysis()
                # 상관관계 분석 완료
            except Exception as e:
                print(f"[DEBUG] 상관관계 분석 오류: {str(e)}")
                correlation_analysis = {'message': '상관관계 분석 중 오류 발생'}
            
            # 생활습관 영향 분석
            try:
                lifestyle_impact = analyzer.lifestyle_impact_analysis()
                print(f"[DEBUG] 생활습관 영향 분석 성공")
            except Exception as e:
                print(f"[DEBUG] 생활습관 영향 분석 오류: {str(e)}")
                lifestyle_impact = {'message': '생활습관 영향 분석 중 오류 발생'}
            
            # 분석 결과 생성
            analysis_results = {
                'summary': summary_stats,
                'correlations': correlation_analysis,
                'lifestyle_impact': lifestyle_impact
            }
            
            # NumPy/Pandas 타입을 표준 Python 타입으로 변환
            try:
                analysis_results = convert_to_serializable(analysis_results)
                # 직렬화 가능한지 테스트
                json.dumps(analysis_results) # JSON 직렬화 테스트
            except Exception as e:
                # JSON 직렬화 오류 처리
                logging.error(f"분석 결과 JSON 직렬화 오류: {str(e)}")
                # 오류 발생 시 기본 결과로 대체
                analysis_results = {
                    'summary': {'message': 'JSON 직렬화 중 오류 발생'},
                    'correlations': {'message': 'JSON 직렬화 중 오류 발생'},
                    'lifestyle_impact': {'message': 'JSON 직렬화 중 오류 발생'}
                }
            
            # 분석 결과 생성 완료
            
        except Exception as e:
            print(f"[DEBUG] 분석 중 오류 발생: {str(e)}")
            # 오류 발생 시 기본 결과 반환
            analysis_results = {
                'summary': {'message': '분석 중 오류가 발생했습니다.'},
                'correlations': {'message': '상관관계 분석 중 오류가 발생했습니다.'},
                'lifestyle_impact': {'message': '생활 습관 영향 분석 중 오류가 발생했습니다.'}
            }
        
        # 분석 결과 저장
        save_analysis_results(file_id, task_id, analysis_results)
        
        return {"file_id": file_id, "task_id": task_id}
    except Exception as e:
        raise HTTPException(500, f"파일 처리 중 오류가 발생했습니다: {str(e)}")