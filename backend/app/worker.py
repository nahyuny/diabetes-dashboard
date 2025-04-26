# 참고: 이 파일은 더 이상 사용되지 않습니다. 현재는 동기식 처리로 변경되었습니다.
# 이전에 사용하던 Celery 비동기 처리 방식의 코드입니다.

# from celery import Celery
from app.preprocessing.health_data_processor import HealthDataProcessor
from app.analysis.diabetes_analyzer import DiabetesAnalyzer
from app.db.crud import update_task_status, save_analysis_results
import os
import json

# celery_app = Celery('diabetes_dashboard')
# celery_app.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
# celery_app.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# @celery_app.task(bind=True)
def process_health_data_task(file_id):
    """학생 건강검사 데이터 처리 및 분석 작업"""
    try:
        # 작업 시작 상태 업데이트
        # Celery task ID가 없으므로 task_id를 직접 전달해야 함
        # update_task_status(self.request.id, 'processing')
        
        # 파일 정보 가져오기
        from app.db.crud import get_file_info
        file_info = get_file_info(file_id)
        file_path = file_info['path']
        
        # 1. 데이터 전처리
        processor = HealthDataProcessor(file_path)
        if not processor.preprocess():
            raise Exception("데이터 전처리 중 오류가 발생했습니다.")
        
        # 2. 당뇨 관련 데이터 추출
        diabetes_data = processor.get_diabetes_risk_factors()
        
        # 3. 분석 수행
        analyzer = DiabetesAnalyzer(diabetes_data)
        
        # 각종 분석 수행
        summary_stats = analyzer.get_summary_stats()
        correlation_analysis = analyzer.correlation_analysis()
        lifestyle_impact = analyzer.lifestyle_impact_analysis()
        
        # 4. 분석 결과 통합
        analysis_results = {
            'summary': summary_stats,
            'correlations': correlation_analysis,
            'lifestyle_impact': lifestyle_impact
        }
        
        # JSON으로 직렬화 가능한지 확인
        try:
            json.dumps(analysis_results)
        except TypeError as e:
            # numpy나 pandas 타입 등 직렬화 불가능한 객체가 있을 경우 변환
            analysis_results = convert_to_serializable(analysis_results)
        
        # 5. 분석 결과 저장
        save_analysis_results(file_id, self.request.id, analysis_results)
        
        # 6. 작업 상태 업데이트
        # update_task_status(self.request.id, 'completed')
        
        return {
            'status': 'success',
            'file_id': file_id,
            'task_id': 'direct_process'  # Celery 없이 직접 처리된 경우
        }
        
    except Exception as e:
        # 오류 발생 시 상태 업데이트
        # update_task_status(self.request.id, 'failed', str(e))
        
        # 예외 다시 발생
        raise

def convert_to_serializable(obj):
    """NumPy/Pandas 객체를 JSON 직렬화 가능한 형태로 변환"""
    import numpy as np
    import pandas as pd
    
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