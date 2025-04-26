import React, { useState } from 'react';
import { Form, InputNumber, Select, Button, Card, Result, Row, Col } from 'antd';
import { calculateRisk } from '../services/risk';

const { Option } = Select;

const RiskPredictionModel = () => {
  const [form] = Form.useForm();
  const [riskResult, setRiskResult] = useState(null);
  
  const onFinish = (values) => {
    // 간단한 위험도 예측 모델 (실제로는 서비스에서 더 복잡한 계산 수행)
    const risk = calculateRisk(values);
    setRiskResult(risk);
  };
  
  const resetForm = () => {
    form.resetFields();
    setRiskResult(null);
  };
  
  return (
    <div>
      {!riskResult ? (
        <Form
          form={form}
          name="riskPrediction"
          onFinish={onFinish}
          layout="vertical"
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="age"
                label="나이"
                rules={[{ required: true, message: '나이를 입력하세요' }]}
              >
                <InputNumber min={6} max={19} style={{ width: '100%' }} placeholder="나이 (세)" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="gender"
                label="성별"
                rules={[{ required: true, message: '성별을 선택하세요' }]}
              >
                <Select placeholder="성별 선택">
                  <Option value="male">남성</Option>
                  <Option value="female">여성</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="height"
                label="키"
                rules={[{ required: true, message: '키를 입력하세요' }]}
              >
                <InputNumber min={100} max={200} style={{ width: '100%' }} placeholder="키 (cm)" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="weight"
                label="몸무게"
                rules={[{ required: true, message: '몸무게를 입력하세요' }]}
              >
                <InputNumber min={20} max={150} style={{ width: '100%' }} placeholder="몸무게 (kg)" />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="waist"
                label="허리둘레"
                rules={[{ required: true, message: '허리둘레를 입력하세요' }]}
              >
                <InputNumber min={40} max={150} style={{ width: '100%' }} placeholder="허리둘레 (cm)" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="exercise"
                label="운동 빈도"
                rules={[{ required: true, message: '운동 빈도를 선택하세요' }]}
              >
                <Select placeholder="운동 빈도 선택">
                  <Option value="rarely">거의 안함</Option>
                  <Option value="sometimes">가끔 (주 1-2회)</Option>
                  <Option value="often">자주 (주 3회 이상)</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item
                name="fastFood"
                label="패스트푸드 섭취 빈도"
                rules={[{ required: true, message: '패스트푸드 섭취 빈도를 선택하세요' }]}
              >
                <Select placeholder="패스트푸드 섭취 빈도 선택">
                  <Option value="rarely">거의 안함</Option>
                  <Option value="sometimes">가끔 (주 1-2회)</Option>
                  <Option value="often">자주 (주 3회 이상)</Option>
                  <Option value="daily">매일</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              당뇨 위험도 계산하기
            </Button>
          </Form.Item>
        </Form>
      ) : (
        <Result
          status={riskResult.level === 'high' ? 'warning' : 'success'}
          title={`당뇨 위험도: ${riskResult.percentage}%`}
          subTitle={riskResult.message}
          extra={[
            <Button type="primary" key="back" onClick={resetForm}>
              다시 계산하기
            </Button>
          ]}
        >
          <div className="desc">
            <Card size="small" title="위험 요인 분석">
              <p>
                <strong>BMI:</strong> {riskResult.bmi.toFixed(1)} ({riskResult.bmiCategory})
              </p>
              <p>
                <strong>생활습관 위험도:</strong> {riskResult.lifestyleRisk}
              </p>
              <p>
                <strong>신체조건 위험도:</strong> {riskResult.physicalRisk}
              </p>
            </Card>
          </div>
        </Result>
      )}
    </div>
  );
};

export default RiskPredictionModel;