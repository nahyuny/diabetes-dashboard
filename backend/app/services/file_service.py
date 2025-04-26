import os
import uuid
from fastapi import UploadFile
import shutil
from datetime import datetime
from app.db.crud import create_file_record

# 업로드 디렉토리 설정
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "../../uploads"))

# 디렉토리가 없으면 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def validate_file(file: UploadFile) -> bool:
    """CSV 파일인지 확인하고 기본 검증 수행"""
    
    # 파일 확장자 검증
    if not file.filename.endswith('.csv'):
        return False
    
    # 파일 크기 검증 (예: 10MB 이하)
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB
    
    chunk = await file.read(chunk_size)
    while chunk:
        file_size += len(chunk)
        if file_size > 10 * 1024 * 1024:  # 10MB
            return False
        chunk = await file.read(chunk_size)
    
    # 파일 포인터 처음으로 되돌리기
    await file.seek(0)
    
    return True

async def save_file(file: UploadFile, user_id: int) -> str:
    """파일을 저장하고 파일 ID 반환"""
    
    # 고유 파일명 생성
    file_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = file.filename
    file_extension = original_filename.split('.')[-1]
    
    # 저장할 파일 경로
    save_filename = f"{file_id}_{timestamp}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, save_filename)
    
    # 파일 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # DB에 파일 정보 저장
    file_record = {
        "id": file_id,
        "filename": original_filename,
        "path": file_path,
        "user_id": user_id,
        "created_at": datetime.now(),
        "file_size": os.path.getsize(file_path)
    }
    
    create_file_record(file_record)
    
    return file_id