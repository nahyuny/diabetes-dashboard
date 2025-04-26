import React, { useState, useEffect } from 'react';
import { Layout, message, Form, Input, Button, Card } from 'antd';
import FileUpload from './components/FileUpload';
import Dashboard from './pages/Dashboard';
import { checkServerHealth, login } from './services/api';
import 'antd/dist/antd.css';
import './App.css';

const { Content, Footer } = Layout;

function App() {
  const [uploadedData, setUploadedData] = useState(null);
  const [serverStatus, setServerStatus] = useState('checking');
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  
  useEffect(() => {
    // 백엔드 서버 상태 확인
    const checkServer = async () => {
      try {
        await checkServerHealth();
        setServerStatus('online');
      } catch (error) {
        setServerStatus('offline');
        message.error('백엔드 서버에 연결할 수 없습니다. 관리자에게 문의하세요.');
      }
    };
    
    checkServer();
  }, []);
  
  const handleUploadComplete = (data) => {
    setUploadedData(data);
    message.success('파일이 성공적으로 업로드되었습니다. 데이터 분석 중...');
  };
  
  const handleLogin = async (values) => {
    setIsLoggingIn(true);
    try {
      await login(values.username, values.password);
      setIsLoggedIn(true);
      message.success('로그인 성공');
    } catch (error) {
      message.error('로그인 실패: ' + (error.response?.data?.detail || '아이디 또는 비밀번호가 잘못되었습니다.'));
    } finally {
      setIsLoggingIn(false);
    }
  };
  
  return (
    <Layout className="layout" style={{ minHeight: '100vh' }}>
      <Content style={{ padding: '50px' }}>
        {!isLoggedIn ? (
          <div style={{ maxWidth: '400px', margin: '0 auto' }}>
            <h1 style={{ textAlign: 'center', marginBottom: '40px' }}>
              학생 건강검사 데이터 분석 서비스
            </h1>
            <Card title="로그인">
              <Form
                name="login"
                onFinish={handleLogin}
                layout="vertical"
              >
                <Form.Item
                  label="아이디"
                  name="username"
                  rules={[{ required: true, message: '아이디를 입력해주세요' }]}
                >
                  <Input placeholder="admin" />
                </Form.Item>
                <Form.Item
                  label="비밀번호"
                  name="password"
                  rules={[{ required: true, message: '비밀번호를 입력해주세요' }]}
                >
                  <Input.Password placeholder="password" />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={isLoggingIn} block>
                    로그인
                  </Button>
                </Form.Item>
                <div style={{ textAlign: 'center', fontSize: '12px', color: '#888' }}>
                  테스트 계정: admin / password
                </div>
              </Form>
            </Card>
          </div>
        ) : !uploadedData ? (
          <div style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h1 style={{ textAlign: 'center', marginBottom: '40px' }}>
              학생 건강검사 데이터 분석 서비스
            </h1>
            <FileUpload onUploadComplete={handleUploadComplete} />
          </div>
        ) : (
          <Dashboard fileId={uploadedData.file_id} taskId={uploadedData.task_id} />
        )}
      </Content>
      
      <Footer style={{ textAlign: 'center' }}>
        학생 건강검사 데이터 분석 대시보드 ©{new Date().getFullYear()} 제작
      </Footer>
    </Layout>
  );
}

export default App;