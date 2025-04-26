import React from 'react';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';

const LifestyleFactorsChart = ({ data }) => {
  // 오류 처리
  if (!data || data.error) {
    return (
      <div style={{ height: '300px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <p>{data?.error || '생활습관 요인 분석에 필요한 충분한 데이터가 없습니다'}</p>
      </div>
    );
  }

  // 상수(intercept) 제외, 계수 기준으로 정렬
  const factors = Object.keys(data)
    .filter(key => key !== 'const') // 상수항 제외
    .sort((a, b) => Math.abs(data[b].coefficient) - Math.abs(data[a].coefficient));
  
  const coefficients = factors.map(factor => data[factor].coefficient);
  
  // 색상 설정 (양수는 빨강, 음수는 파랑, 유의미한 것은 진하게)
  const backgroundColors = factors.map(factor => {
    const coef = data[factor].coefficient;
    const isSignificant = data[factor].significant;
    
    if (coef > 0) {
      return isSignificant ? 'rgba(245, 34, 45, 0.9)' : 'rgba(245, 34, 45, 0.4)';
    } else {
      return isSignificant ? 'rgba(24, 144, 255, 0.9)' : 'rgba(24, 144, 255, 0.4)';
    }
  });

  // 라벨 간소화
  const simplifiedLabels = factors.map(factor => {
    return factor
      .replace('주3회이상', '주3회+')
      .replace('하루30분이상', '30분+')
      .replace('2시간이상', '2시간+')
      .replace('_cm', '')
      .replace('_kg', '');
  });

  const chartData = {
    labels: simplifiedLabels,
    datasets: [
      {
        label: '혈당치에 대한 영향력',
        data: coefficients,
        backgroundColor: backgroundColors,
        borderColor: 'rgba(0, 0, 0, 0.1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',  // 수평 바 차트
    scales: {
      x: {
        title: {
          display: true,
          text: '회귀 계수 (양수: 혈당 증가, 음수: 혈당 감소)'
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
            const factorName = factors[context.dataIndex];
            const value = data[factorName].coefficient.toFixed(3);
            const pValue = data[factorName].p_value.toFixed(3);
            const significant = data[factorName].significant;
            
            let effect = value > 0 ? '증가' : '감소';
            
            return [
              `계수: ${value}`,
              `p-value: ${pValue}`,
              `통계적 유의성: ${significant ? '있음' : '없음'}`,
              `혈당을 ${effect}시키는 경향이 있음`
            ];
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

export default LifestyleFactorsChart;