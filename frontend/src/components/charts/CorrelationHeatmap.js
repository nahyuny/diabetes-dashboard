import React from 'react';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';

const CorrelationHeatmap = ({ data }) => {
  // 상관계수가 없는 경우 처리
  if (!data || Object.keys(data).length === 0) {
    return (
      <div style={{ height: '300px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <p>분석에 필요한 충분한 데이터가 없습니다</p>
      </div>
    );
  }

  // 혈당치와의 상관관계만 표시 (자기 자신 제외)
  const labels = Object.keys(data).filter(key => key !== '혈당치_mgdL');
  const correlationValues = labels.map(key => data[key]);

  // 색상 설정 (음수는 파랑, 양수는 빨강)
  const backgroundColors = correlationValues.map(value => 
    value < 0 ? `rgba(24, 144, 255, ${Math.abs(value)})` : `rgba(245, 34, 45, ${Math.abs(value)})`
  );

  const chartData = {
    labels: labels.map(label => {
      // 라벨 간소화
      return label
        .replace('_mgdL', '')
        .replace('_cm', '')
        .replace('_kg', '');
    }),
    datasets: [
      {
        label: '혈당치와의 상관계수',
        data: correlationValues,
        backgroundColor: backgroundColors,
        borderColor: 'rgba(0, 0, 0, 0.1)',
        borderWidth: 1,
        barPercentage: 0.6
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',  // 수평 바 차트
    scales: {
      x: {
        min: -1,
        max: 1,
        title: {
          display: true,
          text: '상관계수 (-1 ~ 1)'
        }
      }
    },
    plugins: {
      tooltip: {
        callbacks: {
          title: (tooltipItems) => {
            return tooltipItems[0].label;
          },
          label: (context) => {
            const value = context.raw.toFixed(3);
            let direction = value > 0 ? '양의' : '음의';
            let strength = Math.abs(value);
            
            let description = '';
            if (strength > 0.7) description = '강한';
            else if (strength > 0.3) description = '중간';
            else description = '약한';
            
            return [`상관계수: ${value}`, `${direction} ${description} 상관관계`];
          }
        }
      }
    }
  };

  return (
    <div style={{ height: '400px' }}>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default CorrelationHeatmap;