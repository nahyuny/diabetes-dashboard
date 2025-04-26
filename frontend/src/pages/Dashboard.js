import React, { useState, useEffect } from 'react';
import { Layout, Spin, Tabs, Card, Statistic, Row, Col, Typography, Alert } from 'antd';
import { UserOutlined, AlertOutlined, BarChartOutlined, HeartOutlined } from '@ant-design/icons';
import { fetchAnalysisResults } from '../services/api';
import DiabetesRiskChart from '../components/charts/DiabetesRiskChart';
import BMIDistributionChart from '../components/charts/BMIDistributionChart';
import CorrelationHeatmap from '../components/charts/CorrelationHeatmap';
import LifestyleFactorsChart from '../components/charts/LifestyleFactorsChart';
import RiskPredictionModel from '../components/RiskPredictionModel';

const { Header, Content, Footer } = Layout;
const { TabPane } = Tabs;
const { Title, Paragraph } = Typography;

const Dashboard = ({ fileId, taskId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  
  useEffect(() => {
    // 분석 결과 가져오기
    const fetchData = async () => {
      try {
        const result = await fetchAnalysisResults(taskId);
        if (result.status === 'completed') {
          setAnalysisData(result.data);
          setLoading(false);
        } else if (result.status === 'processing') {
          // 아직 처리 중이면 5초 후 다시 시도
          setTimeout(fetchData, 5000);
        } else {
          throw new Error('분석 작업이 실패했습니다.');
        }
      } catch (err) {
        setError(err.message || '데이터를 불러오는 중 오류가 발생했습니다.');
        setLoading(false);
      }
    };
    
    fetchData();
  }, [taskId]);
  
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <p style={{ marginTop: 20 }}>분석 결과를 불러오는 중입니다...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <Alert
        message="분석 오류"
        description={error}
        type="error"
        showIcon
        style={{ maxWidth: '600px', margin: '100px auto' }}
      />
    );
  }
  
  const { summary, correlations, lifestyle_impact } = analysisData;
  
  return (
    <Layout>
      <Header style={{ background: '#fff', padding: '0 20px' }}>
        <Title level={3}>학생 건강검사 데이터 분석 대시보드</Title>
      </Header>
      
      <Content style={{ padding: '20px' }}>
        {/* 요약 통계 카드 */}
        <Row gutter={[16, 16]} style={{ marginBottom: '20px' }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="분석 대상 학생 수"
                value={summary.total_students}
                prefix={<UserOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="당뇨 위험군 학생 수"
                value={summary.diabetes_risk ? (summary.diabetes_risk.diabetes + summary.diabetes_risk.prediabetes) : 0}
                prefix={<AlertOutlined />}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="평균 혈당치"
                value={summary.blood_glucose ? summary.blood_glucose.mean.toFixed(1) : 'N/A'}
                suffix="mg/dL"
                prefix={<HeartOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="과체중 이상 비율"
                value={summary.bmi ? 
                  ((summary.bmi.overweight + summary.bmi.obese) / summary.total_students * 100).toFixed(1) : 
                  'N/A'
                }
                suffix="%"
                prefix={<BarChartOutlined />}
              />
            </Card>
          </Col>
        </Row>
        
        {/* 탭 기반 대시보드 */}
        <Tabs defaultActiveKey="overview" type="card">
          <TabPane tab="개요" key="overview">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Card title="혈당 수준 분포">
                  {summary.diabetes_risk ? (
                    <DiabetesRiskChart data={summary.diabetes_risk} />
                  ) : (
                    <div style={{ height: '300px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                      <p>혈당 수준 데이터가 없습니다</p>
                    </div>
                  )}
                </Card>
              </Col>
              <Col span={12}>
                <Card title="BMI 분포">
                  {summary.bmi ? (
                    <BMIDistributionChart data={summary.bmi} />
                  ) : (
                    <div style={{ height: '300px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                      <p>BMI 데이터가 없습니다</p>
                    </div>
                  )}
                </Card>
              </Col>
            </Row>
          </TabPane>
          
          <TabPane tab="상관관계 분석" key="correlation">
            <Card title="혈당치와 주요 요인 간의 상관관계">
              <CorrelationHeatmap data={correlations ? correlations.glucose_correlation : {}} />
              <Paragraph style={{ marginTop: 20 }}>
                상관계수가 양수일수록 해당 요인이 혈당치 증가와 관련이 있으며, 
                음수일수록 혈당치 감소와 관련이 있습니다. 절댓값이 클수록 관련성이 강합니다.
              </Paragraph>
            </Card>
          </TabPane>
          
          <TabPane tab="생활습관 영향" key="lifestyle">
            <Card title="생활습관이 혈당치에 미치는 영향">
              <LifestyleFactorsChart data={lifestyle_impact ? lifestyle_impact.coefficients : {}} />
              <Paragraph style={{ marginTop: 20 }}>
                {lifestyle_impact && lifestyle_impact.model_summary ? (
                  <>
                    회귀분석 결과, 모델의 설명력(R²)은 {(lifestyle_impact.model_summary.r_squared * 100).toFixed(1)}%입니다.
                    양수 계수는 해당 요인이 혈당치 증가에 기여함을, 음수 계수는 혈당치 감소에 기여함을 의미합니다.
                  </>
                ) : (
                  '분석에 필요한 충분한 데이터가 없습니다.'
                )}
              </Paragraph>
            </Card>
          </TabPane>
          
          <TabPane tab="위험도 예측" key="prediction">
            <Card title="당뇨 위험도 예측 모델">
              <RiskPredictionModel />
            </Card>
          </TabPane>
        </Tabs>
      </Content>
      <Footer style={{ textAlign: 'center', backgroundColor: '#f0f2f5', padding: '12px' }}>
        학생 건강검사 데이터 분석 대시보드 ©2025 김나현 제작
      </Footer>
    </Layout>
  );
};

export default Dashboard;