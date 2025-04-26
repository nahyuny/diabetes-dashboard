#!/bin/bash

# 백엔드 실행
echo "Starting backend server..."
cd backend

# Python 가상환경 생성 및 활성화
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# 의존성 설치
echo "Installing dependencies..."
pip install -r requirements.txt

# 백엔드 서버 실행 (백그라운드)
echo "Running FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 프론트엔드 실행
echo "Starting frontend server..."
cd ../frontend

# Node 의존성 설치
echo "Installing node dependencies..."
npm install

# React 개발 서버 실행
echo "Running React development server..."
npm start &
FRONTEND_PID=$!

# 종료 핸들러
function cleanup {
    echo "Shutting down servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

# Ctrl+C 시그널 핸들링
trap cleanup SIGINT

echo "Both servers are running. Press Ctrl+C to stop."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"

# 무한 대기
while true; do
    sleep 1
done