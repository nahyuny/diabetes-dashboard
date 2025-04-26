import axios from 'axios';

// API 기본 설정
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터: 인증 토큰 추가
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 응답 인터셉터: 오류 처리
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401 오류 시 로그아웃 처리
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      // 로그인 페이지로 리디렉션 (필요한 경우)
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 로그인 함수
export const login = async (username, password) => {
  try {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await axios.post(`${API_URL}/token`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    // 토큰 저장
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    
    return response;
  } catch (error) {
    throw error;
  }
};

// 로그아웃 함수
export const logout = () => {
  localStorage.removeItem('token');
};

// 학생 건강검사 데이터 업로드
export const uploadHealthData = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response;
  } catch (error) {
    throw error;
  }
};

// 분석 결과 가져오기
export const fetchAnalysisResults = async (taskId) => {
  try {
    const response = await api.get(`/analysis/${taskId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// 서버 상태 확인
export const checkServerHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default api;