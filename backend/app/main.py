from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 업로드 디렉토리 자동 생성
try:
    # 몽키 패칭을 사용하여 경로 가져오기
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uploads_dir = os.path.join(base_dir, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    logger.info(f"uploads 디렉토리 확인/생성: {uploads_dir}")
    
    # 결과 저장용 디렉토리 생성
    results_dir = os.path.join(uploads_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    logger.info(f"results 디렉토리 확인/생성: {results_dir}")
except Exception as e:
    logger.error(f"디렉토리 생성 오류: {str(e)}")

from app.services.auth_service import (
    create_access_token, 
    get_current_user,
    fake_users_db,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
# 엔드포인트 라우터 임포트
from app.api.endpoints import uploads, analysis

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="학생 건강검사 데이터 분석 API",
    description="학교나 교육기관에서 학생 건강검사 CSV 파일을 업로드하고 분석하는 서비스",
    version="1.0.0"
)

# CORS 미들웨어 설정
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

# 프로덕션 환경에서는 실제 도메인 추가
if os.environ.get("PRODUCTION_DOMAIN"):
    origins.append(os.environ.get("PRODUCTION_DOMAIN"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(uploads.router, prefix="/api", tags=["파일 업로드"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["분석"])

# 인증 관련 엔드포인트
@app.post("/api/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """토큰 발급 엔드포인트"""
    user = None
    
    # 사용자 확인 (실제 구현에서는 암호 검증 필요)
    if form_data.username in fake_users_db:
        user = fake_users_db[form_data.username]
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자 이름 또는 비밀번호",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# 분석 결과 조회는 analysis 라우터에서 처리

# 서버 상태 확인 엔드포인트
@app.get("/api/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy"}

# 간단한 루트 경로
@app.get("/")
async def root():
    return {"message": "학생 건강검사 데이터 분석 API에 오신 것을 환영합니다! /docs로 이동하여 API 문서를 확인하세요."}

# FastAPI 문서 경로 설정
app.docs_url = "/docs"
app.redoc_url = "/redoc"

# 애플리케이션 기본 메타데이터 설정
app.openapi_tags = [
    {
        "name": "파일 업로드",
        "description": "CSV 파일 업로드 관련 API",
    },
    {
        "name": "인증",
        "description": "사용자 인증 관련 API",
    },
    {
        "name": "분석",
        "description": "데이터 분석 결과 관련 API",
    }
]

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    
    # 개발 환경에서 실행
    uvicorn.run("app.main:app", host=host, port=port, reload=True)