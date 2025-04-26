/**
 * 당뇨 위험도 계산 유틸리티
 * 간단한 예시 모델로, 실제 의학적 근거에 기반한 정확한 모델은 아닙니다.
 */

// BMI 계산
export const calculateBMI = (weight, height) => {
  // 키는 cm로 입력받지만 m²로 변환 필요
  const heightInMeter = height / 100;
  return weight / (heightInMeter * heightInMeter);
};

// BMI 카테고리 결정
export const getBMICategory = (bmi) => {
  if (bmi < 18.5) return '저체중';
  if (bmi < 23) return '정상';
  if (bmi < 25) return '과체중';
  return '비만';
};

// 당뇨 위험도 계산
export const calculateRisk = (userData) => {
  // 1. BMI 계산
  const bmi = calculateBMI(userData.weight, userData.height);
  const bmiCategory = getBMICategory(bmi);
  
  // 2. BMI 기반 위험도 점수 (0-100)
  let riskScore = 0;
  
  if (bmi < 18.5) riskScore += 10;
  else if (bmi < 23) riskScore += 20;
  else if (bmi < 25) riskScore += 40;
  else if (bmi < 30) riskScore += 60;
  else riskScore += 80;
  
  // 3. 허리둘레 기반 추가 점수
  // 성별에 따라 다른 기준 적용
  if (userData.gender === 'male') {
    if (userData.waist > 90) riskScore += 20;
    else if (userData.waist > 85) riskScore += 10;
  } else {
    if (userData.waist > 85) riskScore += 20;
    else if (userData.waist > 80) riskScore += 10;
  }
  
  // 4. 운동 빈도에 따른 점수 조정
  switch (userData.exercise) {
    case 'often':
      riskScore -= 15;
      break;
    case 'sometimes':
      riskScore -= 5;
      break;
    case 'rarely':
      riskScore += 10;
      break;
  }
  
  // 5. 식습관에 따른 점수 조정
  switch (userData.fastFood) {
    case 'daily':
      riskScore += 20;
      break;
    case 'often':
      riskScore += 10;
      break;
    case 'sometimes':
      riskScore += 5;
      break;
    case 'rarely':
      riskScore -= 5;
      break;
  }
  
  // 6. 점수 범위 조정 (0-100)
  riskScore = Math.max(0, Math.min(100, riskScore));
  
  // 7. 위험도 메시지 및 수준 결정
  let riskLevel;
  let riskMessage;
  
  if (riskScore < 30) {
    riskLevel = 'low';
    riskMessage = '당뇨 위험도가 낮습니다. 건강한 생활습관을 유지하세요.';
  } else if (riskScore < 60) {
    riskLevel = 'medium';
    riskMessage = '당뇨 위험도가 중간 수준입니다. 식습관과 운동에 주의가 필요합니다.';
  } else {
    riskLevel = 'high';
    riskMessage = '당뇨 위험도가 높습니다. 전문의 상담을 권장합니다.';
  }
  
  // 8. 생활습관, 신체조건 위험도 평가
  const lifestyleRisk = determineRiskLevel(
    userData.exercise === 'rarely' ? 30 : 
    userData.exercise === 'sometimes' ? 15 : 0
    +
    userData.fastFood === 'daily' ? 30 :
    userData.fastFood === 'often' ? 20 :
    userData.fastFood === 'sometimes' ? 10 : 0
  );
  
  const physicalRisk = determineRiskLevel(
    (bmi >= 25 ? 30 : bmi >= 23 ? 15 : 0)
    +
    (userData.gender === 'male' && userData.waist > 90) || 
    (userData.gender === 'female' && userData.waist > 85) ? 30 : 0
  );
  
  return {
    percentage: riskScore,
    level: riskLevel,
    message: riskMessage,
    bmi,
    bmiCategory,
    lifestyleRisk,
    physicalRisk
  };
};

// 위험 수준 결정 헬퍼 함수
function determineRiskLevel(score) {
  if (score >= 40) return '높음';
  if (score >= 20) return '중간';
  return '낮음';
}

export default {
  calculateBMI,
  getBMICategory,
  calculateRisk
};