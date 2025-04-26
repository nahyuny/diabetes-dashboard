import React from 'react';
import { Pie } from 'react-chartjs-2';
import 'chart.js/auto';

const DiabetesRiskChart = ({ data }) => {
  const chartData = {
    labels: ['정상', '전당뇨', '당뇨의심'],
    datasets: [
      {
        data: [data.normal, data.prediabetes, data.diabetes],
        backgroundColor: ['#52c41a', '#faad14', '#f5222d'],
        hoverBackgroundColor: ['#389e0d', '#d48806', '#cf1322'],
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.raw || 0;
            const total = context.dataset.data.reduce((acc, curr) => acc + curr, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value}명 (${percentage}%)`;
          }
        }
      }
    }
  };

  return (
    <div style={{ height: '300px' }}>
      <Pie data={chartData} options={options} />
    </div>
  );
};

export default DiabetesRiskChart;