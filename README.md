# 학생 건강검사 데이터 분석 대시보드

학교나 교육기관에서 학생 건강검사 CSV 파일을 업로드하면 자동으로 데이터를 분석하고, 특히 2형 당뇨와 관련된 요인을 시각화하여 대시보드 형태로 제공하는 웹 애플리케이션입니다.

## 프로젝트 개요

이 프로젝트는 학생들의 건강검사 데이터를 활용하여 당뇨병 위험 요인을 조기에 식별하고 예방 대책을 마련하는 데 도움을 주기 위해 개발되었습니다. 특히 어린 나이에 발생하는 2형 당뇨는 적절한 생활습관 개선으로 예방이 가능하므로, 위험군을 조기에 파악하는 것이 중요합니다.

데이터를 기반으로 학생들의 건강 상태를 시각적으로 파악할 수 있으며, 특히 당뇨 위험 요인과 생활습관 간의 관계를 분석하여 맞춤형 예방 지침을 제공할 수 있습니다.

© 2025 김나현 제작

## 주요 기능

- 학생 건강검사 CSV 파일 업로드 및 분석
- 혈당 수준 분포 시각화 (정상, 전당뇨, 당뇨의심)
- BMI 분포 시각화
- 혈당치와 주요 요인들 간의 상관관계 분석 ([분석 방법론](./CORRELATION_ANALYSIS.md))
- 생활습관이 혈당치에 미치는 영향 분석
- 개인별 당뇨 위험도 예측 모델

## 기술 스택

### 백엔드
- FastAPI: 고성능 API 서버
- Pandas/NumPy: 데이터 분석
- SciPy/StatsModels: 통계 분석
- JWT: 사용자 인증
- 참고: 현재 버전에서는 동기 처리 방식 사용

### 프론트엔드
- React: UI 구성
- Ant Design: UI 컴포넌트
- Chart.js: 데이터 시각화
- Axios: API 통신

### 인프라
- Docker/Docker Compose: 컨테이너화 및 배포(선택)
- Nginx: 웹 서버 및 리버스 프록시(선택)
- 또는 Netlify/Vercel(프론트엔드) + Heroku/Render(백엔드) 조합으로 배포 가능

## 시작하기

### 전제 조건
- Python 3.9+ 설치
- Node.js 16+ 설치
- Git 설치

### 설치 및 실행

#### 방법 1: 간단한 데모 버전 실행
```bash
# 간단한 데모 버전 실행 (Flask 기반)
cd diabetes-dashboard
python simple_demo.py

# 브라우저에서 접속
# http://127.0.0.1:8080
```

#### 방법 2: 전체 애플리케이션 실행

1. 저장소 클론
   ```bash
   git clone <repository-url>
   cd diabetes-dashboard
   ```

2. 백엔드 설정 및 실행
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # 개발 모드로 실행
   DEBUG=1 python -m app.main
   ```

3. 프론트엔드 설정 및 실행
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. 브라우저에서 접속
   ```
   http://localhost:3000
   ```

## 데이터 형식

### 입력 CSV 파일 요구사항

학생 건강검사 CSV 파일은 다음과 같은 컬럼을 포함해야 합니다:
- 학년, 성별, 키_cm, 몸무게_kg, 허리둘레_cm, 혈당치_mgdL
- 생활습관 관련 컬럼 (선택): 라면, 음료수, 패스트푸드, 우유유제품, 과일, 주3회이상운동, 하루30분이상운동, TV시청2시간이상, 게임2시간이상

## 개발자 정보

### 프로덕션 배포 준비

1. 백엔드 배포 준비
   ```bash
   cd backend
   
   # 디버그 모드 비활성화
   # app/main.py에서 DEBUG 환경변수 확인 로직 수정
   
   # Procfile 생성 (Heroku 배포시)
   echo "web: gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker" > Procfile
   ```

2. 프론트엔드 배포 준비
   ```bash
   cd frontend
   
   # 프로덕션 빌드 생성
   npm run build
   
   # 백엔드 API URL 설정 (.env 파일)
   echo "REACT_APP_API_URL=https://your-backend-url.com/api" > .env.production
   ```

3. CORS 설정 확인
   백엔드의 `app/main.py`에서 origins 목록에 프론트엔드 도메인이 포함되어 있는지 확인하세요.

### 로컬 개발 환경 설정

1. 백엔드 개발 환경
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. 프론트엔드 개발 환경
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 기여 방법

1. 이슈 생성 또는 기존 이슈 선택
2. 기능 브랜치 생성 (`git checkout -b feature/new-feature`)
3. 변경사항 커밋 (`git commit -m 'Add new feature'`)
4. 브랜치 푸시 (`git push origin feature/new-feature`)
5. Pull Request 생성

## 라이센스

이 프로젝트는 MIT 라이센스에 따라 사용이 허가됩니다 - 자세한 내용은 LICENSE 파일을 참조하세요.

## 문제 해결

### 알려진 문제

1. CSV 파일 인코딩 문제
   - 해결: 시스템이 여러 인코딩(CP949, EUC-KR, UTF-8, CP1252)을 순차적으로 시도합니다.

2. JSON 직렬화 오류
   - 해결: NumPy/Pandas 데이터 타입을 표준 Python 타입으로 변환하는 유틸리티 함수가 구현되어 있습니다.
   
3. 데이터 분석 실패
   - 원인: 입력 데이터 형식이 예상과 다를 수 있습니다.
   - 해결: 요구되는 데이터 형식을 준수하는지 확인하세요. 데이터 전처리 로직은 `/backend/app/preprocessing/health_data_processor.py`에서 확인할 수 있습니다.

## 감사의 글

이 프로젝트를 사용해 주신 모든 분들께 감사드립니다.

© 2025 김나현 제작