import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button, Progress, Alert, Card } from 'antd';
import { UploadOutlined, CheckCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import { uploadHealthData } from '../services/api';

const FileUpload = ({ onUploadComplete }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  
  const { getRootProps, getInputProps } = useDropzone({
    accept: '.csv,text/csv',
    multiple: false,
    onDrop: (acceptedFiles) => {
      setFile(acceptedFiles[0]);
      setError(null);
    }
  });
  
  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    setUploadProgress(0);
    
    try {
      // Progress 시뮬레이션 (실제로는 axios의 progress 이벤트 사용)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return 95;
          }
          return prev + 5;
        });
      }, 500);
      
      // API 호출로 파일 업로드
      const response = await uploadHealthData(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // 업로드 완료 후 콜백 호출
      onUploadComplete(response.data);
      
    } catch (err) {
      setError(err.response?.data?.detail || '파일 업로드 중 오류가 발생했습니다.');
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <Card title="학생 건강검사 데이터 업로드">
      <div {...getRootProps()} style={{
        border: '2px dashed #d9d9d9',
        borderRadius: '4px',
        padding: '20px',
        textAlign: 'center',
        cursor: 'pointer',
        marginBottom: '20px'
      }}>
        <input {...getInputProps()} />
        <p>CSV 파일을 여기에 끌어다 놓거나 클릭하여 업로드하세요</p>
        <UploadOutlined style={{ fontSize: '32px', color: '#1890ff' }} />
      </div>
      
      {file && (
        <div style={{ marginBottom: '20px' }}>
          <p>
            <CheckCircleOutlined style={{ color: '#52c41a' }} /> {file.name}
          </p>
        </div>
      )}
      
      {uploading && (
        <Progress percent={uploadProgress} status="active" />
      )}
      
      {error && (
        <Alert
          message="업로드 오류"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: '20px' }}
        />
      )}
      
      <Button
        type="primary"
        icon={uploading ? <LoadingOutlined /> : <UploadOutlined />}
        loading={uploading}
        disabled={!file || uploading}
        onClick={handleUpload}
      >
        업로드
      </Button>
    </Card>
  );
};

export default FileUpload;