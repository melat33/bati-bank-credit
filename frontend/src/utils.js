// 1. Convert score to risk label
export const getRiskLabel = (score) => {
  if (score >= 0.7) {
    return "High";
  } else if (score >= 0.4) {
    return "Medium";
  } else {
    return "Low";
  }
};

// 2. Convert score to color
export const getRiskColor = (score) => {
  if (score >= 0.7) {
    return "red";
  } else if (score >= 0.4) {
    return "orange";
  } else {
    return "green";
  }
};

// 3. Format Ethiopian Birr currency
export const formatCurrency = (amount) => {
  return `ETB ${amount.toLocaleString()}`;
};