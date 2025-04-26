import React from 'react';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';

const BMIDistributionChart = ({ data }) => {
  const chartData = {
    labels: ['저체중', '정상', '과체중', '비만'],
    datasets: [
      {
        label: '학생 수',
        data: [data.underweight, data.normal, data.overweight, data.obese],
        backgroundColor: ['#1890ff', '#52c41a', '#faad14', '#f5222d'],
        borderColor: ['#096dd9', '#389e0d', '#d48806', '#cf1322'],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: '학생 수'
        }
      },
      x: {
        title: {
          display: true,
          text: 'BMI 분류'
        }
      }
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.dataset.label || '';
            const value = context.raw || 0;
            const total = data.underweight + data.normal + data.overweight + data.obese;
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value}명 (${percentage}%)`;
          }
        }
      }
    }
  };

  return (
    <div style={{ height: '300px' }}>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default BMIDistributionChart;