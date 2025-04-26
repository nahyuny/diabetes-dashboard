from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

# 인증 설정
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY", "test_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24시간

# 환경 변수에서 사용자 정보 가져오기
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "password")

# 간단한 예시를 위한 임시 사용자 DB
fake_users_db = {
    ADMIN_USERNAME: {
        "id": 1,
        "username": ADMIN_USERNAME,
        "email": f"{ADMIN_USERNAME}@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password" - 실제 구현시 암호화 필요
        "disabled": False,
    }
}

# OAuth2 기반 인증 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 사용자 정보를 위한 모델
class User:
    def __init__(self, id: int, username: str, email: str, disabled: bool = False):
        self.id = id
        self.username = username
        self.email = email
        self.disabled = disabled

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 토큰 생성"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """현재 인증된 사용자 정보 가져오기"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증 정보",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 개발 모드에서는 인증 검사 건너뛰기 (배포 시 제거 필요)
        if os.environ.get("DEBUG") == "1":
            # 개발 모드에서는 관리자로 가정
            return User(
                id=1, 
                username="admin", 
                email="admin@example.com"
            )
            
        # 실제 인증 로직
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    # 사용자 정보 가져오기
    if username in fake_users_db:
        user_data = fake_users_db[username]
        return User(
            id=user_data["id"], 
            username=user_data["username"], 
            email=user_data["email"],
            disabled=user_data["disabled"]
        )
    else:
        raise credentials_exception

async def get_active_user(current_user: User = Depends(get_current_user)):
    """활성화된 사용자인지 확인"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="비활성화된 사용자")
    return current_user